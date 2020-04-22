#      Thremulate executes Network Adversary Post Compromise Activities.
#      Copyright (C) 2020  Mwesigwa Arnold
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime
import random
import string

import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import (
    check_authorized,
)
from aiohttp_session import get_session
# noinspection PyUnresolvedReferences
from art.run_atomics import agent_commands
# noinspection PyUnresolvedReferences
from art.run_atomics import get_all_techniques, get_one_technique_and_params
# noinspection PyUnresolvedReferences
from db.database import *
from peewee import IntegrityError


@aiohttp_jinja2.template('agent/agent_index.html')
async def agent_index(request):
    """
    Retrieves all the agents in the database
    :param request:
    :return: Template with all agents if successful otherwise an exception
    """
    await check_authorized(request)
    agents = []

    # Avoids the N + 1 problem through fetching the related table together
    query = Agent.select().join(Adversary)

    for ag in query:
        agents.append({'id': ag.id, 'name': ag.name, 'initial_contact': ag.initial_contact,
                       'last_contact': ag.last_contact, 'adversary': ag.adversary.name})

    session = await get_session(request)
    current_user = session['current_user']
    return {'current_user': current_user, 'agents': agents, 'title': 'Agents'}


@aiohttp_jinja2.template('agent/assign_tasks.html')
async def assign_tasks(request):
    """
    Retrieves template with techniques available for assignment to an agent
    :param request:
    :return: Template with agent techniques available
    """
    await check_authorized(request)

    try:
        agent_id = request.match_info['id']

        ag = Agent.get(Agent.id == agent_id)
        agent_platform = ag.platform

        tech_matrix = get_all_techniques(agent_platform)

        session = await get_session(request)
        current_user = session['current_user']
        return {'current_user': current_user, 'matrix': tech_matrix, 'agent_id': agent_id, 'title': 'Techniques'}
    except KeyError:
        return web.Response(text='Missing agent id', status=400)
    except Agent.DoesNotExist:
        raise web.HTTPFound('/agents')


async def agent_output(request):
    """
    Updates the database with the agent's result of a technique
    :param request:
    :return: 'success' if successful otherwise an exception
    """
    data = await request.post()
    try:
        agent_id = data['id']

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
        Agent.update(last_contact=executed).where(Agent.id == agent_id).execute()
        return web.Response(text='success')
    except KeyError:
        web.Response(text='failed', status=400)
    except Agent.DoesNotExist:
        web.Response(text='failed', status=400)
    except Agent.AgentTechnique:
        web.Response(text='failed', status=400)


async def agent_techniques(request):
    """
    Retrieves the MITRE ATT&CK IDs of techniques assigned to an agent
    :param request:
    :return: MITRE ATT&CK IDs of techniques assigned to an agent
    """
    try:
        agent_id = request.match_info['id']
        tech_id = ''

        for agent_techs in AgentTechnique.select() \
                .where((AgentTechnique.agent_id == agent_id) & (AgentTechnique.executed.is_null(True))):
            tech_id = tech_id + str(agent_techs.technique_id) + ':' + str(agent_techs.test_num) + ','

        return web.Response(text=tech_id)
    except KeyError:
        web.Response(text='failed', status=400)  # Wrong parameters
    except AgentTechnique.DoesNotExist:
        web.Response(text='Agent not assigned')


async def agent_tasks(request):
    """
    Retrieves instructions for the agent
    :param request:
    :return: Agent instruction in text format
    """
    try:
        agent_id = request.match_info['id']
        agent_assignments = ''
        techniques = []
        Agent.update(last_contact=datetime.datetime.now()).where(Agent.id == agent_id).execute()
        assigned_techs = AgentTechnique.select() \
            .where((AgentTechnique.agent_id == agent_id) & (AgentTechnique.executed.is_null(True)))
        ag = Agent.get(Agent.id == agent_id)
        agent_platform = ag.platform
        if assigned_techs.count() != 0:
            test_num = None
            for agent_techs in assigned_techs:
                tech_id = ('T%s' % agent_techs.technique_id)
                test_num = agent_techs.test_num

                techniques.append({'tech_id': tech_id, 'test_num': test_num})

            # Formulating parameters
            list_of_param_dict = []
            for t in techniques:
                params = Parameter.select().where(
                    (Parameter.agent_id == agent_id) & (Parameter.technique_id == t['tech_id'][1:]) & (
                            Parameter.test_num == test_num))
                param_number = params.count()

                if param_number != 0:
                    param_dict = {}
                    for p in params:
                        param_dict.__setitem__(p.param_name, p.param_value)

                    list_of_param_dict.append(param_dict)
                else:
                    list_of_param_dict.append(None)

            agent_assignments = assignments(techniques, agent_platform, list_of_param_dict)

        commands = '{0}++{1}'.format(str(ag.kill_date), agent_assignments)
        return web.Response(text=commands)
    except KeyError:
        web.Response(text='failed')  # Wrong parameters
    except Agent.DoesNotExist:
        web.Response(text='failed', status=400)
    except AgentTechnique.DoesNotExist:
        web.Response(text='failed', status=400)
    except Parameter.DoesNotExist:
        web.Response(text='failed', status=400)


