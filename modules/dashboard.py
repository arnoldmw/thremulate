#      Thremulate executes Network Adversary Post Compromise Behavior.
#      Copyright (C) 2021  Mwesigwa Arnold
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

import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import check_authorized
from aiohttp_session import get_session
from db.database import *


@aiohttp_jinja2.template('dashboard/dashboard.html')
async def dashboard(request):
    await check_authorized(request)
    counts = []

    # Adversary count
    camp_count = Adversary.select().count()
    # Agent count
    agent_count = Agent.select().count()
    # Technique count
    tech_count = Technique.select().count()
    # User count
    user_count = User.select().count()

    # Percentage techniques assigned and executed
    exec3 = AgentTechnique.select().where(AgentTechnique.executed.is_null(False)).count()
    exec4 = AgentTechnique.select().where(AgentTechnique.executed.is_null(True)).count()

    if exec3 != 0:
        percent_tech_executed = int((exec3 / (exec4 + exec3)) * 100)
    else:
        percent_tech_executed = 0

    # Number of distinct or unique techniques executed
    unique_tech_execution_count = AgentTechnique.select(AgentTechnique.technique_id) \
        .where(AgentTechnique.executed.is_null(False)).distinct().count()

    counts.append(camp_count)  # 0
    counts.append(agent_count)  # 1
    counts.append(tech_count)  # 2
    counts.append(user_count)  # 3
    counts.append(percent_tech_executed)  # 4
    counts.append(unique_tech_execution_count)  # 5

    graph = []

    camp_month_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # Number of adversaries per month
    query6 = Adversary.select(Adversary.id, Adversary.created_date.month.alias('month'),
                              fn.Count(Adversary.id).alias('count')).group_by(Adversary.created_date.month)

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

    top_active_agents = most_active_agents()
    timeline = timeline_data()
    platform_execution = platform_exec_count()

    session = await get_session(request)
    current_user = session['current_user']
    return {'current_user': current_user, 'counts': counts, 'graph': graph, 'weekly': weekly,
            'top_active_agents': top_active_agents, 'timeline': timeline, 'plat_exec': platform_execution}


def most_active_agents():
    most_active_agents_in_db = []
    number_executed = fn.Count(AgentTechnique.executed)
    query7 = AgentTechnique.select(AgentTechnique.agent_id,
                                   number_executed.alias('count'), Agent.name, Agent.platform) \
        .join(Agent) \
        .group_by(AgentTechnique.agent_id) \
        .having(AgentTechnique.executed.is_null(False)).order_by(number_executed.desc()).limit(5).dicts()

    for a in query7:
        most_active_agents_in_db.append(a)

    return most_active_agents_in_db


def timeline_data():
    t_data = []
    query = AgentTechnique.select(AgentTechnique.executed, fn.Count(AgentTechnique.agent_id).alias('count')) \
        .group_by(AgentTechnique.executed.day).having(AgentTechnique.executed.is_null(False)) \
        .order_by(AgentTechnique.executed.desc()).limit(6).dicts()

    for n in query:
        t_data.append(n)

    return t_data


def platform_exec_count():
    plat_execution = AgentTechnique.select(Agent.platform, AgentTechnique.agent_id,
                                           fn.Count(AgentTechnique.technique_id).alias('count')).join(Agent) \
        .group_by(AgentTechnique.agent_id).having(AgentTechnique.executed.is_null(False)).dicts()

    plat_exec = {'windows': 0, 'linux': 0, 'macos': 0}
    for p in plat_execution:
        if p['platform'] == 'windows':
            plat_exec['windows'] = plat_exec['windows'] + p['count']
        if p['platform'] == 'macos':
            plat_exec['macos'] = plat_exec['macos'] + p['count']
        if p['platform'] == 'linux':
            plat_exec['linux'] = plat_exec['linux'] + p['count']

    return plat_exec


def setup_dashboard_routes(app):
    """
    Adds dashboard route to the application.
    :param app:
    :return: None
    """
    app.add_routes([
        web.get('/dashboard', dashboard, name='dashboard'),
    ])
