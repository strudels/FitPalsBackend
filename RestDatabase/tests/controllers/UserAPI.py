import unittest
import simplejson as json
from app import app,db,socketio,reset_app
from app.models import *

class UsersApiTestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

        self.test_user = User.query.filter(User.fb_id=="fbTestUser1").first()
        if not self.test_user:
            self.test_user = User("fbTestUser1")
            db.session.add(self.test_user)
            db.session.commit()
            self.test_user = self.test_user.dict_repr(public=False)

    def tearDown(self):
        reset_app()

    def test_create_user(self):
        resp = self.app.post("/users",data={"fb_id":"some fb_id"})
        assert resp.status_code==201 #user created

    def test_get_users(self):
        resp = self.app.get("/users")
        assert resp.status_code==200

    def test_get_user(self):
        resp = self.app.get("/users/" + str(self.test_user["id"]))
        assert resp.status_code==200

    def test_update_user(self):
        #log in test_user1 to chat web socket
        client = socketio.test_client(app)
        client.emit("join", self.test_user)

        user_id = self.test_user["id"]
        fb_id = self.test_user["fb_id"]
        resp = self.app.put("/users/" + str(user_id),
                            data={
                                "longitude":20,
                                "latitude":20,
                                "about me":"I'm a test user!"},
                            headers = {"Authorization":fb_id})
        assert resp.status_code==202

    def test_delete_user(self):
        user_id = self.test_user["id"]
        fb_id = self.test_user["fb_id"]
        resp = self.app.delete("/users/" + str(user_id),
                               headers={"Content-Type": "application/x-www-form-urlencoded",
                                        "Authorization":fb_id})
        assert resp.status_code==200
