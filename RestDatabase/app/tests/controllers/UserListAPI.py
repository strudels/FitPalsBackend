import requests
import unittest

from tests import host_url

class TestUserListAPI(unittest.TestCase):
    def users_post_signup(self):
        resp = requests.post(
            host_url + "/users",
            data={
                "fb_id":"fb8080",
                "name":"unittest",
                "longitude":-82.319645,
                "latitude":27.924475
            },
            verify=False
        )
        self.assertEqual(resp.status_code,201)

    def users_post_login(self):
        resp = requests.post(
            host_url + "/users",
            data={
                "fb_id":"fb8080",
            },
            verify=False
        )
        self.assertGreaterEqual(resp.status_code, 200)

        resp2 = requests.post(
            host_url + "/users",
            data={
                "fb_id":"fb8080",
            },
            verify=False
        )
        self.assertEqual(resp.status_code, 200)


    def users_get(self):
        resp = requests.get(
            host_url + "/users",
            params={
                "longitude":-82.319645,
                "latitude":27.924475,
                "radius":17000
            },
            verify=False
        )
        self.assertEqual(resp.status_code, 200)
