# noinspection
from auth import *
from campaign import *
from dashboard import *
from agent import *


import logging
import ssl

from aiohttp import web
import jinja2
from pathlib import Path
import aiohttp_jinja2

# noinspection PyUnresolvedReferences
from middleware import setup_middleware

from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

# noinspection PyUnresolvedReferences
from database import *

THIS_DIR = Path(__file__).parent

FORM_FIELD_NAME = '_csrf_token'
SESSION_NAME = 'csrf_token'


@aiohttp_jinja2.template('base.html')
async def index(request):
    return {
        'title': "Test",
        'intro': "Success! you've setup a basic aiohttp app.",
    }


@aiohttp_jinja2.template('users_index.html')
async def users_index(request):
    users = User.select()
    perms = []
    users_list = []
    user = {}
    for m in users:
        user.__setitem__('id', m.id)
        user.__setitem__('fname', m.fname)
        user.__setitem__('lname', m.lname)
        user.__setitem__('email', m.email)
        user.__setitem__('disabled', m.disabled)
        user.__setitem__('superuser', m.is_superuser)

        # for n in m.userpermissions:
        #     perms.append(n.perm_name)
        #
        # user.__setitem__('perms', perms)

        users_list.append(user)
        user = {}
        # perms = []
    return {'users': users_list, 'title': 'Users'}


async def user_delete(request):
    user_id = request.match_info['id']

    q = User.delete().where(User.id == user_id)
    q.execute()
    raise web.HTTPFound('/users')


@aiohttp_jinja2.template('user_edit.html')
async def user_edit(request):
    user_id = request.match_info['id']
    user = User.get(User.id == user_id)
    perms = [{'perm_id': '', 'perm_name': ''}, {'perm_id': '', 'perm_name': ''}]
    user_selected = {}

    user_selected.__setitem__('id', user.id)
    user_selected.__setitem__('fname', user.fname)
    user_selected.__setitem__('lname', user.lname)
    user_selected.__setitem__('email', user.email)
    user_selected.__setitem__('disabled', user.disabled)
    user_selected.__setitem__('superuser', user.is_superuser)

    i = 0
    if user.userpermissions.count() > 0:
        for p in user.userpermissions:
            # perms.append()
            if i == 3:
                break
            perms.__setitem__(i, {'perm_id': p.perm_id.id, 'perm_name': p.perm_id.name})
            # perms.append({'perm_id': p.perm_id.id, 'perm_name': p.perm_id.name})
            i = i + 1

    user_selected.__setitem__('user_perms', perms)

    permissions = Permissions.select()
    perm_list = []
    for pm in permissions:
        perm_list.append({'id': pm.id, 'name': pm.name})

    # print(user_selected)
    # print(perm_list)
    return {'user': user_selected, 'perm_list': perm_list, 'title': 'User Edit'}


async def user_edit_post(request):
    data = await request.post()
    # print('register')
    # for key in data.keys():
    #     print(key + ': ' + data[key])

    permissions = []

    if 'user_id' and 'fname' and 'lname' and 'email' and 'disabled' and 'superuser' in data:

        user_id = data['user_id']

        if 'public' in data:
            permissions.append({'user_id': user_id, 'perm_id': data['public']})
        if 'protected' in data:
            permissions.append({'user_id': user_id, 'perm_id': data['protected']})

        if permissions.__len__() > 0:
            UserPermissions.delete().where(UserPermissions.user_id == user_id).execute()

        if data['disabled'] == 'False':
            disabled = False
        else:
            disabled = True

        if data['superuser'] == 'False':
            superuser = False
        else:
            superuser = True

        UserPermissions.insert_many(permissions).execute()
        User.update(fname=data['fname'], lname=data['lname'], email=data['email'], is_superuser=superuser,
                    disabled=disabled).where(User.id == user_id).execute()

        raise web.HTTPFound('/users')

    else:

        permissions = Permissions.select()
        perm_list = []
        for pm in permissions:
            perm_list.append({'id': pm.id, 'name': pm.name})

        response = aiohttp_jinja2.render_template('user_edit.html', request, {'user': data, 'perm_list': perm_list})
        # response.headers['Content-Language'] = 'en'
        return response


async def create_app():
    app = web.Application()
    app.add_routes([
        web.get('/', index),
        web.get('/users', users_index, name='users'),
        web.get('/user_delete/{id}', user_delete, name='user_delete'),
        web.get('/user_edit/{id}', user_edit, name='user_edit'),
        web.post('/user_edit_post', user_edit_post, name='user_edit_post'),

        web.static('/static/', path=THIS_DIR / 'app/static', show_index=True, append_version=True, name='static'),
        web.static('/downloads/', path=THIS_DIR / 'app/downloads', show_index=True, name='downloads'),
        web.static('/uploads/', path=THIS_DIR / 'app/uploads', show_index=True, name='uploads')
    ])

    # Routes
    setup_auth_routes(app)
    setup_campaign_routes(app)
    setup_dashboard_routes(app)
    setup_agent_routes(app)

    load = jinja2.FileSystemLoader(str(THIS_DIR / 'app/templates'))
    aiohttp_jinja2.setup(app, loader=load)
    app['name'] = 'S.T.A.E'

    setup_middleware(app)

    # CSRF CODE 1
    # csrf_policy = aiohttp_csrf.policy.FormPolicy(FORM_FIELD_NAME)
    # csrf_storage = aiohttp_csrf.storage.SessionStorage(SESSION_NAME)
    # aiohttp_csrf.setup(app, policy=csrf_policy, storage=csrf_storage)

    secret_key = b'\xd0\x04)E\x14\x98\xa1~\xecE\xae>(\x1d6\xec\xbfQ\xa4\x19\x0e\xbcre,\xf8\x8f\x84WV.\x8d'
    setup(app, EncryptedCookieStorage(secret_key))

    # CSRF CODE 2
    # app.middlewares.append(aiohttp_csrf.csrf_middleware)

    # HTTPS using Secure Sockets Layer
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile='certificates/stae.crt', keyfile='certificates/stae.key')

    # Stops asyncio warnings because asycio implements its own exception handling. This throws many exceptions
    # that cannot be handled due to this being a development environment.
    logging.getLogger('asyncio').setLevel(logging.CRITICAL)

    # logging.basicConfig(level=logging.INFO)

    # web.run_app(app, host="localhost", port=8080, ssl_context=ssl_context)

    return app

# adev runserver --livereload --debug-toolbar
# app = create_app()
# web.run_app(app, host="localhost", port=8000)
