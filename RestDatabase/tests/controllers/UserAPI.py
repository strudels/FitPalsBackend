import unittest
from app import app

class UserApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        pass

    def tearDown(self):
        pass

    def test_failure(self):
        resp = self.app.get("/users")
        assert True == False
