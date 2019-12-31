from aiohttp import web
from database import *
import aiohttp_jinja2
from peewee import IntegrityError

# noinspection PyUnresolvedReferences
from db_auth import generate_password_hash


@aiohttp_jinja2.template('auth/login.html')
async def login(request):
    return {'title': 'Login'}


async def login_post(request):
    return {}


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
        print(error.__context__)
        # peewee.IntegrityError: UNIQUE constraint failed: user.email

    raise web.HTTPFound('/users')


def setup_auth_routes(app):
    app.add_routes([
        web.get('/login', login, name='login'),
        web.post('/login_post', login_post),
        web.get('/register', register, name='register'),
        web.post('/register_post', register_post, name='register_post'),
        ])
