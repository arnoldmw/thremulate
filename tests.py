import unittest
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
# noinspection PyUnresolvedReferences
from server import create_app
# noinspection PyUnresolvedReferences
from server import create_app_two

data = {'email': 'admin@thremulate.com', 'password': 'thremulate'}


class ThremulateTests(AioHTTPTestCase):

    async def get_application(self):
        app = await create_app()
        return app

    @unittest_run_loop
    async def test_index(self):
        resp = await self.client.request("GET", "/")
        assert resp.status == 200
        text = await resp.text()
        assert "Thremulate" in text

    @unittest_run_loop
    async def test_login_get(self):
        resp = await self.client.request("GET", "/login")
        assert resp.status == 200
        # text = await resp.text()
        # assert "Hello, world" in text

    @unittest_run_loop
    async def test_login_post(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        assert resp.status == 200

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
        # text = await resp.text()
        # assert ";" in text

    @unittest_run_loop
    async def test_dashboard(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        resp_two = await self.client.request("GET", "/dashboard")
        self.assertTrue(resp_two.status == 200, msg="Failed to access /dashboard. Received status code {0}"
                        .format(resp_two.status))
        text = await resp.text()
        assert "Dashboard" in text

    @unittest_run_loop
    async def test_agent_index(self):
        resp = await self.client.request("POST", "/login_post", data=data)
        self.assertTrue(resp.status == 200, msg="Failed to access /login. Received status code {0}"
                        .format(resp.status))
        resp_two = await self.client.request("GET", "/agents")
        self.assertTrue(resp_two.status == 200, msg="Failed to access /agents. Received status code {0}"
                        .format(resp_two.status))
        text = await resp_two.text()
        assert "Agents" in text


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


class Agent(AioHTTPTestCase):
    async def get_application(self):
        app = await create_app_two()
        return app

    @unittest_run_loop
    async def test_register(self):
        agent_registration = {'id': 44444, 'hostname': 'DC01', 'platform': 'windows', 'plat_version': '10.10.10',
                              'username': 'Administrator'}
        resp = await self.client.request("POST", "register_agent", data=agent_registration)
        self.assertTrue(resp.status == 200, msg="Failed to access /register_agent. Received status code {0}"
                        .format(resp.status))
        text = await resp.text()
        self.assertTrue('Agent has registered' in text, msg="Server failed to register agent. "
                                                            "Agent may already be registered")

    # TODO First add agent
    @unittest_run_loop
    async def test_agent_tasks(self):
        resp = await self.client.request("GET", "/agent_tasks/5")
        assert resp.status == 200
        text = await resp.text()
        assert "++" in text


if __name__ == '__main__':
    unittest.main()
