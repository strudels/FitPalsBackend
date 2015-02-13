import unittest
import simplejson as json
from app import app,db
from app.models import *

class UsersApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

        self.test_user = User.query.filter(User.fb_id=="fbTestUser1").first()
        if not self.test_user:
            self.test_user = User("fbTestUser1")
            db.session.add(self.test_user)
            db.session.commit()

    def tearDown(self):
        if hasattr(self, "test_user"):
            db.session.delete(self.test_user)
            db.session.commit()

    def test_create_user(self):
        fb_id = self.test_user.fb_id
        db.session.delete(self.test_user)
        resp = self.app.post("/users",data={"fb_id":fb_id})
        user_id = json.loads(resp.data)["value"]["id"]
        assert resp.status_code==201 #user created

    def test_get_users(self):
        resp = self.app.get("/users")
        assert resp.status_code==200

class UserAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

        self.test_user = User.query.filter(User.fb_id=="fbTestUser1").first()
        if not self.test_user:
            self.test_user = User("fbTestUser1")
            db.session.add(self.test_user)
            db.session.commit()

    def tearDown(self):
        if hasattr(self, "test_user"):
            db.session.delete(self.test_user)
            db.session.commit()

    def test_get_user(self):
        resp = self.app.get("/users/" + str(self.test_user.id))
        assert resp.status_code==200

    def test_update_user(self):
        user_id = self.test_user.id
        fb_id = self.test_user.fb_id
        resp = self.app.put("/users/" + str(user_id),
            data={
                "fb_id":fb_id,
                "longitude":20,
                "latitude":20,
                "about me":"I'm a test user!"
            })
        assert resp.status_code==202

    def test_delete_user(self):
        user_id = self.test_user.id
        fb_id = self.test_user.fb_id
        resp = self.app.delete("/users/" + str(user_id),
            data={"fb_id":fb_id},
            headers={'Content-Type': 'application/x-www-form-urlencoded'})
        self.test_user = User(fb_id)
        db.session.add(self.test_user)
        db.session.commit()
        assert resp.status_code==200
