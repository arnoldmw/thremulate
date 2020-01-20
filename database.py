import datetime
import uuid

import bcrypt
from playhouse.migrate import *
# noinspection PyUnresolvedReferences
from art.run_atomics import get_all_techniques

db = SqliteDatabase('db/adversary.db', pragmas={'foreign_keys': 1})


class BaseModel(Model):
    class Meta:
        database = db


class Adversary(BaseModel):
    name = CharField(unique=True)
    created_date = DateTimeField(default=datetime.datetime.now)
    updated_date = DateTimeField(default=datetime.datetime.now)


class Agent(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField(unique=True, null=True)
    hostname = CharField(max_length=30, null=True)
    username = CharField(max_length=30, null=True)
    platform = CharField(max_length=20, null=True)
    plat_version = CharField(max_length=20, null=True)
    domain = CharField(max_length=20, null=True)
    initial_contact = DateTimeField(default=datetime.datetime.now, null=True)
    last_contact = DateTimeField(default=datetime.datetime.now, null=True)
    adversary = ForeignKeyField(Adversary, backref='agents', null=True)


class Technique(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=30)
    parameters = CharField(max_length=30, null=True)


class AgentTechnique(BaseModel):
    technique_id = ForeignKeyField(Technique)
    agent_id = ForeignKeyField(Agent, backref='techniques')
    test_num = IntegerField()
    output = TextField(null=True)
    result = BooleanField(null=True)
    executed = DateTimeField(null=True)

    class Meta:
        primary_key = CompositeKey('technique_id', 'agent_id', 'test_num')


class Tactic(BaseModel):
    name = CharField(max_length=30)


class TacticTechnique(BaseModel):
    tactic = ForeignKeyField(Tactic)
    technique = ForeignKeyField(Technique)

    class Meta:
        primary_key = CompositeKey('tactic', 'technique')


class Parameter(BaseModel):
    technique_id = ForeignKeyField(Technique, on_delete='CASCADE')
    agent_id = ForeignKeyField(Agent, on_delete='CASCADE')
    test_num = IntegerField()
    param_name = CharField(max_length=30)
    param_value = CharField(max_length=50)


class User(BaseModel):
    id = UUIDField(primary_key=True)
    fname = CharField(max_length=25)
    lname = CharField(max_length=255)
    email = CharField(unique=True, index=True)
    passwd = CharField(max_length=255)
    is_superuser = BooleanField(default=False)
    disabled = BooleanField(default=False)
    reset_pass = BooleanField(default=False)


class Permissions(BaseModel):
    name = CharField(max_length=255, index=True)


class UserPermissions(BaseModel):
    user_id = ForeignKeyField(User, on_delete='CASCADE', backref='userpermissions')
    perm_id = ForeignKeyField(Permissions)


def generate_password_hash(password):
    password_bin = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bin, bcrypt.gensalt())
    return hashed.decode('utf-8')


