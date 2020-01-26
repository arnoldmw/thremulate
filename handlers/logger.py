import datetime
import json
import logging

from main import secret_key
import base64
from cryptography import fernet
from aiohttp.abc import AbstractAccessLogger

secret_key = base64.urlsafe_b64encode(secret_key)


class AccessLogger(AbstractAccessLogger):

    def log(self, request, response, time):
        fern = fernet.Fernet(secret_key)
        session_dict = {'session': {'AIOHTTP_SECURITY': '', 'current_user': {'fname': ''}}}
        if 'AIOHTTP_SESSION' in request.cookies:
            session_val = fern.decrypt(request.cookies['AIOHTTP_SESSION'].encode('utf-8'))
            session_dict.clear()
            session_dict = json.loads(session_val.decode('utf-8'))

        self.logger.info(f' {request.remote} '

                         f'{session_dict["session"]["AIOHTTP_SECURITY"]} '
                         f'{session_dict["session"]["current_user"]["fname"]} '
                         f'[{datetime.datetime.now()} +{time.__round__(4)}] '
                         f'"{request.method} {request.path} HTTP/{request.version[0]}.{request.version[1]}" '
                         f'{response.status} '
                         f'{response.content_length} '
                         # f'{request.headers["User-Agent"]} '
                         )
        # Stops asyncio warnings because asycio implements its own exception handling. This throws many exceptions
        # that cannot be handled due to this being a development environment.
        logging.getLogger('asyncio').setLevel(logging.CRITICAL)

        logging.getLogger('peewee').setLevel(logging.CRITICAL)
        logging.getLogger('aiohttp.access').setLevel(logging.INFO)
