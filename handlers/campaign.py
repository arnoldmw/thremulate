import aiohttp_jinja2
from aiohttp import web
from aiohttp_session import get_session
from database import *
import datetime


@aiohttp_jinja2.template('campaign/campaign_index.html')
async def campaign_index(request):
    campaigns = []

    # Avoids the N + 1 problem through fetching the related table together
    query = (Campaign
             .select(Campaign, fn.Count(Agent.id).alias('count'))
             .join(Agent, JOIN.LEFT_OUTER)
             .group_by(Campaign)
             )

    for camp in query:
        created = camp.created_date.strftime("%d-%b-%Y %H:%M:%S")
        updated = camp.updated_date.strftime("%d-%b-%Y %H:%M:%S")

        campaigns.append({'id': camp.id, 'name': camp.name, 'created': created, 'updated': updated,
                          'no_of_agents': camp.count})
    session = await get_session(request)
    username = session['username']
    return {'username': username, 'campaigns': campaigns, 'title': 'Campaigns'}


async def campaign_add(request):
    data = await request.post()
    Campaign.create(name=data['addName'])
    raise web.HTTPFound('/campaigns')


@aiohttp_jinja2.template('campaign/campaign_details.html')
async def campaign_details(request):
    print(request)
    # camp_details = {}
    agents = []

    if 'id' in request.match_info:
        camp_id = request.match_info['id']

        camp = Campaign.get(Campaign.id == camp_id)
        camp_details = {'name': camp.name, 'created': camp.created_date.strftime("%d-%b-%Y %H:%M:%S"),
                        'updated': camp.updated_date.strftime("%d-%b-%Y %H:%M:%S")}
        for ag in camp.agents:
            agents.append({'id': ag.id, 'name': ag.name, 'platform': ag.platform,
                           'initial_contact': ag.initial_contact.strftime("%d-%b-%Y %H:%M:%S"),
                           'last_contact': ag.last_contact.strftime("%d-%b-%Y %H:%M:%S")})

        session = await get_session(request)
        username = session['username']
        return {'username': username, 'campaign': camp_details, 'agents': agents, 'title': 'Campaign Details'}

    else:
        session = await get_session(request)
        username = session['username']
        context = {'username': username}
        response = aiohttp_jinja2.render_template('campaign/campaign_index.html', request, context)
        return response


async def campaign_update(request):
    data = await request.post()
    # TODO: Check for UNIQUE constraint
    q = Campaign.update(name=data['name']).where(Campaign.id == data['id'])
    q.execute()
    raise web.HTTPFound('/campaigns')


async def campaign_delete(request):
    data = await request.post()
    q = Campaign.delete().where(Campaign.id == data['id'])
    q.execute()
    raise web.HTTPFound('/campaigns')


def setup_campaign_routes(app):
    app.add_routes([
        web.get('/campaigns', campaign_index, name='campaigns'),
        web.get('/campaign_details/{id}', campaign_details, name='campaign_details'),
        web.post('/campaign_add', campaign_add),
        web.post('/campaign_update', campaign_update),
        web.post('/campaign_delete', campaign_delete),
    ])
