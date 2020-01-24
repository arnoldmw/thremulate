import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import check_authorized
from aiohttp_session import get_session
# noinspection PyUnresolvedReferences
from database import Adversary, Agent


@aiohttp_jinja2.template('adversary/campaign_index.html')
async def campaign_index(request):
    await check_authorized(request)
    adversaries = []

    query = Adversary.select()

    for adv in query:
        adversaries.append({'id': adv.id, 'name': adv.name, 'created': adv.created_date, 'updated': adv.updated_date,
                            'no_of_agents': adv.agents.count()})

    session = await get_session(request)
    username = session['username']

    return {'username': username, 'adversaries': adversaries, 'title': 'Adversaries'}


async def campaign_add(request):
    await check_authorized(request)
    data = await request.post()
    Adversary.create(name=data['addName'])
    raise web.HTTPFound('/adversaries')


@aiohttp_jinja2.template('adversary/campaign_details.html')
async def campaign_details(request):
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
        response = aiohttp_jinja2.render_template('adversary/campaign_index.html', request, context)
        return response


async def campaign_update(request):
    await check_authorized(request)
    data = await request.post()
    # TODO: Check for UNIQUE constraint
    q = Adversary.update(name=data['name']).where(Adversary.id == data['id'])
    q.execute()
    raise web.HTTPFound('/adversaries')


async def campaign_delete(request):
    await check_authorized(request)
    data = await request.post()
    q = Adversary.delete().where(Adversary.id == data['id'])
    q.execute()
    raise web.HTTPFound('/adversaries')


def setup_campaign_routes(app):
    app.add_routes([
        web.get('/adversaries', campaign_index, name='adversaries'),
        web.get('/campaign_details/{id}', campaign_details, name='campaign_details'),
        web.post('/campaign_add', campaign_add),
        web.post('/campaign_update', campaign_update),
        web.post('/campaign_delete', campaign_delete),
    ])
