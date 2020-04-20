import datetime
import random
import string
import unittest
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
# noinspection PyUnresolvedReferences
from server import create_app
# noinspection PyUnresolvedReferences
from server import create_app_two
# noinspection PyUnresolvedReferences
from db.database import *

data = {'email': 'admin@thremulate.com', 'password': 'thremulate'}
agent_id = random.randrange(10000, 99999)
hostname = ''.join(random.choice(string.ascii_lowercase) for _ in range(7))
agent_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(7))
agent_adv_id = Adversary.get(Adversary.name == 'Unknown')
agent_registration = {'id': agent_id,
                      'hostname': hostname,
                      'platform': 'windows',
                      'plat_version': '10.10.10',
                      'username': 'Administrator'}


def add_agent_to_db():
    agent_registration.__setitem__('adversary', agent_adv_id)
    agent_registration.__setitem__('name', agent_name)
    Agent.insert_many(agent_registration).execute()


def delete_agent_from_db():
    Agent.delete().where(Agent.id == agent_id).execute()


class ThremulateTests(AioHTTPTestCase):

    async def get_application(self):
        app = await create_app()
        return app

    @unittest_run_loop
    async def test_index(self):
        resp = await self.client.request("GET", "/")
        self.assertTrue(resp.status == 200, msg="Failed to access /")
        text = await resp.text()
        self.assertTrue("Thremulate" in text, msg="Failed to access / template")

    @unittest_run_loop
    async def test_login_get(self):
        resp = await self.client.request("GET", "/login")
        self.assertTrue(resp.status == 200, msg="Failed to access /login")

    @unittest_run_loop
    async def test_login_post(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login_post")

    @unittest_run_loop
    async def test_logout(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        resp_two = await self.client.request("GET", "/logout")
        self.assertTrue(resp_two.status == 200, msg="Failed to access /logout. Received status code {0}"
                        .format(resp_two.status))

    @unittest_run_loop
    async def test_register(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        resp_two = await self.client.request("GET", "/register")
        self.assertTrue(resp_two.status == 200, msg="Failed to access /register. Received status code {0}"
                        .format(resp_two.status))

    @unittest_run_loop
    async def test_register_post(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        register_one = {'firstname': 'Operator', 'lastname': 'One', 'email': 'opone@thremulate.com',
                        'password': data['password'], 'confirm_password': data['password'],
                        'old_password': data['password']}
        resp_two = await self.client.request("POST", "/register_post", data=register_one)
        self.assertTrue(resp_two.status == 200,
                        msg="Failed to access /change_password_post. Received status code {0}"
                        .format(resp_two.status))

        resp_three = await self.client.request("POST", "/register_post", data=register_one)
        text = await resp_three.text()
        self.assertTrue(resp_three.status == 200,
                        msg="Failed to access /change_password_post. Received status code {0}"
                        .format(resp_three.status))
        self.assertTrue('Email already in use' in text,
                        msg="Email already in use message not shown")

    @unittest_run_loop
    async def test_force_reset_password(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        resp_two = await self.client.request("GET", "/force_reset_password")
        self.assertTrue(resp_two.status == 200, msg="Failed to access /force_reset_password. Received status code {0}"
                        .format(resp_two.status))

    @unittest_run_loop
    async def test_home(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to login")
        resp_two = await self.client.request("GET", "/home")
        self.assertTrue(resp_two.status == 200, msg="Failed to access /home. Received status code {0}"
                        .format(resp_two.status))

    @unittest_run_loop
    async def test_dashboard(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        resp_two = await self.client.request("GET", "/dashboard")
        self.assertTrue(resp_two.status == 200, msg="Failed to access /dashboard. Received status code {0}"
                        .format(resp_two.status))


class UserManagement(AioHTTPTestCase):
    async def get_application(self):
        app = await create_app()
        return app

    @unittest_run_loop
    async def test_user_index(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        resp_two = await self.client.request("GET", "/users")
        self.assertTrue(resp_two.status == 200, msg="Failed to access /users. Received status code {0}"
                        .format(resp_two.status))

    @unittest_run_loop
    async def test_user_profile(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        resp_two = await self.client.request("GET", "/user_profile")
        self.assertTrue(resp_two.status == 200, msg="Failed to access /user_profile. Received status code {0}"
                        .format(resp_two.status))

    @unittest_run_loop
    async def test_user_edit(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        resp_two = await self.client.request("GET", "/user_edit")
        self.assertTrue(resp_two.status == 200, msg="Failed to access /user_edit. Received status code {0}"
                        .format(resp_two.status))

    @unittest_run_loop
    async def test_change_password(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        resp_two = await self.client.request("GET", "/change_password")
        self.assertTrue(resp_two.status == 200, msg="Failed to access /change_password. Received status code {0}"
                        .format(resp_two.status))

    @unittest_run_loop
    async def test_change_password_post(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        change_pass = {'password': data['password'], 'confirm_password': data['password'],
                       'old_password': data['password']}
        resp_two = await self.client.request("POST", "/change_password_post", data=change_pass)
        self.assertTrue(resp_two.status == 200, msg="Failed to access /change_password_post. Received status code {0}"
                        .format(resp_two.status))

        change_pass_two = {'password': 'thremulatethremulate', 'confirm_password': data['password'],
                           'old_password': data['password']}
        resp_three = await self.client.request("POST", "/change_password_post", data=change_pass_two)
        text = await resp_three.text()
        self.assertTrue(resp_three.status == 200, msg="Failed to access /change_password_post. Received status code {0}"
                        .format(resp_three.status))
        self.assertTrue('New and Confirm New password did not match' in text,
                        msg="Passwords did not match message not shown")

    @unittest_run_loop
    async def test_user_edit_post(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        change_pass = {'fname': 'Admin', 'lname': 'Admin',
                       'email': data['email']}
        resp_two = await self.client.request("POST", "/user_edit_post", data=change_pass)
        self.assertTrue(resp_two.status == 200, msg="Failed to access /user_edit_post. Received status code {0}"
                        .format(resp_two.status))


class AdversaryTests(AioHTTPTestCase):
    async def get_application(self):
        app = await create_app()
        return app

    @unittest_run_loop
    async def test_adversaries_index(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        resp_two = await self.client.request("GET", "/adversaries")
        self.assertTrue(resp_two.status == 200, msg="Failed to access /adversaries. Received status code {0}"
                        .format(resp_two.status))

    @unittest_run_loop
    async def test_adversary_details(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        resp_two = await self.client.request("GET", "/adversary_details/1")
        self.assertTrue(resp_two.status == 200, msg="Failed to access /adversary_details/1. Received status code {0}"
                        .format(resp_two.status))

    @unittest_run_loop
    async def test_adversary_add(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        adversary_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(7))
        resp_two = await self.client.request("POST", "/adversary_add", data={'addName': adversary_name})
        self.assertTrue(resp_two.status == 200, msg="Failed to access /adversary_add. Received status code {0}"
                        .format(resp_two.status))
        text = await resp_two.text()
        self.assertTrue(text != 'exists', msg="Adversary already exists")
        Adversary.delete().where(Adversary.name == adversary_name).execute()

    @unittest_run_loop
    async def test_adversary_update(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        adversary_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(7))
        adv_id = Adversary.create(name=adversary_name)
        resp_two = await self.client.request("POST", "/adversary_update", data={'id': adv_id, 'name': adversary_name})
        self.assertTrue(resp_two.status == 200, msg="Failed to access /adversary_update. Received status code {0}"
                        .format(resp_two.status))
        Adversary.delete().where(Adversary.name == adversary_name).execute()

    @unittest_run_loop
    async def test_adversary_delete(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        adversary_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(7))
        adv_id = Adversary.create(name=adversary_name)
        print(adv_id)
        resp_two = await self.client.request("POST", "/adversary_delete", data={'id': adv_id})
        self.assertTrue(resp_two.status == 200, msg="Failed to access /adversary_delete. Received status code {0}"
                        .format(resp_two.status))


# We need to assign Agent technique test before the Agent does anything. AgentAssignTechnique and AgentOutput
# classes represent the edge case
# It should run before other tests yet unittest run tests in alphabetical order hence the strange name.
class AAgentInitialization(AioHTTPTestCase):
    async def get_application(self):
        app = await create_app_two()
        return app

    @unittest_run_loop
    async def test_agent_register(self):
        resp = await self.client.request("POST", "register_agent", data=agent_registration)
        self.assertTrue(resp.status == 200, msg="Failed to access /register_agent. Received status code {0}"
                        .format(resp.status))
        text = await resp.text()
        self.assertTrue('Agent has registered' in text, msg="Server failed to register agent. Agent may already be "
                                                            "registered")
        Agent.delete().where(Agent.id == agent_id).execute()


# We need to assign Agent technique test before the Agent does anything. AgentAssignTechnique and AgentOutput
# classes represent the edge case
class ABgentAssignTechnique(AioHTTPTestCase):
    async def get_application(self):
        app = await create_app()
        return app

    @unittest_run_loop
    async def test_assign_tasks(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        add_agent_to_db()
        resp_two = await self.client.request("GET", "/assign_tasks/%s" % agent_id)
        self.assertTrue(resp_two.status == 200, msg="Failed to access /assign_tasks/{0}. Received status code {1}"
                        .format(agent_id, resp_two.status))
        delete_agent_from_db()

    @unittest_run_loop
    async def test_customize_technique(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        add_agent_to_db()
        resp_two = await self.client.request("GET", "/customize_technique/?agent_id=%s&tech_id=1002" % agent_id)
        self.assertTrue(resp_two.status == 200, msg="Failed to access /customize_technique. Received status code {0}"
                        .format(resp_two.status))
        delete_agent_from_db()

    @unittest_run_loop
    async def test_customize_technique_post(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        custom_tech = {'agent_id': agent_id, 'tech_id': 1002, 'test_id': 0, 'input_path': '%USERPROFILE%',
                       'output_file': '%USERPROFILE%\\data.rar'}
        resp_two = await self.client.request("POST", "/customize_technique_post", data=custom_tech)
        self.assertTrue(resp_two.status == 200,
                        msg="Failed to access /customize_technique_post. Received status code {0}"
                        .format(resp_two.status))
        text = await resp_two.text()
        self.assertTrue('Assigned' in text, msg="Failed to assign technique")


class AgentCommunicationLines(AioHTTPTestCase):
    async def get_application(self):
        app = await create_app_two()
        return app

    @unittest_run_loop
    async def test_agent_tasks(self):
        resp = await self.client.request("GET", "/agent_tasks/%s" % agent_id)
        self.assertTrue(resp.status == 200, msg="Failed to access agent_tasks")
        text = await resp.text()
        self.assertTrue("++" in text, msg="Failed to get techniques from server")

    @unittest_run_loop
    async def test_agent_techniques(self):
        resp = await self.client.request("GET", "/agent_techniques/{0}".format(agent_id))
        self.assertTrue(resp.status == 200, msg="Failed to access /agent_techniques/{0}".format(agent_id))

    @unittest_run_loop
    async def test_agent_output(self):
        agent_output = {'id': agent_id, 'tech': '1002:0',
                        'executed': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'output': 'Success--Agent output'}
        resp = await self.client.request("POST", "agent_output", data=agent_output)
        self.assertTrue(resp.status == 200, msg="Failed to access /agent_output. Received status code {0}"
                        .format(resp.status))
        text = await resp.text()
        self.assertTrue('success' in text, msg="Server failed to store agent output.")


class AgentRoutes(AioHTTPTestCase):
    async def get_application(self):
        app = await create_app()
        return app

    @unittest_run_loop
    async def test_agent_index(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        resp_two = await self.client.request("GET", "/agents")
        self.assertTrue(resp_two.status == 200, msg="Failed to access /agents. Received status code {0}"
                        .format(resp_two.status))
        text = await resp_two.text()
        self.assertTrue("Agents" in text, msg="Failed to access /agents template")

    @unittest_run_loop
    async def test_agent_details(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        resp_two = await self.client.request("GET", "/agent_details/%s" % agent_id)
        self.assertTrue(resp_two.status == 200, msg="Failed to access /agent_details. Received status code {0}"
                        .format(resp_two.status))
        text = await resp_two.text()
        self.assertTrue("Agent Details" in text, msg="Failed to access /agent_details template.")

    @unittest_run_loop
    async def test_agent_edit(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        resp_two = await self.client.request("GET", "/agent_edit/%s" % agent_id)
        self.assertTrue(resp_two.status == 200, msg="Failed to access /agent_edit. Received status code {0}"
                        .format(resp_two.status))
        text = await resp_two.text()
        self.assertTrue("Update Agent" in text, msg="Failed to access /agent_edit template")

    @unittest_run_loop
    async def test_agent_edit_post(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        agent_edit = {'agent_id': agent_id, 'name': 'Disk kill', 'adversary': 1, 'kill_date': ''}
        resp_two = await self.client.request("POST", "/agent_edit_post", data=agent_edit)
        self.assertTrue(resp_two.status == 200, msg="Failed to access /agent_edit_post. Received status code {0}"
                        .format(resp_two.status))

    @unittest_run_loop
    async def test_delete_tech_output(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        delete_tech_output = {'agent_id': agent_id, 'tech_id': 1002, 'test_num': 0}
        resp_two = await self.client.request("POST", "/delete_tech_output", data=delete_tech_output)
        self.assertTrue(resp_two.status == 200, msg="Failed to access /delete_tech_output. Received status code {0}"
                        .format(resp_two.status))

    @unittest_run_loop
    async def test_delete_tech_output(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        delete_tech = {'agent_id': agent_id, 'tech_id': 1002, 'test_num': 0}
        resp_two = await self.client.request("POST", "/delete_tech_assignment", data=delete_tech)
        self.assertTrue(resp_two.status == 200, msg="Failed to access /delete_tech_assignment. Received status code {0}"
                        .format(resp_two.status))

    @unittest_run_loop
    async def test_delete_agent(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        delete_agent = {'agent_id': agent_id}
        resp_two = await self.client.request("POST", "/agent_delete_post", data=delete_agent)
        self.assertTrue(resp_two.status == 200, msg="Failed to access /agent_delete_post. Received status code {0}"
                        .format(resp_two.status))
        text = await resp_two.text()
        self.assertTrue("success" in text, msg="Failed to delete agent")


if __name__ == '__main__':
    unittest.main()
