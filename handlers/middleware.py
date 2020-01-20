import aiohttp_jinja2
from aiohttp import web


@web.middleware
async def response_headers(request, handler):
    response = await handler(request)
    # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Content-Security-Policy blocks inline styles and inline javascript
    # response.headers['Content-Security-Policy'] = "default-src 'self'"

    return response


@aiohttp_jinja2.template('middleware/404.html')
async def handle_404(request):
    return {'title': 'Page not found'}


@aiohttp_jinja2.template('middleware/500.html')
async def handle_500(request):
    return {'title': 'Error'}


def create_error_middleware(overrides):
    @web.middleware
    async def error_middleware(request, handler):

        try:
            response = await handler(request)

            override = overrides.get(response.status)
            if override:
                return await override(request)

            return response

        except web.HTTPException as ex:
            override = overrides.get(ex.status)
            if override:
                return await override(request)

            raise

    return error_middleware


def setup_middleware(app):
    error_middleware = create_error_middleware({
        404: handle_404,
        500: handle_500
    })
    app.middlewares.append(error_middleware)
    app.middlewares.append(response_headers)
