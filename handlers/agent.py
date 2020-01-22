import aiohttp_jinja2
from aiohttp import web
from aiohttp_session import get_session
from database import *
import datetime

import string
import random

# noinspection PyUnresolvedReferences
from art.run_atomics import get_commands
# noinspection PyUnresolvedReferences
from art.run_atomics import agent_commands
# noinspection PyUnresolvedReferences
from art.run_atomics import get_all_techniques, get_one_technique_and_params
# noinspection PyUnresolvedReferences
from art.run_atomics import get_all_techniques_and_params


@aiohttp_jinja2.template('agent/agent_index.html')
async def agent_index(request):
    # fas fa - broadcast - tower
    agents = []

    # Avoids the N + 1 problem through fetching the related table together
    query = Agent.select().join(Adversary)

    for ag in query:
        # ic = ag.initial_contact.strftime("%d-%b-%Y %H:%M:%S")
        # lc = ag.last_contact.strftime("%d-%b-%Y %H:%M:%S")

        agents.append({'id': ag.id, 'name': ag.name, 'initial_contact': ag.initial_contact,
                       'last_contact': ag.last_contact, 'adversary': ag.adversary.name})

    session = await get_session(request)
    username = session['username']
    return {'username': username, 'agents': agents, 'title': 'Agents'}


@aiohttp_jinja2.template('agent/assign_tasks.html')
async def assign_tasks(request):
    agent_id = request.match_info['id']

    ag = Agent.get(Agent.id == agent_id)
    agent_platform = ag.platform

    tech_matrix = get_all_techniques(agent_platform)

    session = await get_session(request)
    username = session['username']
    return {'username': username, 'matrix': tech_matrix, 'agent_id': agent_id, 'title': 'Techniques'}


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
    agent_id = data['id']
    # print(data[2])
    tech_id = data['tech'].split(':')[0]
    test_num = data['tech'].split(':')[1]
    executed = data['executed']

    raw_output = data['output']

    status = ''.join(raw_output.split('--')[:1])
    if 'Success' == status:
        result = True
    else:
        result = False

    output = ''.join(raw_output.split('--')[1:])
    if output == '':
        output = 'This command ran successfully but returned no console output'

    # ADDING RESULTS AND OUTPUT FROM AN AGENT
    AgentTechnique.update(output=output, executed=executed, result=result).where(
        (AgentTechnique.agent_id == agent_id) & (AgentTechnique.technique_id == tech_id) & (
                    AgentTechnique.test_num == test_num)).execute()

    return web.Response(text='success')


# TECHNIQUES ASSIGNED TO AN AGENT
async def agent_techniques(request):
    agent_id = request.match_info['id']
    tech_id = ''

    for agent_techs in AgentTechnique.select().where(AgentTechnique.agent_id == agent_id):
        # return agent_techs.technique_id
        tech_id = tech_id + str(agent_techs.technique_id) + ':' + str(agent_techs.test_num) + ','

    return web.Response(text=tech_id)


# SENDS AGENT COMMANDS TO RUN, MAKE IT A POST METHOD
async def agent_tasks(request):
    agent_id = request.match_info['id']

    techniques = []
    tests = []
    # t = {'tech_id': '', 'test_num': ''}

    for agent_techs in AgentTechnique.select().where(AgentTechnique.agent_id == agent_id):
        tech_id = ('T%s' % agent_techs.technique_id)
        test_num = agent_techs.test_num

        techniques.append({'tech_id': tech_id, 'test_num': test_num})

    ag = Agent.get(Agent.id == agent_id)
    agent_platform = ag.platform

    # Formulating parameters
    list_of_param_dict = []
    for t in techniques:
        params = Parameter.select().where(Parameter.agent_id == agent_id and Parameter.technique_id == t['tech_id'][1:])
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
    command_list = agent_commands(tech_list, plat, parameters)

    string_commands = ''

    for com in command_list:
        string_commands = string_commands + com

    return string_commands


@aiohttp_jinja2.template('agent/agent_details.html')
async def agent_details(request):
    agent_id = request.match_info['id']

    details = []
    agent = {}

    agt = Agent.select(Agent, AgentTechnique).join(AgentTechnique).join(Adversary, on=Agent.adversary == Adversary.id) \
        .where(AgentTechnique.agent_id == agent_id)

    for ag in agt:
        agent = {'id': ag.id, 'name': ag.name, 'adversary': ag.adversary.name, 'domain': ag.domain,
                 'platform': ag.platform}
        for tech in ag.techniques:
            details.append({'tech_id': tech.technique_id, 'test_num': tech.test_num, 'name': tech.technique_id.name,
                            'output': tech.output, 'executed': tech.executed, 'result': tech.result})
        break

    session = await get_session(request)
    username = session['username']
    return {'username': username, 'agent': agent, 'details': details, 'title': 'Agent Details'}


