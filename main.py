import aiohttp_csrf
import datetime
import logging
import ssl

from aiohttp import web
import jinja2
from pathlib import Path
import aiohttp_jinja2

# noinspection PyUnresolvedReferences
from middleware import setup_middleware

from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

# noinspection PyUnresolvedReferences
from database import *

# noinspection PyUnresolvedReferences
from db_auth import generate_password_hash

# noinspection PyUnresolvedReferences
from art.run_atomics import get_commands
# noinspection PyUnresolvedReferences
from art.run_atomics import better_get_commands
# noinspection PyUnresolvedReferences
from art.run_atomics import get_all_techniques, get_one_technique_and_params
# noinspection PyUnresolvedReferences
from art.run_atomics import get_all_techniques_and_params

# noinspection PyUnresolvedReferences
# from db_auth import generate_password_hash
from peewee import IntegrityError

THIS_DIR = Path(__file__).parent

FORM_FIELD_NAME = '_csrf_token'
SESSION_NAME = 'csrf_token'


@aiohttp_jinja2.template('base.html')
async def index(request):
    return {
        'title': "Test",
        'intro': "Success! you've setup a basic aiohttp app.",
    }


@aiohttp_jinja2.template('campaign_index.html')
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
    return {'campaigns': campaigns, 'title': 'Campaigns'}


@aiohttp_jinja2.template('agent_index.html')
async def agent_index(request):
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

    return {'agents': agents, 'title': 'Agents'}


# @aiohttp_jinja2.template('assign_tasks.html')
@aiohttp_jinja2.template('assign_tasks_forms.html')
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


@aiohttp_jinja2.template('agent_details.html')
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


@aiohttp_jinja2.template('agent_edit.html')
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


@aiohttp_jinja2.template('customize_technique.html')
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


async def campaign_add(request):
    data = await request.post()
    Campaign.create(name=data['addName'])
    raise web.HTTPFound('/campaigns')


@aiohttp_jinja2.template('campaign_details.html')
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

        return {'campaign': camp_details, 'agents': agents, 'title': 'Campaign Details'}
    else:
        return web.HTTPFound('/campaigns')


async def campaign_update(request):
    data = await request.post()
    q = Campaign.update(name=data['name']).where(Campaign.id == data['id'])
    q.execute()
    raise web.HTTPFound('/campaigns')


async def campaign_delete(request):
    data = await request.post()
    q = Campaign.delete().where(Campaign.id == data['id'])
    q.execute()
    raise web.HTTPFound('/campaigns')


async def register_agent(request):
    data = await request.post()
    # print(type(data))
    # print(data.keys())
    agent_id = data['id']
    host_name = data['host_name']

    Agent.create(id=agent_id, name=host_name, os_name='Windows 7', os_version='7.3.4', product_id='6KKL',
                 domain='work.com', campaign=Campaign.get(Campaign.name == 'Cobalt'))
    return web.Response(text=str(agent_id) + ' ' + host_name)


@aiohttp_jinja2.template('users_index.html')
async def users_index(request):
    users = User.select()
    perms = []
    users_list = []
    user = {}
    for m in users:
        user.__setitem__('id', m.id)
        user.__setitem__('fname', m.fname)
        user.__setitem__('lname', m.lname)
        user.__setitem__('email', m.email)
        user.__setitem__('disabled', m.disabled)
        user.__setitem__('superuser', m.is_superuser)

        # for n in m.userpermissions:
        #     perms.append(n.perm_name)
        #
        # user.__setitem__('perms', perms)

        users_list.append(user)
        user = {}
        # perms = []
    return {'users': users_list, 'title': 'Users'}


async def user_delete(request):
    user_id = request.match_info['id']

    q = User.delete().where(User.id == user_id)
    q.execute()
    raise web.HTTPFound('/users')


@aiohttp_jinja2.template('user_edit.html')
async def user_edit(request):
    user_id = request.match_info['id']
    user = User.get(User.id == user_id)
    perms = [{'perm_id': '', 'perm_name': ''}, {'perm_id': '', 'perm_name': ''}]
    user_selected = {}

    user_selected.__setitem__('id', user.id)
    user_selected.__setitem__('fname', user.fname)
    user_selected.__setitem__('lname', user.lname)
    user_selected.__setitem__('email', user.email)
    user_selected.__setitem__('disabled', user.disabled)
    user_selected.__setitem__('superuser', user.is_superuser)

    i = 0
    if user.userpermissions.count() > 0:
        for p in user.userpermissions:
            # perms.append()
            if i == 3:
                break
            perms.__setitem__(i, {'perm_id': p.perm_id.id, 'perm_name': p.perm_id.name})
            # perms.append({'perm_id': p.perm_id.id, 'perm_name': p.perm_id.name})
            i = i + 1

    user_selected.__setitem__('user_perms', perms)

    permissions = Permissions.select()
    perm_list = []
    for pm in permissions:
        perm_list.append({'id': pm.id, 'name': pm.name})

    # print(user_selected)
    # print(perm_list)
    return {'user': user_selected, 'perm_list': perm_list, 'title': 'User Edit'}


