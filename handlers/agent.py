import aiohttp_jinja2
from aiohttp import web
from aiohttp_session import get_session
from database import *
import datetime

# noinspection PyUnresolvedReferences
from art.run_atomics import get_commands
# noinspection PyUnresolvedReferences
from art.run_atomics import better_get_commands
# noinspection PyUnresolvedReferences
from art.run_atomics import get_all_techniques, get_one_technique_and_params
# noinspection PyUnresolvedReferences
from art.run_atomics import get_all_techniques_and_params


@aiohttp_jinja2.template('agent/agent_index.html')
async def agent_index(request):
    session = await get_session(request)
    # fas fa - broadcast - tower
    agents = []

    # Avoids the N + 1 problem through fetching the related table together
    query = (Agent
             .select(Agent, Campaign)
             .join(Campaign))

    for ag in query:
        ic = ag.initial_contact.strftime("%d-%b-%Y %H:%M:%S")
        lc = ag.last_contact.strftime("%d-%b-%Y %H:%M:%S")

        agents.append({'id': ag.id, 'name': ag.name, 'initial_contact': ic,
                       'last_contact': lc, 'campaign': ag.campaign.name})

    username = session['username']
    return {'agents': agents, 'title': 'Agents', 'username': username}


@aiohttp_jinja2.template('agent/assign_tasks.html')
async def assign_tasks(request):
    agent_id = request.match_info['id']

    ag = Agent.get(Agent.id == agent_id)
    agent_platform = ag.platform

    tech_list = get_all_techniques(agent_platform)

    return {'techs': tech_list, 'agent_id': agent_id, 'title': 'Techniques'}


async def assign_tasks_post(request):
    data = await request.post()

    agent_id = data['agent_id']
    rec_data = []

    for key in data.keys():
        if data[key] is not '':
            print(key + ': ' + data[key])
            rec_data.append(data[key])

    print('Data got')
    print(rec_data)
    data_len = rec_data.__len__()
    rec_data = rec_data[1:data_len - 1]

    for data in rec_data:
        AgentTechnique.create(technique_id=data, agent_id=agent_id)

    raise web.HTTPFound('/agents')


# AGENT SENDS RESULTS BACK TO C2
async def agent_output(request):
    data = await request.post()
    # agent_id = data['id']
    # print(data[2])
    # tech_id = data['']
    # print(type(data))
    keys = []
    for key in data.keys():
        keys.append(key)
    print(keys)

    output = data[keys[1]]

    # ADDING RESULTS AND OUTPUT FROM AN AGENT
    query = AgentTechnique.update(output=output, executed=datetime.datetime.now(), result=1).where(
        AgentTechnique.agent_id == keys[0] and
        AgentTechnique.technique_id == int(keys[1][1:]))
    query.execute()

    return web.Response(text='Hello')


# TECHNIQUES ASSIGNED TO AN AGENT
async def agent_techniques(request):
    agent_id = request.match_info['id']
    tech_id = ''

    for agent_techs in AgentTechnique.select().where(AgentTechnique.agent_id == agent_id):
        # return agent_techs.technique_id
        tech_id = tech_id + 'T' + str(agent_techs.technique_id) + ','

    return web.Response(text=tech_id)


# SENDS AGENT COMMANDS 5TO RUN, MAKE IT A POST METHOD
async def agent_tasks(request):
    agent_id = request.match_info['id']

    techniques = []

    for agent_techs in AgentTechnique.select().where(AgentTechnique.agent_id == agent_id):
        # return agent_techs.technique_id
        tech_id = 'T' + str(agent_techs.technique_id)

        techniques.append(tech_id)

    ag = Agent.get(Agent.id == agent_id)
    agent_platform = ag.platform

    # Formulating parameters
    list_of_param_dict = []
    for t in techniques:
        params = Parameter.select().where(Parameter.agent_id == agent_id and Parameter.technique_id == t[1:])
        param_number = params.count()

        if param_number != 0:
            param_dict = {}
            for p in params:
                param_dict.__setitem__(p.param_name, p.param_value)
                # list_of_param_dict.append(param_dict)
                # param_dict.__setitem__(p.param_name, p.param_value)
            list_of_param_dict.append(param_dict)
        else:
            list_of_param_dict.append(None)

    # print('parameters submitted')
    # print(param_dict)

    # commands = assignments(techniques, agent_platform, param_dict)
    commands = assignments(techniques, agent_platform, list_of_param_dict)
    return web.Response(text=commands)


def assignments(tech_list, plat, parameters):
    command_list = better_get_commands(tech_list, plat, parameters)

    string_commands = ''

    for com in command_list:
        com = com + ','
        string_commands = string_commands + com

    return string_commands


