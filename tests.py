import datetime
import unittest
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
# noinspection PyUnresolvedReferences
from server import create_app
# noinspection PyUnresolvedReferences
from server import create_app_two

data = {'email': 'admin@thremulate.com', 'password': 'thremulate'}
agent_id = 44444


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
        text = await resp.text()
        self.assertTrue("Dashboard" in text, msg="Failed to access /dashboard template")


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
        resp_two = await self.client.request("POST", "/adversary_add", data={'addName': 'APT4000'})
        self.assertTrue(resp_two.status == 200, msg="Failed to access /adversary_add. Received status code {0}"
                        .format(resp_two.status))
        text = await resp_two.text()
        self.assertTrue(text != 'exists', msg="Adversary already exists")

    @unittest_run_loop
    async def test_adversary_update(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        resp_two = await self.client.request("POST", "/adversary_update", data={'id': 1, 'name': 'APT4444'})
        self.assertTrue(resp_two.status == 200, msg="Failed to access /adversary_update. Received status code {0}"
                        .format(resp_two.status))

    @unittest.skip("Need to handle exception")
    # TODO: Do not attach an agent to it
    @unittest_run_loop
    async def test_adversary_delete(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        resp_two = await self.client.request("POST", "/adversary_delete", data={'id': 1})
        self.assertTrue(resp_two.status == 200, msg="Failed to access /adversary_delete. Received status code {0}"
                        .format(resp_two.status))


class AgentCommunicationLines(AioHTTPTestCase):
    async def get_application(self):
        app = await create_app_two()
        return app

    @unittest_run_loop
    async def test_register(self):
        agent_registration = {'id': agent_id, 'hostname': 'DC01', 'platform': 'windows', 'plat_version': '10.10.10',
                              'username': 'Administrator'}
        resp = await self.client.request("POST", "register_agent", data=agent_registration)
        self.assertTrue(resp.status == 200, msg="Failed to access /register_agent. Received status code {0}"
                        .format(resp.status))
        text = await resp.text()
        self.assertTrue('Agent has registered' in text, msg="Server failed to register agent. Agent may already be "
                                                            "registered")

    # First add agent
    @unittest_run_loop
    async def test_agent_tasks(self):
        resp = await self.client.request("GET", "/agent_tasks/%s" % agent_id)
        self.assertTrue(resp.status == 200, msg="Failed to access agent_tasks")
        text = await resp.text()
        self.assertTrue("++" in text, msg="Failed to get techniques from server")

    @unittest_run_loop
    async def test_agent_techniques(self):
        resp = await self.client.request("GET", "/agent_techniques/44444")
        self.assertTrue(resp.status == 200, msg="Failed to access /agent_techniques/44444")

    # First assign techniques to agent. First run test_customize_technique_post.
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
    async def test_customize_technique(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        resp_two = await self.client.request("GET", "/customize_technique/?agent_id=%s&tech_id=1002" % agent_id)
        self.assertTrue(resp_two.status == 200, msg="Failed to access /customize_technique. Received status code {0}"
                        .format(resp_two.status))

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

    @unittest_run_loop
    async def test_delete_tech_output(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        delete_tech_output = {'agent_id': agent_id, 'tech_id': 1002, 'test_num': 0}
        resp_two = await self.client.request("POST", "/delete_tech_output", data=delete_tech_output)
        self.assertTrue(resp_two.status == 200, msg="Failed to access /delete_tech_output. Received status code {0}"
                        .format(resp_two.status))


if __name__ == '__main__':
    unittest.main()
