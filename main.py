# noinspection PyUnresolvedReferences
import logging
import ssl
from pathlib import Path

import aiohttp_debugtoolbar
import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_security import SessionIdentityPolicy
from aiohttp_security import (
    check_authorized,
)
from aiohttp_security import setup as setup_security
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
# noinspection PyUnresolvedReferences
from database import *
# noinspection PyUnresolvedReferences
from db_auth import DBAuthorizationPolicy
# noinspection PyUnresolvedReferences
from handlers.agent import *
# noinspection PyUnresolvedReferences
from handlers.auth import *
# noinspection PyUnresolvedReferences
from handlers.adversary import *
# noinspection PyUnresolvedReferences
from handlers.dashboard import *
# noinspection PyUnresolvedReferences
from handlers.logger import *
# noinspection PyUnresolvedReferences
from handlers.middleware import setup_middleware
# noinspection PyUnresolvedReferences
from handlers.user_mgt import *

THIS_DIR = Path(__file__).parent
secret_key = b'\xd0\x04)E\x14\x98\xa1~\xecE\xae>(\x1d6\xec\xbfQ\xa4\x19\x0e\xbcre,\xf8\x8f\x84WV.\x8d'


# noinspection PyUnusedLocal
@aiohttp_jinja2.template('index.html')
async def index(request):
    return {}


@aiohttp_jinja2.template('home.html')
async def home(request):
    await check_authorized(request)
    session = await get_session(request)
    # username = session['username']
    current_user = session['current_user']
    return {'current_user': current_user, 'title': "Home"}


async def create_app():
    app = web.Application()
    app.add_routes([
        web.get('/', index, name='index'),
        web.get('/home', home, name='home'),
        web.static('/static/', path=THIS_DIR / 'app/static', append_version=True, name='static'),
        web.static('/downloads/', path=THIS_DIR / 'app/downloads', show_index=True, name='downloads'),
        web.static('/uploads/', path=THIS_DIR / 'app/uploads', show_index=True, name='uploads')
    ])

    # Routes
    setup_auth_routes(app)
    setup_campaign_routes(app)
    setup_dashboard_routes(app)
    setup_agent_routes(app)
    setup_user_mgt_routes(app)
    setup_middleware(app)

    load = jinja2.FileSystemLoader(str(THIS_DIR / 'app/templates'))
    aiohttp_jinja2.setup(app, loader=load)
    app['name'] = 'thremulate'

    setup(app, EncryptedCookieStorage(secret_key))

    # Setting authentication and authorization
    setup_security(app, SessionIdentityPolicy(), DBAuthorizationPolicy())

    # HTTPS using Secure Sockets Layer
    # ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # ssl_context.load_cert_chain(certfile='certificates/thremulate.crt', keyfile='certificates/thremulate.key')

    aiohttp_debugtoolbar.setup(app, intercept_redirects=False)
    # web.run_app(app, host="localhost", port=8080, ssl_context=ssl_context)

    return app

# adev runserver --livereload --debug-toolbar
if __name__ == '__main__':
    application = create_app()
    logging.basicConfig(level=logging.INFO, filename=THIS_DIR / 'logs/thremulate.log')
    web.run_app(application, host="0.0.0.0", port=8000, access_log_class=AccessLogger)