@aiohttp_jinja2.template('agent/agent_details.html')
async def agent_details(request):
    agent_id = request.match_info['id']

    # agt = (AgentTechnique.select(Agent, AgentTechnique).join(Agent).where(AgentTechnique.agent_id == agent_id))
    # agt = AgentTechnique.select().join(Technique).where(AgentTechnique.agent_id == agent_id)

    agt = Agent.select(Agent.name, Agent.id, Agent.campaign_id, AgentTechnique, Technique) \
        .join(AgentTechnique) \
        .join(Technique) \
        .where(AgentTechnique.agent_id == agent_id)

    details = []
    agent = {}
    # print(agt)
    for at in agt:
        details.append({'name': at.agenttechnique.technique_id.name, 'output': at.agenttechnique.output})
        agent = {'name': at.name, 'campaign': at.campaign.name, 'domain': at.domain}

    # for at in agt:
    #     details.append({'name': at.technique_id.name, 'output': at.output})

    return {'agent': agent, 'details': details, 'title': 'Agent Details'}


@aiohttp_jinja2.template('agent/agent_edit.html')
async def agent_edit(request):
    agent_id = request.match_info['id']
    campaigns = []

    agt = Agent.get(Agent.id == agent_id)
    agent = {'agt_id': agt.id, 'agt_name': agt.name, 'camp_id': agt.campaign_id}

    camps = Campaign.select()
    for camp in camps:
        campaigns.append({'camp_id': camp.id, 'camp_name': camp.name})

    return {'agent': agent, 'campaigns': campaigns, 'title': 'Update Agent'}


async def agent_edit_post(request):
    data = await request.post()

    agent_id = data['agent_id']
    agent_name = data['name']
    campaign_id = data['campaign']

    query = Agent.update(name=agent_name, campaign_id=campaign_id).where(Agent.id == agent_id)
    query.execute()

    # TODO: Show message to user that details were submitted

    raise web.HTTPFound('/agents')


@aiohttp_jinja2.template('agent/customize_technique.html')
async def customize_technique(request):
    arr = []
    data = await request.post()

    for key in data.keys():
        # print(key)
        arr.append(data[key])

    # print('Dataaaaa')
    # print(arr)
    # TODO: Tends to throw IndexError
    agent_id = arr[0]
    tech_id = 'T' + arr[1]

    tech = get_one_technique_and_params(tech_id)
    tech.__setitem__('agent_id', agent_id)
    tech.__setitem__('title', 'Techniques')

    return tech


async def customize_technique_post(request):
    data = await request.post()
    # TODO: Show message to user that details were submitted

    # print('Custom param data')
    keys = data['keys'].split(',')
    values = data['values'].split(',')
    i = 2

    # print(keys)
    # print(values)

    agent_id = values[0]
    tech_id = values[1]

    # Add to AgentTechnique table
    AgentTechnique.create(technique_id=tech_id, agent_id=agent_id)

    # Add to Parameters table
    for key in keys:
        # print(key)
        # print(values[i])
        Parameter.create(agent_id=agent_id, technique_id=tech_id, param_name=str(key), param_value=str(values[i]))
        i = i + 1

    # send = '/assign_tasks/' + agent_id
    # raise web.HTTPFound(send)
    return web.Response(text='Form received')


async def register_agent(request):
    data = await request.post()
    # print(type(data))
    # print(data.keys())
    agent_id = data['id']
    host_name = data['host_name']

    Agent.create(id=agent_id, name=host_name, os_name='Windows 7', os_version='7.3.4', product_id='6KKL',
                 domain='work.com', campaign=Campaign.get(Campaign.name == 'Cobalt'))
    return web.Response(text=str(agent_id) + ' ' + host_name)


def setup_agent_routes(app):
    app.add_routes([
        web.get('/agent_techniques/{id}', agent_techniques),
        web.get('/agent_tasks/{id}', agent_tasks),
        web.post('/customize_technique', customize_technique, name='customize_technique'),
        web.post('/customize_technique_post', customize_technique_post, name='customize_technique_post'),
        web.post('/agent_output', agent_output),
        web.get('/assign_tasks/{id}', assign_tasks, name='assign_get'),
        web.post('/assign_tasks_post', assign_tasks_post, name='assign_post'),
        web.post('/register_agent', register_agent),
        web.get('/agents', agent_index, name='agents'),
        web.get('/agent_details/{id}', agent_details, name='agent_details'),
        web.get('/agent_edit/{id}', agent_edit, name='agent_edit'),
        web.post('/agent_edit_post', agent_edit_post, name='agent_edit_post'),

    ])