def assignments(tech_list, plat, parameters):
    """
    Retrieves the instructions from the run_atomics module
    :param tech_list: List of techniques assigned to the agent
    :param plat: Platform of the agent
    :param parameters: Parameters for execution of the technique
    :return: string_commands string
    """
    command_list = agent_commands(tech_list, plat, parameters)

    string_commands = ''

    for com in command_list:
        string_commands = string_commands + com

    return string_commands


@aiohttp_jinja2.template('agent/agent_details.html')
async def agent_details(request):
    """
    Retrieves the details of an agent
    :param request:
    :return: '/agent_details' template if successful otherwise an exception
    """
    await check_authorized(request)
    try:
        agent_id = request.match_info['id']

        details = []
        agent = {}

        agt = Agent.select(Agent, Adversary.name).join(Adversary).where(Agent.id == agent_id)

        for ag in agt:
            agent = {'id': ag.id, 'name': ag.name, 'adversary': ag.adversary.name, 'domain': ag.domain,
                     'platform': ag.platform, 'hostname': ag.hostname,
                     'username': ag.username, 'plat_version': ag.plat_version, 'kill_date': ag.kill_date,
                     'initial_contact': ag.initial_contact, 'last_contact': ag.last_contact}
            for tech in ag.techniques:
                details.append({'tech_id': tech.technique_id, 'test_num': tech.test_num, 'name': tech.technique_id.name,
                                'output': tech.output, 'executed': tech.executed, 'result': tech.result})
            break

        session = await get_session(request)
        current_user = session['current_user']
        return {'current_user': current_user, 'agent': agent, 'details': details, 'title': 'Agent Details'}
    except KeyError:
        return web.Response(status=400)
    except Agent.DoesNotExist:
        return web.Response(status=400)


@aiohttp_jinja2.template('agent/agent_edit.html')
async def agent_edit(request):
    """
    Template with a form for editing an agent's details
    :param request:
    :return: Template with the agent edit form if successful otherwise an exception
    """
    await check_authorized(request)
    try:
        agent_id = request.match_info['id']
        adversaries = []

        agt = Agent.get(Agent.id == agent_id)
        agent = {'agt_id': agt.id, 'agt_name': agt.name, 'adv_id': agt.adversary_id, 'kill_date': agt.kill_date}

        advs = Adversary.select()
        for adv in advs:
            adversaries.append({'adv_id': adv.id, 'adv_name': adv.name})

        session = await get_session(request)
        current_user = session['current_user']
        return {'current_user': current_user, 'agent': agent, 'adversaries': adversaries, 'title': 'Update Agent'}
    except KeyError:
        return web.Response(status=400)
    except Agent.DoesNotExist:
        return web.Response(status=400)


async def agent_edit_post(request):
    """
    Updates the details of an agent in the database
    :param request:
    :return: 'agent_details' if successful otherwise an exception
    """
    await check_authorized(request)
    data = await request.post()
    try:
        agent_id = data['agent_id']
        kill_date = data['kill_date']
        if kill_date != '':
            kill_date = kill_date.replace('T', ' ')
            kill_date = '%s:00' % kill_date
        else:
            kill_date = None

        Agent.update(name=data['name'], adversary_id=data['adversary'], kill_date=kill_date) \
            .where(Agent.id == agent_id).execute()

        raise web.HTTPFound('/agent_details/%s' % agent_id)
    except KeyError:
        return web.Response(status=400)
    except Agent.DoesNotExist:
        return web.Response(status=400)


async def agent_delete_post(request):
    """
    Deletes an agent.
    :param request:
    :return: 'success' if successful otherwise an exception is raised.
    """
    await check_authorized(request)
    data = await request.post()

    try:
        agent_id = data['agent_id']
        Parameter.delete().where(Parameter.agent_id == agent_id).execute()
        AgentTechnique.delete().where(AgentTechnique.agent_id == agent_id).execute()
        Agent.delete().where(Agent.id == agent_id).execute()
        return web.Response(text='success', status=200)
    except KeyError:
        return web.Response(text='error', status=400)
    except Parameter.DoesNotExist:
        pass
    except AgentTechnique.DoesNotExist:
        pass
    except Agent.DoesNotExist:
        return web.Response(text='error', status=400)