async def user_edit_post(request):
    data = await request.post()
    # print('register')
    # for key in data.keys():
    #     print(key + ': ' + data[key])

    permissions = []

    if 'user_id' and 'fname' and 'lname' and 'email' and 'disabled' and 'superuser' in data:

        user_id = data['user_id']

        if 'public' in data:
            permissions.append({'user_id': user_id, 'perm_id': data['public']})
        if 'protected' in data:
            permissions.append({'user_id': user_id, 'perm_id': data['protected']})

        if permissions.__len__() > 0:
            UserPermissions.delete().where(UserPermissions.user_id == user_id).execute()

        if data['disabled'] == 'False':
            disabled = False
        else:
            disabled = True

        if data['superuser'] == 'False':
            superuser = False
        else:
            superuser = True

        UserPermissions.insert_many(permissions).execute()
        User.update(fname=data['fname'], lname=data['lname'], email=data['email'], is_superuser=superuser,
                    disabled=disabled).where(User.id == user_id).execute()

        raise web.HTTPFound('/users')

    else:

        permissions = Permissions.select()
        perm_list = []
        for pm in permissions:
            perm_list.append({'id': pm.id, 'name': pm.name})

        response = aiohttp_jinja2.render_template('user_edit.html', request, {'user': data, 'perm_list': perm_list})
        # response.headers['Content-Language'] = 'en'
        return response


@aiohttp_jinja2.template('login.html')
async def login(request):
    return {'title': 'Login'}


@aiohttp_jinja2.template('login.html')
async def login_post(request):
    return {}


@aiohttp_jinja2.template('register.html')
async def register(request):
    # token = await aiohttp_csrf.generate_token(request)
    # csrf = {'field_name': FORM_FIELD_NAME, 'token': token}
    return {'title': 'Register'}


async def register_post(request):
    data = await request.post()
    # print('register')
    # for key in data.keys():
    #     print(key + ': ' + data[key])

    try:
        user = User.create(fname=data['firstname'], lname=data['lastname'], email=data['email'],
                           passwd=generate_password_hash(data['password']),
                           is_superuser=0, disabled=0)
        UserPermissions.create(user_id=user.id, perm_id=Permissions.get(Permissions.name == 'public'))

    except IntegrityError as error:
        print(error.__context__)
        # peewee.IntegrityError: UNIQUE constraint failed: user.email

    raise web.HTTPFound('/users')


@aiohttp_jinja2.template('reset_password.html')
async def reset_password(request):
    user_id = request.match_info['id']
    return {'user_id': user_id, 'title': 'Reset Password'}


async def reset_password_post(request):
    data = await request.post()
    # print('register')
    # for key in data.keys():
    #     print(key + ': ' + data[key])

    if 'confirm_password' and 'password' and 'user_id' in data:
        if data['confirm_password'] == data['password']:
            User.update(passwd=generate_password_hash(data['password'])).where(User.id == data['user_id']).execute()
            # print('updated')

    raise web.HTTPFound('/users')


