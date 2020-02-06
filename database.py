import datetime
import uuid
from pathlib import Path

import bcrypt
# noinspection PyUnresolvedReferences
from art.run_atomics import techniques_for_db
from playhouse.migrate import *

THIS_DIR = Path(__file__).parent
db = SqliteDatabase(THIS_DIR / 'db/adversary.db', pragmas={'foreign_keys': 1})


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
    domain = CharField(max_length=30, null=True)
    initial_contact = DateTimeField(default=datetime.datetime.now, null=True)
    kill_date = DateTimeField(null=True)
    last_contact = DateTimeField(default=datetime.datetime.now, null=True)
    adversary = ForeignKeyField(Adversary, backref='agents', null=True)


class Technique(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=30)


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
    id = UUIDField(primary_key=True, default=uuid.uuid4())
    fname = CharField(max_length=25)
    lname = CharField(max_length=255)
    email = CharField(unique=True, index=True)
    passwd = CharField(max_length=255)
    is_superuser = BooleanField(default=False)
    disabled = BooleanField(default=False)
    reset_pass = BooleanField(default=False)
    lockout_count = IntegerField(default=0)


class Permissions(BaseModel):
    name = CharField(max_length=255, index=True)


class UserPermissions(BaseModel):
    user_id = ForeignKeyField(User, on_delete='CASCADE', backref='userpermissions')
    perm_id = ForeignKeyField(Permissions)


def generate_password_hash(password):
    password_bin = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bin, bcrypt.gensalt())
    return hashed.decode('utf-8')


def init_db():
    db.connect()
    print('[+] Setting up default database')

    # db.drop_tables([Adversary, Agent, Technique, AgentTechnique, Tactic, TacticTechnique,
    #                 Parameter, User, Permissions, UserPermissions])
    # print('[+] All tables dropped')
    db.create_tables([Adversary, Agent, Technique, AgentTechnique, Tactic, TacticTechnique,
                      Parameter, User, Permissions, UserPermissions])
    print('[+] All tables created')

    # Adversary table
    print('[+] Adding Adversary records')
    adversary_data = [
        {'name': 'Unknown'},
        {'name': 'Fin7'},
        {'name': 'Lazarus'}
    ]
    Adversary.insert_many(adversary_data).execute()

    # Agent table
    print('[+] Adding Agent records')
    Agent.create(id=1, name='Hunter', platform='windows', plat_version='10.4.5', username='JohnDoe',
                 domain='home.local', hostname='Johnie', adversary=Adversary.get(Adversary.name == 'Unknown'))

    # Tactics table
    print('[+] Adding Tactics records')
    tactics_data = [
        {'id': 1, 'name': 'Initial Access'},
        {'id': 2, 'name': 'Execution'},
        {'id': 3, 'name': 'Persistence'},
        {'id': 4, 'name': 'Privilege Escalation'},
        {'id': 5, 'name': 'Defense Evasion'},
        {'id': 6, 'name': 'Credential Access'},
        {'id': 7, 'name': 'Discovery'},
        {'id': 8, 'name': 'Lateral Movement'},
        {'id': 9, 'name': 'Collection'},
        {'id': 10, 'name': 'Exfiltration'},
        {'id': 11, 'name': 'Command and Control'},
        {'id': 40, 'name': 'Impact'},
    ]
    Tactic.insert_many(tactics_data).execute()

    # Technique table
    tech_table = techniques_for_db()
    for t in tech_table:
        try:
            Technique.get(Technique.id == t['id'])
        except Technique.DoesNotExist:
            Technique.create(id=t['id'], name=t['name'])
            pass

    # TODO: TacticTechnique table

    # User table
    print('[+] Adding User records')
    user_ids = {'admin': uuid.uuid4(), 'userone': uuid.uuid4(), 'usertwo': uuid.uuid4()}
    user_data = [
        {'id': user_ids['admin'], 'fname': 'Admin', 'lname': 'Admin', 'email': 'admin@thremulate.com',
         'passwd': generate_password_hash('thremulate'), 'is_superuser': True, 'disabled': False},
        {'id': user_ids['userone'], 'fname': 'UserOne', 'lname': 'UsOne', 'email': 'uone@thremulate.com',
         'passwd': generate_password_hash('thremulate'), 'is_superuser': False, 'disabled': False},
        {'id': user_ids['usertwo'], 'fname': 'UserTwo', 'lname': 'UsTwo', 'email': 'utwo@thremulate.com',
         'passwd': generate_password_hash('thremulate'), 'is_superuser': False, 'disabled': False}
    ]
    User.insert_many(user_data).execute()

    # Permissions table
    print('[+] Adding Permissions records')
    permission_data = [
        {'name': 'public'},
        {'name': 'protected'}
    ]
    Permissions.insert_many(permission_data).execute()

    # UserPermissions table
    print('[+] Adding UserPermissions records')
    user_permissions_data = [
        {'user_id': user_ids['userone'], 'perm_id': Permissions.get(Permissions.name == 'public')},
        {'user_id': user_ids['usertwo'], 'perm_id': Permissions.get(Permissions.name == 'public')},
    ]

    UserPermissions.insert_many(user_permissions_data).execute()
    print('[+] Finished setting up default database')
