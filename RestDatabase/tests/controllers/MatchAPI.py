import unittest
import simplejson as json
from app import app,db
from app.models import *

class MatchApiTestCase(unittest.TestCase):
    def setUp(self):
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
            data={"fb_id":fb_id, "match_id":self.test_user2.id, "liked":True})
        assert resp.status_code==201 #match created

    def test_get_matches(self):
        resp = self.app.get("/users/" + str(self.test_user1.id) + "/matches")
        assert resp.status_code==200

    def test_get_liked_matches(self):
        resp = self.app.get("/users/" + str(self.test_user1.id) + "/matches?liked=true")
        assert resp.status_code==200

    def test_delete_matches(self):
        fb_id = self.test_user1.fb_id
        resp = self.app.delete("/users/" + str(self.test_user1.id) + "/matches",
            data={"fb_id":fb_id},
            headers={'Content-Type': 'application/x-www-form-urlencoded'})
        assert resp.status_code==200

    def test_delete_one_match(self):
        fb_id = self.test_user1.fb_id
        resp = self.app.delete("/users/" + str(self.test_user1.id) + "/matches",
            data={"fb_id":fb_id, "match_id":self.test_user2.id},
            headers={'Content-Type': 'application/x-www-form-urlencoded'})
        assert resp.status_code==200