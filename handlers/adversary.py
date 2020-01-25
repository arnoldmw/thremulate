import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import check_authorized
from aiohttp_session import get_session
# noinspection PyUnresolvedReferences
from database import Adversary, Agent


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
    username = session['username']

    return {'username': username, 'adversaries': adversaries, 'title': 'Adversaries'}


async def adversary_add(request):
    """
    Adds an adversary to the database.
    :param request:
    :return: '/adversaries' if successful other an exception is raised.
    """
    await check_authorized(request)
    data = await request.post()
    Adversary.create(name=data['updateName'])
    raise web.HTTPFound('/adversaries')


@aiohttp_jinja2.template('adversary/adversary_details.html')
async def adversary_details(request):
    """
    Retrieves the template with the details of an adversary.
    :param request:
    :return: '/adversary_details'  if successful other an exception is raised.
    """
    await check_authorized(request)
    agents = []

    if 'id' in request.match_info:
        camp_id = request.match_info['id']

        camp = Adversary.get(Adversary.id == camp_id)
        camp_details = {'name': camp.name, 'created': camp.created_date.strftime("%d-%b-%Y %H:%M:%S"),
                        'updated': camp.updated_date.strftime("%d-%b-%Y %H:%M:%S")}
        for ag in camp.agents:
            agents.append({'id': ag.id, 'name': ag.name, 'platform': ag.platform,
                           'initial_contact': ag.initial_contact.strftime("%d-%b-%Y %H:%M:%S"),
                           'last_contact': ag.last_contact.strftime("%d-%b-%Y %H:%M:%S")})

        session = await get_session(request)
        username = session['username']
        return {'username': username, 'adversary': camp_details, 'agents': agents, 'title': 'Adversary Details'}

    else:
        session = await get_session(request)
        username = session['username']
        context = {'username': username}
        response = aiohttp_jinja2.render_template('adversary/adversary_index.html', request, context)
        return response


async def adversary_update(request):
    """
    Updates the name of an adversary.
    :param request:
    :return: '/adversaries' if successful other an exception is raised.
    """
    await check_authorized(request)
    data = await request.post()
    # TODO: Check for UNIQUE constraint
    q = Adversary.update(name=data['name']).where(Adversary.id == data['id'])
    q.execute()
    raise web.HTTPFound('/adversaries')


async def adversary_delete(request):
    """
    Deletes an adversary.
    :param request:
    :return: '/adversaries if successful otherwise an exception is raised.
    """
    await check_authorized(request)
    data = await request.post()
    q = Adversary.delete().where(Adversary.id == data['id'])
    q.execute()
    raise web.HTTPFound('/adversaries')


def setup_campaign_routes(app):
    """
    Adds adversary routes to the application.
    :param app:
    :return: None
    """
    app.add_routes([
        web.get('/adversaries', adversary_index, name='adversaries'),
        web.get('/adversary_details/{id}', adversary_details, name='adversary_details'),
        web.post('/adversary_add', adversary_add),
        web.post('/adversary_update', adversary_update),
        web.post('/adversary_delete', adversary_delete),
    ])