@aiohttp_jinja2.template('agent/agent_edit.html')
async def agent_edit(request):
    agent_id = request.match_info['id']
    adversaries = []

    agt = Agent.get(Agent.id == agent_id)
    agent = {'agt_id': agt.id, 'agt_name': agt.name, 'adv_id': agt.adversary_id, 'kill_date': agt.kill_date}

    advs = Adversary.select()
    for adv in advs:
        adversaries.append({'adv_id': adv.id, 'adv_name': adv.name})

    session = await get_session(request)
    username = session['username']
    return {'username': username, 'agent': agent, 'adversaries': adversaries, 'title': 'Update Agent'}


async def agent_edit_post(request):
    data = await request.post()
    print(data['agent_id'])
    print(data['name'])
    print(data['adversary'])
    print(data['kill_date'])
    print(data['kill_time'])
    agent_id = data['agent_id']
    agent_name = data['name']
    adversary_id = data['adversary']

    # query = Agent.update(name=agent_name, adversary_id=adversary_id).where(Agent.id == agent_id)
    # query.execute()

    # TODO: Show message to user that details were submitted

    raise web.HTTPFound('/agents')


@aiohttp_jinja2.template('agent/customize_technique.html')
async def customize_technique(request):
    # arr = []
    # data = await request.post()

    tech_id = 'T' + request.query['tech_id']
    agent_id = request.query['agent_id']
    agent_platform = Agent.get(Agent.id == agent_id).platform

    session = await get_session(request)
    username = session['username']

    tech = get_one_technique_and_params(tech_id, agent_platform)
    tech.__setitem__('agent_id', agent_id)
    tech.__setitem__('title', 'Techniques')
    tech.__setitem__('username', username)

    return tech


async def customize_technique_post(request):
    data = await request.post()

    try:

        agent_id = data['agent_id']
        tech_id = data['tech_id']
        test_id = data['test_id']

        # Add to AgentTechnique table
        try:
            AgentTechnique.create(technique_id=tech_id, agent_id=agent_id, test_num=test_id)
        except IntegrityError:
            return web.Response(text='Already assigned')

        # Add to Parameters table, if any
        # Anything other than agent_id, tech_id, test_id is a parameter, else no parameters
        if len(data) > 3:
            params = []
            for key in data.keys():
                if key != 'agent_id' and key != 'tech_id' and key != 'test_id':
                    params.append(
                        {'technique_id': tech_id, 'agent_id': agent_id, 'test_num': test_id,
                         'param_name': key, 'param_value': data[key]})

            try:
                Parameter.insert_many(params).execute()
            except IntegrityError:
                return web.Response(text='Invalid parameters')

        return web.Response(text='Assigned')

    except KeyError:
        return web.Response(text='Invalid data')


async def register_agent(request):
    data = await request.post()

    agent_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(7))

    try:
        Agent.create(id=data['id'], name=agent_name, hostname=data['hostname'], platform=data['platform'],
                     plat_version=data['plat_version'], username=data['username'])
    except IntegrityError:
        return web.Response(text='Agent already registered')

    return web.Response(text='Agent has registered')


async def delete_tech_output(request):
    data = await request.post()

    AgentTechnique.update(output=None, result=None, executed=None) \
        .where((AgentTechnique.agent_id == data['agent_id']) & (AgentTechnique.technique_id == data['tech_id'])
               & (AgentTechnique.test_num == data['test_num'])).execute()

    return web.Response(text='deleted')


async def delete_tech_assignment(request):
    data = await request.post()

    AgentTechnique.delete() \
        .where((AgentTechnique.agent_id == data['agent_id']) & (AgentTechnique.technique_id == data['tech_id'])
               & (AgentTechnique.test_num == data['test_num'])).execute()

    return web.Response(text='success')


def setup_agent_routes(app):
    app.add_routes([
        web.get('/agent_techniques/{id}', agent_techniques),
        web.get('/agent_tasks/{id}', agent_tasks),
        web.get('/customize_technique/', customize_technique, name='customize_technique'),
        web.post('/customize_technique_post', customize_technique_post, name='customize_technique_post'),
        web.post('/agent_output', agent_output),
        web.get('/assign_tasks/{id}', assign_tasks, name='assign_get'),
        web.post('/assign_tasks_post', assign_tasks_post, name='assign_post'),
        web.post('/register_agent', register_agent),
        web.post('/delete_tech_output', delete_tech_output),
        web.post('/delete_tech_assignment', delete_tech_assignment),
        web.get('/agents', agent_index, name='agents'),
        web.get('/agent_details/{id}', agent_details, name='agent_details'),
        web.get('/agent_edit/{id}', agent_edit, name='agent_edit'),
        web.post('/agent_edit_post', agent_edit_post, name='agent_edit_post'),

    ])
