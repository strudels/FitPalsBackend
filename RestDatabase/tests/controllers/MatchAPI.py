import unittest
import simplejson as json
from app import app,db
from app.models import *

class MatchApiTestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

        self.test_user1 = User.query.filter(User.fb_id=="fbTestUser1").first()
        if not self.test_user1:
            self.test_user1 = User("fbTestUser1")
            db.session.add(self.test_user1)
            db.session.commit()

        self.test_user2 = User.query.filter(User.fb_id=="fbTestUser1").first()
        if not self.test_user2:
            self.test_user2 = User("fbTestUser1")
            db.session.add(self.test_user2)
            db.session.commit()

    def tearDown(self):
        if hasattr(self, "test_user1"):
            db.session.delete(self.test_user1)
            db.session.commit()

        if hasattr(self, "test_user2"):
            db.session.delete(self.test_user2)
            db.session.commit()

    def test_add_match(self):
        fb_id = self.test_user1.fb_id
        resp = self.app.post("/users/" + str(self.test_user1.id) + "/matches",
                             data={"match_id":self.test_user2.id, "liked":True},
                             headers={"Authorization":fb_id})
        assert resp.status_code==201

    def test_add_match_unauthorized(self):
        fb_id = self.test_user1.fb_id
        resp = self.app.post("/users/" + str(self.test_user1.id) + "/matches",
                             data={"match_id":self.test_user2.id, "liked":True},
                             headers={"Authorization":fb_id + "junk"})
        assert resp.status_code==401

    def test_get_matches(self):
        resp = self.app.get("/users/" + str(self.test_user1.id) + "/matches")
        assert resp.status_code==200

    def test_get_liked_matches(self):
        resp = self.app.get("/users/" + str(self.test_user1.id) + "/matches?liked=true")
        assert resp.status_code==200

    def test_delete_matches(self):
        fb_id = self.test_user1.fb_id
        resp = self.app.delete("/users/" + str(self.test_user1.id) + "/matches",
            headers={'Content-Type': 'application/x-www-form-urlencoded',
                     "Authorization":fb_id})
        assert resp.status_code==200

    def test_delete_matches_unauthorized(self):
        fb_id = self.test_user1.fb_id
        resp = self.app.delete("/users/" + str(self.test_user1.id) + "/matches",
            headers={'Content-Type': 'application/x-www-form-urlencoded',
                     "Authorization":fb_id + "junk"})
        assert resp.status_code==401

    def test_delete_one_match(self):
        fb_id = self.test_user1.fb_id
        resp = self.app.delete("/users/" + str(self.test_user1.id) + "/matches",
            data={"match_id":self.test_user2.id},
            headers={'Content-Type': 'application/x-www-form-urlencoded',
                     "Authorization":fb_id})
        assert resp.status_code==200
