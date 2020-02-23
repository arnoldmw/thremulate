import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import (
    remember, forget, authorized_userid,
    check_permission, check_authorized,
)
from aiohttp_session import new_session, get_session

from stae.db_auth import *


@aiohttp_jinja2.template('auth/login.html')
async def login(request):
    """
    Retrieves the login template for authentication.
    :param request:
    :return: home of the user if successful otherwise the same template with the error message.
    """
    user_id = await authorized_userid(request)
    if user_id is None:
        return {'title': 'Login'}

    raise web.HTTPFound('/home')


async def login_post(request):
    """
    Checks if the credentials are valid or if the account is locked out. Increases the account lockout count for
    every failed authentication attempt. Checks if the user must reset their password after it is reset by a superuser.
    :param request:
    :return: home of the user if successful otherwise an exception is raised or error message on the login page.
    """
    data = await request.post()
    try:
        email = data['email']
        password = data['password']

        try:
            user = User.get(User.email == email)
            if user.lockout_count >= 10:
                context = {'error': '*Account locked. Contact Administrator.'}
                response = aiohttp_jinja2.render_template('auth/login.html',
                                                          request,
                                                          context)
                return response
        except User.DoesNotExist:
            context = {'error': '*Incorrect login'}
            response = aiohttp_jinja2.render_template('auth/login.html',
                                                      request,
                                                      context)
            return response

        result = check_credentials(email, password)
        if result:
            session = await new_session(request)

            response = web.HTTPFound('/home')
            await remember(request, response, str(user.id))

            # Password must be reset when a super user resets it for better audit trails.
            if user.reset_pass:
                raise web.HTTPFound('/force_reset_password')

            session.__setitem__('current_user', {'fname': user.fname, 'is_su': user.is_superuser})

            raise web.HTTPFound('/home')

        user.lockout_count = user.lockout_count + 1
        user.save()
        context = {'error': '*Incorrect login'}
        response = aiohttp_jinja2.render_template('auth/login.html',
                                                  request,
                                                  context)
        return response
    except KeyError:
        return web.Response(status=400)


@aiohttp_jinja2.template('auth/force_reset_password.html')
async def force_reset_password(request):
    """
    Retrieves the template for resetting the password after a superuser reset it for another user.
    :param request:
    :return: Template with password reset form otherwise an exception is raised.
    """
    user_id = await check_authorized(request)
    session = await get_session(request)
    session.invalidate()
    return {'user_id': user_id}


async def force_reset_password_post(request):
    """
    Updates the user password after it was reset by a superuser and sets the user reset_pass to False.
    :param request:
    :return: home of the user if successful otherwise an exception is raised or error message on the
    force_reset_password template.
    """
    data = await request.post()
    try:
        user_id = data['user_id']
        if data['new_password'] == data['confirm_new_password']:

            try:

                user = User.get(User.id == user_id)

                check_password_hash(data['current_password'], user.passwd)

                user.passwd = generate_password_hash(data['new_password'])
                user.reset_pass = False
                user.save()

                session = await new_session(request)
                session.__setitem__('username', user.fname)

                response = web.HTTPFound('/home')
                await remember(request, response, user_id)
                raise response

            except User.DoesNotExist:
                return web.Response(status=400)
        else:
            context = {'user_id': '*Incorrect credentials'}
            response = aiohttp_jinja2.render_template('auth/force_reset_password.html',
                                                      request,
                                                      context)
            return response

    except KeyError:
        return web.Response(status=400)


async def logout(request):
    """
    Logs outs the user amd deletes the session created for the user.
    :param request:
    :return: '/' if successful ootherwise an exception is raised.
    """
    await check_authorized(request)
    response = web.HTTPFound('/')
    await forget(request, response)
    session = await get_session(request)
    session.invalidate()
    raise response


@aiohttp_jinja2.template('auth/register.html')
async def register(request):
    """
    Retrieves template for registering user.
    :param request:
    :return: Template with register user form if successful otherwise an exception is raised.
    """
    await check_permission(request, 'protected')
    return {'title': 'Register'}


async def register_post(request):
    """
    Registers a user after the register user form is submitted
    :param request:
    :return: '/users' if successful otherwise an exception is raised.
    """
    await check_permission(request, 'protected')
    data = await request.post()

    try:
        passwd = data['password']
        conf_passwd = data['confirm_password']

        if passwd == conf_passwd:
            user = User.create(fname=data['firstname'], lname=data['lastname'], email=data['email'],
                               passwd=generate_password_hash(passwd),
                               is_superuser=False, disabled=False)
            UserPermissions.create(user_id=user.id, perm_id=Permissions.get(Permissions.name == 'public'))
            raise web.HTTPFound('/users')
        else:
            # TODO:  Return passwords do not match message to user
            print('passwords do not match')

    except KeyError:
        return web.Response(status=400)
    except IntegrityError as error:
        # TODO: Return error message to user
        if 'id' in error.__context__.__str__():
            print('id constraint failed')
        if 'email' in error.__context__.__str__():
            print('email constraint failed')


@aiohttp_jinja2.template('auth/reset_password.html')
async def reset_password(request):
    """
    Retrieves the template with reset password form.
    :param request:
    :return: Template with reset password form otherwise an exception is raised.
    """
    await check_permission(request, 'protected')

    try:
        user_id = request.match_info['id']
        session = await get_session(request)
        current_user = session['current_user']
        return {'current_user': current_user, 'user_id': user_id, 'title': 'Reset Password'}
    except KeyError:
        return web.Response(status=400)


async def reset_password_post(request):
    """
    Resets a user password through the superuser or administrator account.
    :param request:
    :return: '/users' if successful otherwise an exception is raised.
    """
    await check_permission(request, 'protected')
    data = await request.post()

    try:
        if data['confirm_password'] == data['password']:
            admin_id = await authorized_userid(request)
            try:
                admin_pass = User.get(User.id == admin_id).passwd

                if check_password_hash(data['admin_password'], admin_pass):
                    User.update(passwd=generate_password_hash(data['password']), reset_pass=True). \
                        where(User.id == data['user_id']).execute()

                    raise web.HTTPFound('/users')
            except User.DoesNotExist:
                return web.Response(status=400)

    except KeyError:
        return web.Response(status=400)


async def reset_lockout_post(request):
    """
    Resets the account lockout count to zero (0).
    :param request:
    :return: 'success' if successful otherwise an exception is raised.
    """
    await check_permission(request, 'protected')
    data = await request.post()

    try:
        User.update(lockout_count=0).where(User.id == data['user_id']).execute()
        return web.Response(text='success')
    except KeyError:
        return web.Response(status=400)


def setup_auth_routes(app):
    """
    Adds auth routes to the application.
    :param app:
    :return:
    """
    app.add_routes([
        web.get('/login', login, name='login'),
        web.post('/login_post', login_post, name='login_post'),
        web.get('/logout', logout, name='logout'),
        web.get('/register', register, name='register'),
        web.post('/register_post', register_post, name='register_post'),
        web.get('/reset_password/{id}', reset_password, name='reset_password'),
        web.post('/reset_password_post', reset_password_post, name='reset_password_post'),
        web.get('/force_reset_password', force_reset_password, name='force_reset_password'),
        web.post('/force_reset_password_post', force_reset_password_post, name='force_reset_password_post'),
        web.post('/reset_lockout_post', reset_lockout_post, name='reset_lockout_post')
    ])
