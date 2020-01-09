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
    email = data['email']
    password = data['password']

    result = check_credentials(email, password)
    if result:
        response = web.HTTPFound('/home')
        await remember(request, response, email)
        session = await new_session(request)
        # session.new = True

        username = User.get(User.email == email).fname
        session['username'] = username
        raise response

    context = {'error': '*Incorrect login'}
    response = aiohttp_jinja2.render_template('auth/login.html',
                                              request,
                                              context)
    return response


async def logout(request):
    await check_authorized(request)
    response = web.HTTPFound('/')
    await forget(request, response)
    return response


@aiohttp_jinja2.template('auth/register.html')
async def register(request):
    return {'title': 'Register'}


async def register_post(request):
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
    user_id = request.match_info['id']
    session = await get_session(request)
    username = session['username']
    return {'username': username, 'user_id': user_id, 'title': 'Reset Password'}


async def reset_password_post(request):
    data = await request.post()
    # print('register')
    # for key in data.keys():
    #     print(key + ': ' + data[key])

    if 'confirm_password' and 'password' and 'user_id' in data:
        if data['confirm_password'] == data['password']:
            User.update(passwd=generate_password_hash(data['password'])).where(User.id == data['user_id']).execute()
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
    ])
