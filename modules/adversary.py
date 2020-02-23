import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import check_authorized
from aiohttp_session import get_session
from stae.database import Adversary


@aiohttp_jinja2.template('adversary/adversary_index.html')
async def adversary_index(request):
    """
    Retrieves the template showing all adversaries.
    :param request:
    :return: '/adversaries' if successful other an exception is raised.
    """
    await check_authorized(request)
    adversaries = []

    query = Adversary.select()

    for adv in query:
        adversaries.append({'id': adv.id, 'name': adv.name, 'created': adv.created_date, 'updated': adv.updated_date,
                            'no_of_agents': adv.agents.count()})

    session = await get_session(request)
    current_user = session['current_user']
    return {'current_user': current_user, 'adversaries': adversaries, 'title': 'Adversaries'}


async def adversary_add(request):
    """
    Adds an adversary to the database.
    :param request:
    :return: '/adversaries' if successful other an exception is raised.
    """
    await check_authorized(request)
    data = await request.post()
    try:
        Adversary.get(Adversary.name == data['addName'])
        return web.Response(text='exists')
    except KeyError:
        return web.Response(status=400)
    except Adversary.DoesNotExist:
        Adversary.create(name=data['addName'])
        return web.Response(text='success')


@aiohttp_jinja2.template('adversary/adversary_details.html')
async def adversary_details(request):
    """
    Retrieves the template with the details of an adversary.
    :param request:
    :return: '/adversary_details'  if successful other an exception is raised.
    """
    await check_authorized(request)
    agents = []

    try:
        adv_id = request.match_info['id']
        adv = Adversary.get(Adversary.id == adv_id)
        adv_details = {'name': adv.name, 'created': adv.created_date.strftime("%d-%b-%Y %H:%M:%S"),
                       'updated': adv.updated_date.strftime("%d-%b-%Y %H:%M:%S")}
        for ag in adv.agents:
            agents.append({'id': ag.id, 'name': ag.name, 'platform': ag.platform,
                           'initial_contact': ag.initial_contact.strftime("%d-%b-%Y %H:%M:%S"),
                           'last_contact': ag.last_contact.strftime("%d-%b-%Y %H:%M:%S")})

        session = await get_session(request)
        current_user = session['current_user']
        return {'current_user': current_user, 'adversary': adv_details, 'agents': agents, 'title': 'Adversary Details'}

    except KeyError:
        return web.Response(status=400)
    except Adversary.DoesNotExist:
        return web.Response(status=400)


async def adversary_update(request):
    """
    Updates the name of an adversary.
    :param request:
    :return: '/adversaries' if successful other an exception is raised.
    """
    await check_authorized(request)
    data = await request.post()

    try:
        name = data['name']
        adv_id = data['id']
        Adversary.update(name=name).where(Adversary.id == adv_id).execute()
        raise web.HTTPFound('/adversaries')
    except KeyError:
        return web.Response(status=400)


async def adversary_delete(request):
    """
    Deletes an adversary.
    :param request:
    :return: '/adversaries if successful otherwise an exception is raised.
    """
    await check_authorized(request)
    data = await request.post()
    try:
        Adversary.delete().where(Adversary.id == data['id']).execute()
        raise web.HTTPFound('/adversaries')
    except KeyError:
        return web.Response(status=400)


def setup_campaign_routes(app):
    """
    Adds adversary routes to the application.
    :param app:
    :return: None
    """
    app.add_routes([
        web.get('/adversaries', adversary_index, name='adversaries'),
        web.get('/adversary_details/{id}', adversary_details, name='adversary_details'),
        web.post('/adversary_add', adversary_add, name='adversary_add'),
        web.post('/adversary_update', adversary_update, name='adversary_update'),
        web.post('/adversary_delete', adversary_delete, name='adversary_delete'),
    ])