def migrate():
    db.connect()
    # db.create_tables([Parameter])
    # db.create_tables([TacticTechnique])

    # db.drop_tables([Adversary, Agent, Technique, AgentTechnique, Tactic, TacticTechnique])
    # db.create_tables([Adversary, Agent, Technique, AgentTechnique, Tactic, TacticTechnique])

    # camp = Adversary(name='Fin7', created_date=datetime.datetime.now, updated_date=datetime.datetime.now)
    # camp.save()

    # Adversary.create(name='Fin7')
    # Adversary.create(name='Cobalt')

    # Agent.create(id=5, name='Hunter', os_name='Windows 10', os_version='10.4.5', product_id='5FF',
    #              domain='home.local', adversary=Adversary.get_by_id(1))

    # Agent.create(id=5, name='Hunter', os_name='Windows 10', os_version='10.4.5', product_id='5FF',
    #              domain='home.local', adversary=Adversary.get(Adversary.name == 'Fin7'))
    # Agent.create(id=4, name='Sniffer', os_name='Windows 7', os_version='7.3.4', product_id='6KKL', domain='work.com',
    #              adversary=Adversary.get(Adversary.name == 'Cobalt'))
    #
    # Technique.create(id=1057, name='Process Discovery')
    # Technique.create(id=1124, name='System Time Discovery')
    # Technique.create(id=1012, name='Query Registry')

    # reg query HKLM\Software\Microsoft\Windows\CurrentVersion\Run
    output1 = '''
    Image Name                     PID Session Name        Session#    Mem Usage
    ========================= ======== ================ =========== ============
    System Idle Process              0 Services                   0          8 K
    System                           4 Services                   0      1,708 K
    Registry                        96 Services                   0      9,080 K
    smss.exe                       448 Services                   0        704 K
    csrss.exe                      712 Services                   0      4,324 K
    wininit.exe                    776 Services                   0      5,084 K
    csrss.exe                      792 Console                    1      4,584 K
    services.exe                   836 Services                   0      7,684 K
    '''

    output2 = '''
    SecurityHealth    REG_EXPAND_SZ    %ProgramFiles%\Windows Defender\MSASCuiL.exe
    AvastUI.exe    REG_SZ    "C:\Program Files\AVAST Software\Avast\AvLaunch.exe" /gui
    RtHDVCpl    REG_SZ    C:\Program Files\Realtek\Audio\HDA\RAVCpl64.exe -s
    '''

    # AgentTechnique.create(technique_id=Technique.get_by_id(1124), agent_id=4, output=output1, result=1)
    # AgentTechnique.create(technique_id=Technique.get_by_id(1012), agent_id=4, output=output2, result=1)
    #
    # Tactic.create(name='Persistence')
    # Tactic.create(name='Discovery')
    #
    # TacticTechnique.create(tactic_id=1, technique_id=1012)
    # TacticTechnique.create(tactic_id=2, technique_id=1012)

    # data = get_all_techniques()
    # Technique.insert_many(data).execute()

    # data = [
    #     {'id': 1, 'name': 'Initial Access'},
    #     {'id': 2, 'name': 'Execution'},
    #     {'id': 3, 'name': 'Persistence'},
    #     {'id': 4, 'name': 'Privilege Escalation'},
    #     {'id': 5, 'name': 'Defense Evasion'},
    #     {'id': 6, 'name': 'Credential Access'},
    #     {'id': 7, 'name': 'Discovery'},
    #     {'id': 8, 'name': 'Lateral Movement'},
    #     {'id': 9, 'name': 'Collection'},
    #     {'id': 10, 'name': 'Exfiltration'},
    #     {'id': 11, 'name': 'Command and Control'},
    #     {'id': 40, 'name': 'Impact'},
    # ]
    # Tactic.insert_many(data).execute()

    # ag = Agent.get(Agent.id == 5)
    # print(ag.platform)

    # db.connect()
    # db.drop_tables([Permissions, UserPermissions])
    db.create_tables([UserPermissions, Permissions])
    # data_source1 = [
    #     {'fname': 'Admin', 'lname': 'Ad', 'email': 'admin@stae.com',
    #      'passwd': generate_password_hash('admin'), 'is_superuser': '1', 'disabled': '0'},
    #     {'fname': 'Moderator', 'lname': 'Mo', 'email': 'moderator@stae.com',
    #      'passwd': generate_password_hash('moderator'), 'is_superuser': '0', 'disabled': '0'},
    #     {'fname': 'User', 'lname': 'Us', 'email': 'user@stae.com',
    #      'passwd': generate_password_hash('user'), 'is_superuser': '0', 'disabled': '0'}
    # ]

    data_source2 = [
        {'name': 'public'},
        {'name': 'protected'}
    ]

    data_source3 = [
        {'user_id': 2, 'perm_id': 2},
        {'user_id': 2, 'perm_id': 1},
        {'user_id': 3, 'perm_id': 1}
    ]

    # Permissions.insert_many(data_source2).execute()
    # UserPermissions.insert_many(data_source3).execute()


if __name__ == '__main__':
    print('Main running')

    # db.drop_tables([User])
    # db.create_tables([User])

    # data_source = [
    #     {'id': uuid.uuid4(), 'fname': 'Admin', 'lname': 'Ad', 'email': 'admin@thremulate.com',
    #      'passwd': generate_password_hash('admin'), 'is_superuser': '1', 'disabled': '0'},
    #     {'id': uuid.uuid4(), 'fname': 'Moderator', 'lname': 'Mo', 'email': 'moderator@thremulate.com',
    #      'passwd': generate_password_hash('moderator'), 'is_superuser': '0', 'disabled': '0'},
    #     {'id': uuid.uuid4(), 'fname': 'User', 'lname': 'Us', 'email': 'user@thremulate.com',
    #      'passwd': generate_password_hash('user'), 'is_superuser': '0', 'disabled': '0'}
    # ]
    # User.insert_many(data_source).execute()

    # user = User.get(User.fname == 'Admin')
    # print(user.reset_pass)
    #
    # q = AgentTechnique.delete() \
    #     .where((AgentTechnique.agent_id == 5) & (AgentTechnique.technique_id == 1082)
    #            & (AgentTechnique.test_num == 0))
    # print(q)

    query = Adversary.select()
    adversaries = []
    for adv in query:
        adversaries.append({'id': adv.id, 'name': adv.name, 'created': adv.created_date, 'updated': adv.updated_date,
                            'no_of_agents': adv.agents.count()})
        # print(adv.id, adv.name, adv.created_date, adv.updated_date, adv.agents.count())
    print(adversaries)