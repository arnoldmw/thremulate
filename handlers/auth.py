from aiohttp import web
from aiohttp_session import new_session, get_session
from database import *
import aiohttp_jinja2
from peewee import IntegrityError
from db_auth import *
from aiohttp_security import (
    remember, forget, authorized_userid,
    check_permission, check_authorized,
)


@aiohttp_jinja2.template('auth/login.html')
async def login(request):
    """
    Retrieves the login template for authentication.
    :param request:
    :return: home of the user if successful otherwise the same template with the error message.
    """
    return {'title': 'Login'}


async def login_post(request):
    """
    Checks if the credentials are valid or if the account is locked out. Increases the account lockout count for
    every failed authentication attempt. Checks if the user must reset their password after it is reset by a superuser.
    :param request:
    :return: home of the user if successful otherwise an exception or error message on the login page.
    """
    data = await request.post()
    if 'email' in data and 'password' in data:
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

            session.__setitem__('username', user.fname)

            raise web.HTTPFound('/home')

        user.lockout_count = user.lockout_count + 1
        user.save()
        context = {'error': '*Incorrect login'}
        response = aiohttp_jinja2.render_template('auth/login.html',
                                                  request,
                                                  context)
        return response

    return web.Response(status=400)


@aiohttp_jinja2.template('auth/force_reset_password.html')
async def force_reset_password(request):
    """
    Retrieves the template for resetting the password after a superuser reset it for another user.
    :param request:
    :return: Template with password reset form.
    """
    user_id = await check_authorized(request)
    session = await get_session(request)
    session.invalidate()
    return {'user_id': user_id}


async def force_reset_password_post(request):
    """
    Updates the user password after it was reset by a superuser and sets the user reset_pass to False.
    :param request:
    :return: home of the user if successful otherwise an exception or error message on the force_reset_password
            template.
    """
    data = await request.post()
    if 'user_id' in data and 'current_password' in data and 'new_password' in data and 'confirm_new_password' in data:
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

    return web.Response(status=400)


async def logout(request):
    await check_authorized(request)
    response = web.HTTPFound('/')
    await forget(request, response)
    session = await get_session(request)
    session.invalidate()
    raise response


@aiohttp_jinja2.template('auth/register.html')
async def register(request):
    await check_permission(request, 'protected')
    return {'title': 'Register'}


async def register_post(request):
    await check_permission(request, 'protected')
    data = await request.post()

    try:
        user = User.create(fname=data['firstname'], lname=data['lastname'], email=data['email'],
                           passwd=generate_password_hash(data['password']),
                           is_superuser=0, disabled=0)
        UserPermissions.create(user_id=user.id, perm_id=Permissions.get(Permissions.name == 'public'))

    except IntegrityError as error:
        if 'id' in error.__context__.__str__():
            print('id constraint failed')
        if 'email' in error.__context__.__str__():
            print('email constraint failed')

    # TODO: Return error message to user
    raise web.HTTPFound('/users')


@aiohttp_jinja2.template('auth/reset_password.html')
async def reset_password(request):
    await check_permission(request, 'protected')
    user_id = request.match_info['id']
    session = await get_session(request)
    username = session['username']
    return {'username': username, 'user_id': user_id, 'title': 'Reset Password'}


async def reset_password_post(request):
    await check_permission(request, 'protected')
    data = await request.post()

    if 'confirm_password' in data and 'password' in data and 'user_id' in data and 'admin_password' in data:
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

    return web.Response(status=400)


async def reset_lockout_post(request):
    await check_permission(request, 'protected')
    data = await request.post()

    if 'user_id' in data:
        User.update(lockout_count=0).where(User.id == data['user_id']).execute()
        return web.Response(text='success')
    return web.Response(status=400)


def setup_auth_routes(app):
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
