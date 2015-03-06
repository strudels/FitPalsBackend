import unittest
import simplejson as json
from app import app,db,reset_app
from app.models import *

class PicturesApiTestCase(unittest.TestCase):
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

    def test_add_picture(self):
        fb_id = self.test_user_private["fb_id"]
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user["id"],
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_id})
        assert resp.status_code==201 #user created
        assert json.loads(resp.data)["message"]=="Picture added."

    def test_add_picture_user_not_found(self):
        fb_id = self.test_user_private["fb_id"]
        resp = self.app.post("/pictures",
                             data={"user_id":0,
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_id})
        assert resp.status_code==404 #user created
        assert json.loads(resp.data)["message"]=="User not found."

    def test_add_picture_not_authorized(self):
        fb_id = self.test_user_private["fb_id"] + "junk"
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user["id"],
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_id})
        assert resp.status_code==401 #user created
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_add_picture_invalid_data(self):
        fb_id = self.test_user_private["fb_id"]
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user["id"],
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":1.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_id})
        assert resp.status_code==400 #user created
        assert json.loads(resp.data)["message"]=="Picture data invalid."

    def test_get_pictures(self):
        resp = self.app.get("/pictures?user_id=%d" % self.test_user["id"])
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Pictures found."

    def test_get_pictures_user_not_found(self):
        resp = self.app.get("/pictures?user_id=%d" % 0)
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="User not found."

    """
    def test_delete_pictures(self):
        fb_id = self.test_user.fb_id
        self.test_user.secondary_pictures.append(Picture(self.test_user,"some fb picture string"))
        db.session.commit()
        resp = self.app.delete("/users/" + str(self.test_user.id) + "/pictures",
            headers={'Content-Type': 'application/x-www-form-urlencoded',
                    "Authorization":fb_id})
        db.session.commit()
        assert resp.status_code==200

    def test_delete_pictures_unauthorized(self):
        fb_id = self.test_user.fb_id
        self.test_user.secondary_pictures.append(Picture(self.test_user,"some fb picture string"))
        db.session.commit()
        resp = self.app.delete("/users/" + str(self.test_user.id) + "/pictures",
            headers={'Content-Type': 'application/x-www-form-urlencoded',
                     "Authorization":fb_id + "junk"})
        db.session.commit()
        assert resp.status_code==200

    def test_delete_one_picture(self):
        fb_id = self.test_user.fb_id
        self.test_user.secondary_pictures.append(Picture(self.test_user,"some fb picture string"))
        db.session.commit()
        pic = self.test_user.secondary_pictures.first()
        resp = self.app.delete("/users/" + str(self.test_user.id) + "/pictures",
            headers={'Content-Type': 'application/x-www-form-urlencoded',
                    "Authorization":fb_id})
        assert resp.status_code==200
    """
