import unittest
import simplejson as json
from app import app,db, reset_app
from app.models import *

class APNTokensApiTestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

        self.test_user = User.query.filter(User.fb_id=="fbTestUser1").first()
        if not self.test_user:
            self.test_user = User("fbTestUser1")
            db.session.add(self.test_user)
            db.session.commit()
        self.test_user_private = self.test_user.dict_repr(public=False)
        self.test_user = self.test_user.dict_repr()

    def tearDown(self):
        reset_app()

    def test_add_device(self):
        fb_id = self.test_user_private["fb_id"]
        resp = self.app.post("/devices",
                             data={"token":"some apn token","user_id":self.test_user["id"]},
                             headers={"Authorization":fb_id})
        assert resp.status_code==201
        assert json.loads(resp.data)["message"]=="Device registered."

    def test_add_device_already_registered(self):
        fb_id = self.test_user_private["fb_id"]
        #post same device twice
        resp = self.app.post("/devices",
                             data={"token":"some apn token","user_id":self.test_user["id"]},
                             headers={"Authorization":fb_id})
        resp = self.app.post("/devices",
                             data={"token":"some apn token","user_id":self.test_user["id"]},
                             headers={"Authorization":fb_id})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Device already registered."

    def test_add_device_user_not_found(self):
        fb_id = self.test_user_private["fb_id"]
        resp = self.app.post("/devices",
                             data={"token":"some apn token","user_id":0},
                             headers={"Authorization":fb_id})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="User not found."

    def test_add_device_not_authorized(self):
        fb_id = self.test_user_private["fb_id"] + "junk"
        resp = self.app.post("/devices",
                             data={"token":"some apn token","user_id":self.test_user["id"]},
                             headers={"Authorization":fb_id})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_add_device_could_not_register(self):
        fb_id = self.test_user_private["fb_id"]
        resp = self.app.post("/devices",
                             data={"token":"some apn token"*9000,
                                   "user_id":self.test_user["id"]},
                             headers={"Authorization":fb_id})
        assert resp.status_code==400
        assert json.loads(resp.data)["message"]=="Could not register device."

    def test_delete_device(self):
        fb_id = self.test_user_private["fb_id"]
        #create device
        resp = self.app.post("/devices",
                             data={"token":"some apn token","user_id":self.test_user["id"]},
                             headers={"Authorization":fb_id})
        device_id = json.loads(resp.data)["value"]["id"]

        #delete device
        resp = self.app.delete("/devices/%d" % device_id,
                               headers={"Authorization":fb_id})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Device deleted."

    def test_delete_device_not_found(self):
        fb_id = self.test_user_private["fb_id"]
        #create device
        resp = self.app.post("/devices",
                             data={"token":"some apn token","user_id":self.test_user["id"]},
                             headers={"Authorization":fb_id})
        device_id = json.loads(resp.data)["value"]["id"]

        #delete device
        resp = self.app.delete("/devices/%d" % 0,
                               headers={"Authorization":fb_id})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Device not found."

    def test_delete_device_not_authorized(self):
        fb_id = self.test_user_private["fb_id"]
        #create device
        resp = self.app.post("/devices",
                             data={"token":"some apn token","user_id":self.test_user["id"]},
                             headers={"Authorization":fb_id})
        device_id = json.loads(resp.data)["value"]["id"]

        #delete device
        resp = self.app.delete("/devices/%d" % device_id,
                               headers={"Authorization":fb_id + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."
