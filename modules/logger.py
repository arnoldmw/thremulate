import datetime
import json
import logging

import base64
from cryptography import fernet
from aiohttp.abc import AbstractAccessLogger
secret_key = b'\xd0\x04)E\x14\x98\xa1~\xecE\xae>(\x1d6\xec\xbfQ\xa4\x19\x0e\xbcre,\xf8\x8f\x84WV.\x8d'
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

        logging.getLogger('peewee').setLevel(logging.CRITICAL)
        logging.getLogger('aiohttp.access').setLevel(logging.INFO)
