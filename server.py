import asyncio
# import aiohttp_debugtoolbar
import logging
import ssl
from pathlib import Path
import os
import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_security import SessionIdentityPolicy
from aiohttp_security import check_authorized
from aiohttp_security import setup as setup_security
from aiohttp_session import setup, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
# noinspection PyUnresolvedReferences
from db.database import *
# noinspection PyUnresolvedReferences
from db.db_auth import DBAuthorizationPolicy
# noinspection PyUnresolvedReferences
from modules.agent import *
# noinspection PyUnresolvedReferences
from modules.auth import *
# noinspection PyUnresolvedReferences
from modules.adversary import *
# noinspection PyUnresolvedReferences
from modules.dashboard import *
# noinspection PyUnresolvedReferences
from modules.middleware import setup_middleware
# noinspection PyUnresolvedReferences
from modules.user_mgt import *
# noinspection PyUnresolvedReferences
from config.settings import config as server

THIS_DIR = Path(__file__).parent
secret_key = b'\xd0\x04)E\x14\x98\xa1~\xecE\xae>(\x1d6\xec\xbfQ\xa4\x19\x0e\xbcre,\xf8\x8f\x84WV.\x8d'
runners = []


# noinspection PyUnusedLocal
@aiohttp_jinja2.template('index.html')
async def index(request):
    return {}


async def index_app_two(request):
    return web.Response(text='AGENT SERVER')


@aiohttp_jinja2.template('home.html')
async def home(request):
    await check_authorized(request)
    session = await get_session(request)
    current_user = session['current_user']
    return {'current_user': current_user, 'title': 'Home'}


def setup_logging():
    if not os.path.exists(path=THIS_DIR / 'logs'):
        os.makedirs('logs')

    # Stops asyncio warnings because asycio implements its own exception handling. This throws many exceptions
    # that cannot be handled due to this being a development environment.
    logging.getLogger('asyncio').setLevel(logging.CRITICAL)

    logging.getLogger('aiohttp.access').setLevel(logging.INFO)
    logging.getLogger('peewee').setLevel(logging.CRITICAL)
    logging.basicConfig(level=logging.INFO, filename=THIS_DIR / 'logs/thremulate.log')


def setup_db():
    if not os.path.exists(path=THIS_DIR / 'db'):
        os.makedirs(THIS_DIR / 'db')
    if not os.path.exists(path=THIS_DIR / 'db/adversary.db'):
        init_db()


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
    # aiohttp_debugtoolbar.setup(app)
    return app


async def create_app_two():
    app = web.Application()
    app.add_routes([
        web.get('/', index_app_two),
        web.static('/get_agent/', path=THIS_DIR / 'agents', show_index=True),
        web.static('/atomics/', path=THIS_DIR / 'art/atomics', show_index=True)
    ])
    setup_agent_communication_routes(app)
    return app


async def start_site_two():
    app_two = await create_app_two()

    app_runner = web.AppRunner(app_two)
    runners.append(app_runner)
    await app_runner.setup()

    site = web.TCPSite(app_runner, host=server['host'], port=server['http'])
    message = """
======== Running on http://localhost:{0}  (AGENT)===========
""".format(server['http'])

    await site.start()
    print(message)


async def start_site_one():
    app_one = await create_app()
    app_runner = web.AppRunner(app_one)
    runners.append(app_runner)
    await app_runner.setup()

    # HTTPS using Secure Sockets Layer
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile='certificates/thremulate.crt', keyfile='certificates/thremulate.key')
    site = web.TCPSite(runner=app_runner, host=server['host'], port=server['https'],
                       ssl_context=ssl_context)
    message = """
======== Running on https://localhost:{0} (OPERATOR)========
""".format(server['https'])

    await site.start()
    print(message)


if __name__ == '__main__':
    setup_logging()
    setup_db()
    loop = asyncio.get_event_loop()
    loop.create_task(start_site_one())
    loop.create_task(start_site_two())

    try:
        loop.run_forever()
    except:
        pass
    finally:
        for runner in runners:
            loop.run_until_complete(runner.cleanup())
