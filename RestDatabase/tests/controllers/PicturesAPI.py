import unittest
import simplejson as json
from app import app,db
from app.models import *

class PicturesApiTestCase(unittest.TestCase):
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

    def test_add_picture(self):
        fb_id = self.test_user.fb_id
        db.session.add(self.test_user)
        resp = self.app.post("/users/" + str(self.test_user.id) + "/pictures",
            data={"picture_id":"some fb picture id string"},
            headers={"Authorization":fb_id})
        db.session.commit()
        assert resp.status_code==201 #user created

    def test_add_picture_unauthorized(self):
        fb_id = self.test_user.fb_id
        db.session.add(self.test_user)
        resp = self.app.post("/users/" + str(self.test_user.id) + "/pictures",
            data={"picture_id":"some fb picture id string"},
            headers={"Authorization":fb_id + "junk"})
        db.session.commit()
        assert resp.status_code==401 #Not Authorized

    def test_get_pictures(self):
        resp = self.app.get("/users/" + str(self.test_user.id) + "/pictures")
        assert resp.status_code==200

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