@aiohttp_jinja2.template('dashboard.html')
async def dashboard(request):
    counts = []

    # Campaign count
    camp_count = Campaign.select().count()
    # Agent count
    agent_count = Agent.select().count()
    # Technique count
    tech_count = Technique.select().count()
    # User count
    user_count = User.select().count()

    # Percentage techniques assigned and executed
    exec3 = AgentTechnique.select().where(AgentTechnique.executed.is_null(False))
    exec4 = AgentTechnique.select().where(AgentTechnique.executed.is_null(True))

    percent_tech_executed = int((exec3.count() / (exec4.count() + exec3.count())) * 100)

    # Number of techniques executed
    # cumulative_tech_execution = AgentTechnique.select().where(AgentTechnique.executed.is_null(False)).count()

    counts.append(camp_count)  # 0
    counts.append(agent_count)  # 1
    counts.append(tech_count)  # 2
    counts.append(user_count)  # 3
    counts.append(percent_tech_executed)  # 4
    # counts.append(cumulative_tech_execution)

    graph = []

    camp_month_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # Number of campaigns per month
    query6 = Campaign.select(Campaign.id, Campaign.created_date.month.alias('month'),
                             fn.Count(Campaign.id).alias('count')).group_by(Campaign.created_date.month)

    for q in query6:
        # Array index begin from 0
        camp_month_count.__setitem__(q.month - 1, q.count)

    # Number of agents per month
    agent_month_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    query5 = Agent.select(Agent.id, Agent.initial_contact.month.alias('month'),
                          fn.Count(Agent.id).alias('count')).group_by(Agent.initial_contact.month)

    for q1 in query5:
        # Array index begin from 0
        agent_month_count.__setitem__(q1.month - 1, q1.count)

    # Number of techniques executed per month
    query6 = AgentTechnique.select(AgentTechnique.technique_id, AgentTechnique.executed.month.alias('month'),
                                   fn.Count(AgentTechnique.technique_id).alias('count')).group_by(
        AgentTechnique.executed.month) \
        .having(AgentTechnique.executed.is_null(False))

    tech_month_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for t in query6:
        # Array index begin from 0
        tech_month_count.__setitem__(t.month - 1, t.count)

    graph.append(camp_month_count)
    graph.append(agent_month_count)
    graph.append(tech_month_count)

    # Weekly Technique Execution
    weekly = []
    stop = datetime.datetime.now()
    difference = datetime.timedelta(days=7)
    start = stop - difference
    exec_in_week = 0

    res = AgentTechnique.select(AgentTechnique.technique_id,
                                AgentTechnique.executed,
                                fn.Count(AgentTechnique.technique_id).alias('count')) \
        .where((start <= AgentTechnique.executed) & (AgentTechnique.executed <= stop)) \
        .group_by(AgentTechnique.executed.day)

    for r in res:
        exec_in_week = exec_in_week + r.count
        weekly.append({'date': r.executed.strftime("%d %b %Y"), 'count': r.count})

    counts.append(exec_in_week)

    return {'counts': counts, 'graph': graph, 'weekly': weekly}


async def create_app():
    app = web.Application()
    app.add_routes([
        web.get('/', index),
        web.get('/dashboard', dashboard, name='dashboard'),
        web.get('/users', users_index, name='users'),
        web.get('/user_delete/{id}', user_delete, name='user_delete'),
        web.get('/user_edit/{id}', user_edit, name='user_edit'),
        web.post('/user_edit_post', user_edit_post, name='user_edit_post'),
        web.get('/reset_password/{id}', reset_password, name='reset_password'),
        web.post('/reset_password_post', reset_password_post, name='reset_password_post'),
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
        web.get('/campaigns', campaign_index, name='campaigns'),
        web.get('/campaign_details/{id}', campaign_details, name='campaign_details'),
        web.post('/campaign_add', campaign_add),
        web.post('/campaign_update', campaign_update),
        web.post('/campaign_delete', campaign_delete),
        web.get('/login', login, name='login'),
        web.post('/login_post', login_post),
        web.get('/register', register, name='register'),
        web.post('/register_post', register_post, name='register_post'),
        web.static('/static/', path=THIS_DIR / 'app/static', show_index=True, append_version=True, name='static'),
        web.static('/downloads/', path=THIS_DIR / 'app/downloads', show_index=True, name='downloads'),
        web.static('/uploads/', path=THIS_DIR / 'app/uploads', show_index=True, name='uploads')
    ])

    load = jinja2.FileSystemLoader(str(THIS_DIR / 'app/templates'))
    aiohttp_jinja2.setup(app, loader=load)
    app['name'] = 'S.T.A.E'

    setup_middleware(app)

    # CSRF CODE 1
    # csrf_policy = aiohttp_csrf.policy.FormPolicy(FORM_FIELD_NAME)
    # csrf_storage = aiohttp_csrf.storage.SessionStorage(SESSION_NAME)
    # aiohttp_csrf.setup(app, policy=csrf_policy, storage=csrf_storage)

    secret_key = b'\xd0\x04)E\x14\x98\xa1~\xecE\xae>(\x1d6\xec\xbfQ\xa4\x19\x0e\xbcre,\xf8\x8f\x84WV.\x8d'
    setup(app, EncryptedCookieStorage(secret_key))

    # CSRF CODE 2
    # app.middlewares.append(aiohttp_csrf.csrf_middleware)

    # HTTPS using Secure Sockets Layer
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile='certificates/stae.crt', keyfile='certificates/stae.key')

    # Stops asyncio warnings because asycio implements its own exception handling. This throws many exceptions
    # that cannot be handled due to this being a development environment.
    logging.getLogger('asyncio').setLevel(logging.CRITICAL)

    # logging.basicConfig(level=logging.INFO)

    # web.run_app(app, host="localhost", port=8080, ssl_context=ssl_context)

    return app

# adev runserver --livereload --debug-toolbar
# app = create_app()
# web.run_app(app, host="localhost", port=8000)
