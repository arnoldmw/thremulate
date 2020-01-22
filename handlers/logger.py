import datetime
from main import secret_key
import base64
from aiohttp.abc import AbstractAccessLogger
from aiohttp_security import authorized_userid


class AccessLogger(AbstractAccessLogger):

    user_id = ''
    secret_key = base64.urlsafe_b64decode(secret_key)
    @staticmethod
    async def get_user_id(request):
        # global user_id
        AccessLogger.user_id = await authorized_userid(request)
        return None

    # async def invoke(self, request):
    #     await AccessLogger.get_user_id(request)

    def log(self, request, response, time):
        async def invoke():
            await AccessLogger.get_user_id(request)

        self.logger.info(f'{request.remote} '
                         f'[{datetime.datetime.now()} +{time.__round__(4)}] '
                         f'"{request.method} {request.path} HTTP/{request.version[0]}.{request.version[1]}" '
                         f'{response.status} '
                         f'{response.content_length} '
                         f'{AccessLogger.user_id}'
                         # f'{AccessLogger.get_user_id(self, request) }'
                         # f'done in {time}s: {response.status} '
                         # f'{request.headers["User-Agent"]} '
                         )
