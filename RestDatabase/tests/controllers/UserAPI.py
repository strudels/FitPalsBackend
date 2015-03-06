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
            self.test_user.name = "test"
            db.session.add(self.test_user)
            db.session.commit()
            self.test_user_public = self.test_user.dict_repr()
            self.test_user = self.test_user.dict_repr(public=False)

    def tearDown(self):
        reset_app()

    def test_create_user(self):
        resp = self.app.post("/users",data={"fb_id":"some fb_id"})
        assert resp.status_code==201
        assert json.loads(resp.data)["message"] == "User created."

    def test_create_user_found(self):
        resp = self.app.post("/users",data={"fb_id":self.test_user["fb_id"]})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"] == "User found."

    def test_get_users(self):
        resp = self.app.get("/users")
        assert resp.status_code==200

    def test_get_user(self):
        resp = self.app.get("/users/" + str(self.test_user["id"]))
        assert resp.status_code==200
        assert json.loads(resp.data)["value"] == self.test_user_public

    def test_get_user_name(self):
        resp = self.app.get("/users/" + str(self.test_user["id"])\
                            + "?attributes=name")
        assert resp.status_code==200
        assert json.loads(resp.data)["value"] == {"name":self.test_user["name"]}
        
    def test_get_user_not_found(self):
        resp = self.app.get("/users/0")
        assert resp.status_code==404
        assert json.loads(resp.data)["message"] == "User not found."
        
    def test_get_user_authorized(self):
        resp = self.app.get("/users/" + str(self.test_user["id"]),
                            headers={"Authorization":self.test_user["fb_id"]})
        assert resp.status_code==200
        assert json.loads(resp.data)["value"] == self.test_user

    def test_get_user_not_authorized(self):
        resp = self.app.get("/users/" + str(self.test_user["id"]),
                            headers={"Authorization":
                                     self.test_user["fb_id"] + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"] == "Not Authorized."

    def test_update_user(self):
        #log in test_user1 to chat web socket
        client = socketio.test_client(app)
        client.emit("join", self.test_user)

        #update the user
        user_id = self.test_user["id"]
        fb_id = self.test_user["fb_id"]
        resp = self.app.put("/users/" + str(user_id),
                            data={
                                "longitude":20,
                                "latitude":20,
                                "about me":"I'm a test user!"},
                            headers = {"Authorization":fb_id})
        assert resp.status_code==202
        
        #ensure that test_user websocket client got new user update
        received = client.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "user_update"
        assert received[-1]["args"][0] == self.test_user_public
        
    def test_update_user_not_found(self):
        user_id = 0
        fb_id = self.test_user["fb_id"]
        resp = self.app.put("/users/" + str(user_id),
                            data={
                                "longitude":20,
                                "latitude":20,
                                "about me":"I'm a test user!"},
                            headers = {"Authorization":fb_id})
        assert resp.status_code==400
        assert json.loads(resp.data)["message"] == "Could not find user."
        
    def test_update_user_not_authorized(self):
        user_id = self.test_user["id"]
        fb_id = self.test_user["fb_id"] + "junk"
        resp = self.app.put("/users/" + str(user_id),
                            data={
                                "longitude":20,
                                "latitude":20,
                                "about me":"I'm a test user!"},
                            headers = {"Authorization":fb_id})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"] == "Not Authorized."
        
    def test_delete_user(self):
        user_id = self.test_user["id"]
        fb_id = self.test_user["fb_id"]
        resp = self.app.delete("/users/" + str(user_id),
                               headers={"Content-Type": "application/x-www-form-urlencoded",
                                        "Authorization":fb_id})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"] == "User deleted."
        
    def test_delete_user_not_found(self):
        user_id = 0
        fb_id = self.test_user["fb_id"]
        resp = self.app.delete("/users/" + str(user_id),
                               headers={"Content-Type": "application/x-www-form-urlencoded",
                                        "Authorization":fb_id})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"] == "Could not find user."

    def test_delete_user_not_authorized(self):
        user_id = self.test_user["id"]
        fb_id = self.test_user["fb_id"] + "junk"
        resp = self.app.delete("/users/" + str(user_id),
                               headers={"Content-Type": "application/x-www-form-urlencoded",
                                        "Authorization":fb_id})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"] == "Not Authorized."