@aiohttp_jinja2.template('agent/customize_technique.html')
async def customize_technique(request):
    """
    Retrieves the template with the available techniques for an agent
    :param request:
    :return: customize_technique.html template
    """
    await check_authorized(request)
    try:
        tech_id = 'T' + request.query['tech_id']
        agent_id = request.query['agent_id']
        agent_platform = Agent.get(Agent.id == agent_id).platform

        session = await get_session(request)
        current_user = session['current_user']

        tech = get_one_technique_and_params(tech_id, agent_platform)
        tech.__setitem__('agent_id', agent_id)
        tech.__setitem__('title', 'Techniques')
        tech.__setitem__('current_user', current_user)

        return tech
    except KeyError:
        return web.Response(status=400)
    except Agent.DoesNotExist:
        return web.Response(status=400)


async def customize_technique_post(request):
    """
    Adds the assigned technique to an agent in the database
    :param request:
    :return: 'Assigned' if successful otherwise an exception
    """
    await check_authorized(request)
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
        return web.Response(status=400)
    except AgentTechnique.DoesNotExist:
        return web.Response(status=400)
    except AgentTechnique.IntegrityError:
        return web.Response(status=400)


async def register_agent(request):
    """
    Registers an agent's details when it beacons to the server
    :param request:
    :return: 'Agent has registered' if successful otherwise an exception
    """
    data = await request.post()

    agent_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(7))
    try:
        agt = Agent.get(Agent.hostname == data['hostname'])
        return web.Response(text='Agent already registered.%s' % agt.id)
    except Agent.DoesNotExist:
        try:
            Agent.create(id=data['id'], name=agent_name, hostname=data['hostname'], platform=data['platform'],
                         plat_version=data['plat_version'], username=data['username'],
                         adversary=Adversary.get(Adversary.name == 'Unknown'))
            return web.Response(text='Agent has registered.%s' % data['id'])
        except Adversary.DoesNotExist:
            Adversary.create(name='Unknown')
            Agent.create(id=data['id'], name=agent_name, hostname=data['hostname'], platform=data['platform'],
                         plat_version=data['plat_version'], username=data['username'],
                         adversary=Adversary.get(Adversary.name == 'Unknown'))
            return web.Response(text='Agent has registered.%s' % data['id'])
    except KeyError:
        web.Response(text='Invalid registration data', status=400)


async def delete_tech_output(request):
    """
    Deletes the results of a technique in the database
    :param request:
    :return: 'deleted' if successful otherwise an exception
    """
    await check_authorized(request)
    data = await request.post()
    try:
        AgentTechnique.update(output=None, result=None, executed=None) \
            .where((AgentTechnique.agent_id == data['agent_id']) & (AgentTechnique.technique_id == data['tech_id'])
                   & (AgentTechnique.test_num == data['test_num'])).execute()

        return web.Response(text='deleted')
    except KeyError:
        web.Response(text='Invalid data', status=400)
    except AgentTechnique.DoesNotExist:
        return web.Response(text='Invalid data', status=400)
    except AgentTechnique.IntegrityError:
        return web.Response(text='Invalid data', status=400)


async def delete_tech_assignment(request):
    """
    Deletes a technique assigned to an agent
    :param request:
    :return: 'success' if successful otherwise an exception
    """
    await check_authorized(request)
    data = await request.post()
    try:
        AgentTechnique.delete() \
            .where((AgentTechnique.agent_id == data['agent_id']) & (AgentTechnique.technique_id == data['tech_id'])
                   & (AgentTechnique.test_num == data['test_num'])).execute()
        Parameter.delete() \
            .where((Parameter.agent_id == data['agent_id']) & (Parameter.technique_id == data['tech_id'])
                   & (Parameter.test_num == data['test_num'])).execute()
        return web.Response(text='success')
    except KeyError:
        return web.Response(text='Invalid data', status=400)
    except AgentTechnique.DoesNotExist:
        return web.Response(text='Invalid data', status=400)


def setup_agent_communication_routes(app):
    """
    Add agent communication routes to the application
    :param app:
    :return:
    """
    app.add_routes([
        web.get('/agent_techniques/{id}', agent_techniques),
        web.get('/agent_tasks/{id}', agent_tasks),
        web.post('/agent_output', agent_output),
        web.post('/register_agent', register_agent),
    ])


def setup_agent_routes(app):
    """
    Adds operator-agent routes to the application.
    :param app:
    :return: None
    """
    app.add_routes([
        web.get('/customize_technique/', customize_technique, name='customize_technique'),
        web.post('/customize_technique_post', customize_technique_post, name='customize_technique_post'),
        web.get('/assign_tasks/{id}', assign_tasks, name='assign_get'),
        web.post('/delete_tech_output', delete_tech_output),
        web.post('/delete_tech_assignment', delete_tech_assignment),
        web.get('/agents', agent_index, name='agents'),
        web.get('/agent_details/{id}', agent_details, name='agent_details'),
        web.get('/agent_edit/{id}', agent_edit, name='agent_edit'),
        web.post('/agent_edit_post', agent_edit_post, name='agent_edit_post'),
        web.post('/agent_delete_post', agent_delete_post, name='agent_delete_post'),

    ])
