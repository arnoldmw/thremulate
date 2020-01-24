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
    return {'title': 'Login'}


async def login_post(request):
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

            if user.reset_pass:
                raise web.HTTPFound('/force_reset_password')

            session.__setitem__('username', user.fname)

            raise web.HTTPFound('/home')

        context = {'error': '*Incorrect login'}
        response = aiohttp_jinja2.render_template('auth/login.html',
                                                  request,
                                                  context)
        return response

    return web.Response(status=400)


@aiohttp_jinja2.template('auth/force_reset_password.html')
async def force_reset_password(request):
    user_id = await check_authorized(request)
    session = await get_session(request)
    session.invalidate()
    return {'user_id': user_id}


async def force_reset_password_post(request):
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
    # print('register')
    # for key in data.keys():
    #     print(key + ': ' + data[key])

    if 'confirm_password' and 'password' and 'user_id' in data:
        if data['confirm_password'] == data['password']:
            User.update(passwd=generate_password_hash(data['password']), reset_pass=True).\
                where(User.id == data['user_id']).execute()
            # print('updated')

    # TODO: Not all are to be redirected to user index
    raise web.HTTPFound('/users')


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
        web.post('/force_reset_password_post', force_reset_password_post, name='force_reset_password_post')
    ])
