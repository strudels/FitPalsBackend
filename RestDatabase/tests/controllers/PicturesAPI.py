import unittest
import simplejson as json
from app import app,db,reset_app
from app.models import *

class PicturesApiTestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

        self.test_user1 = User.query.filter(User.fb_id=="fbTestUser1").first()
        if not self.test_user1:
            self.test_user1 = User("fbTestUser1")
            db.session.add(self.test_user1)
            db.session.commit()
        self.test_user1_private = self.test_user1.dict_repr(public=False)
        self.test_user1 = self.test_user1.dict_repr()

        self.test_user2 = User.query.filter(User.fb_id=="fbTestUser2").first()
        if not self.test_user2:
            self.test_user2 = User("fbTestUser2")
            db.session.add(self.test_user2)
            db.session.commit()
        self.test_user2_private = self.test_user2.dict_repr(public=False)
        self.test_user2 = self.test_user2.dict_repr()

    def tearDown(self):
        reset_app()

    def test_add_picture(self):
        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user1["id"],
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_id})
        assert resp.status_code==201
        assert json.loads(resp.data)["message"]=="Picture added."

    def test_add_picture_user_not_found(self):
        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.post("/pictures",
                             data={"user_id":0,
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_id})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="User not found."

    def test_add_picture_not_authorized(self):
        fb_id = self.test_user1_private["fb_id"] + "junk"
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user1["id"],
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_id})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_add_picture_invalid_data(self):
        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user1["id"],
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":1.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_id})
        assert resp.status_code==400
        assert json.loads(resp.data)["message"]=="Picture data invalid."

    def test_get_pictures(self):
        resp = self.app.get("/pictures?user_id=%d" % self.test_user1["id"])
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Pictures found."

    def test_get_pictures_user_not_found(self):
        resp = self.app.get("/pictures?user_id=%d" % 0)
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="User not found."
        
    def test_update_picture(self):
        #create picture 1
        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user1["id"],
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_id})
        pic1_id = json.loads(resp.data)["value"]["id"]

        #create picture 2
        fb_id = self.test_user2_private["fb_id"]
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user2["id"],
                                   "uri":"some uri",
                                   "ui_index":1,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_id})
        pic1_id = json.loads(resp.data)["value"]["id"]
        
        #update picture
        resp = self.app.put("/pictures/%d" % self.test_user2["id"],
                             data={"uri":"some other uri",
                                   "ui_index":0,
                                   "top":0.6,
                                   "bottom":0.6,
                                   "left":0.6,
                                   "right":0.6},
                             headers={"Authorization":fb_id})
        assert resp.status_code==202
        assert json.loads(resp.data)["message"]=="Picture updated."

    def test_update_picture_not_found(self):
        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.put("/pictures/%d" % 0,
                             data={"uri":"some other uri",
                                   "ui_index":0,
                                   "top":0.6,
                                   "bottom":0.6,
                                   "left":0.6,
                                   "right":0.6},
                             headers={"Authorization":fb_id})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Picture not found."

    def test_update_picture_not_authorized(self):
        #create picture 1
        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user1["id"],
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_id})
        pic1_id = json.loads(resp.data)["value"]["id"]

        #update picture
        resp = self.app.put("/pictures/%d" % pic1_id,
                             data={"uri":"some other uri",
                                   "ui_index":0,
                                   "top":0.6,
                                   "bottom":0.6,
                                   "left":0.6,
                                   "right":0.6},
                             headers={"Authorization":fb_id + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_update_picture_invalid(self):
        #create picture 1
        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user1["id"],
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_id})
        pic1_id = json.loads(resp.data)["value"]["id"]

        #update picture
        resp = self.app.put("/pictures/%d" % pic1_id,
                             data={"uri":"some other uri",
                                   "ui_index":0,
                                   "top":0.6,
                                   "bottom":0.6,
                                   "left":1.6,
                                   "right":0.6},
                             headers={"Authorization":fb_id})
        assert resp.status_code==400
        assert json.loads(resp.data)["message"]=="Picture data invalid."
       
    def test_delete_picture(self):
        fb_id = self.test_user1_private["fb_id"]

        #add picture to delete
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user1["id"],
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_id})
        pic_id = json.loads(resp.data)["value"]["id"]
        
        #delete picture
        resp = self.app.delete("/pictures/%d" % pic_id,
            headers={"Content-Type": "application/x-www-form-urlencoded",
                    "Authorization":fb_id})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Picture removed."

    def test_delete_picture_not_found(self):
        fb_id = self.test_user1_private["fb_id"]
        #delete picture
        resp = self.app.delete("/pictures/%d" % 0,
            headers={"Content-Type": "application/x-www-form-urlencoded",
                    "Authorization":fb_id})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Picture not found."

    def test_delete_picture_not_authorized(self):
        fb_id = self.test_user1_private["fb_id"]

        #add picture to delete
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user1["id"],
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_id})
        pic_id = json.loads(resp.data)["value"]["id"]
        
        #delete picture
        resp = self.app.delete("/pictures/%d" % pic_id,
            headers={"Content-Type": "application/x-www-form-urlencoded",
                     "Authorization":fb_id + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."
