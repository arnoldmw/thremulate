from aiohttp import web
from database import *
import aiohttp_jinja2
from peewee import IntegrityError

from db_auth import generate_password_hash


@aiohttp_jinja2.template('login.html')
async def login(request):
    return {'title': 'Login'}


@aiohttp_jinja2.template('login.html')
async def login_post(request):
    return {}


@aiohttp_jinja2.template('register.html')
async def register(request):
    # token = await aiohttp_csrf.generate_token(request)
    # csrf = {'field_name': FORM_FIELD_NAME, 'token': token}
    return {'title': 'Register'}


async def register_post(request):
    data = await request.post()
    # print('register')
    # for key in data.keys():
    #     print(key + ': ' + data[key])

    try:
        user = User.create(fname=data['firstname'], lname=data['lastname'], email=data['email'],
                           passwd=generate_password_hash(data['password']),
                           is_superuser=0, disabled=0)
        UserPermissions.create(user_id=user.id, perm_id=Permissions.get(Permissions.name == 'public'))

    except IntegrityError as error:
        print(error.__context__)
        # peewee.IntegrityError: UNIQUE constraint failed: user.email

    raise web.HTTPFound('/users')