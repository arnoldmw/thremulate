# noinspection PyUnresolvedReferences
from handlers.auth import *
# noinspection PyUnresolvedReferences
from handlers.campaign import *
# noinspection PyUnresolvedReferences
from handlers.dashboard import *
# noinspection PyUnresolvedReferences
from handlers.agent import *
# noinspection PyUnresolvedReferences
from handlers.user_mgt import *
# noinspection PyUnresolvedReferences
from handlers.middleware import setup_middleware

import logging
import ssl

from aiohttp import web
import jinja2
from pathlib import Path
import aiohttp_jinja2


from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

# noinspection PyUnresolvedReferences
from database import *

THIS_DIR = Path(__file__).parent


@aiohttp_jinja2.template('base.html')
async def index(request):
    return {'title': "Home"}


async def create_app():
    app = web.Application()
    app.add_routes([
        web.get('/', index),
        web.static('/static/', path=THIS_DIR / 'app/static', show_index=True, append_version=True, name='static'),
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

    secret_key = b'\xd0\x04)E\x14\x98\xa1~\xecE\xae>(\x1d6\xec\xbfQ\xa4\x19\x0e\xbcre,\xf8\x8f\x84WV.\x8d'
    setup(app, EncryptedCookieStorage(secret_key))

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
