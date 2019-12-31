import aiohttp_jinja2
from aiohttp import web
from database import *


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


def setup_dashboard_routes(app):
    app.add_routes([
        web.get('/dashboard', dashboard, name='dashboard'),
    ])
