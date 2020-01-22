import datetime
# noinspection PyUnresolvedReferences
import json
# noinspection PyUnresolvedReferences
from main import secret_key
import base64
from cryptography import fernet
from aiohttp.abc import AbstractAccessLogger

secret_key = base64.urlsafe_b64encode(secret_key)


class AccessLogger(AbstractAccessLogger):

    def log(self, request, response, time):
        fern = fernet.Fernet(secret_key)
        session_val = fern.decrypt(request.cookies['AIOHTTP_SESSION'].encode('utf-8'))
        session_dict = json.loads(session_val.decode('utf-8'))

        self.logger.info(f'{request.remote} '
                         f'{session_dict["session"]["AIOHTTP_SECURITY"]} '
                         f'{session_dict["session"]["username"]} '
                         f'[{datetime.datetime.now()} +{time.__round__(4)}] '
                         f'"{request.method} {request.path} HTTP/{request.version[0]}.{request.version[1]}" '
                         f'{response.status} '
                         f'{response.content_length} '
                         # f'{request.headers["User-Agent"]} '
                         )
