import unittest
import simplejson as json
from app import app,db,socketio,reset_app
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
        
    def test_add_match(self):
        #log in test_user1 to chat web socke
        client = socketio.test_client(app)
        client.emit("join", self.test_user1_private)

        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "match_user_id":self.test_user2["id"],
                                   "liked":True},
                             headers={"Authorization":fb_id})
        assert resp.status_code == 201
        assert json.loads(resp.data)["message"]=="Match created."

        #ensure that test_user1 websocket client got update
        received = client.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "match_added"

    def test_add_match_mutual_match(self):
        #log in test_user1 to chat web socke
        client = socketio.test_client(app)
        client.emit("join", self.test_user1_private)
        client2 = socketio.test_client(app)
        client2.emit("join", self.test_user2_private)

        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "match_user_id":self.test_user2["id"],
                                   "liked":True},
                             headers={"Authorization":fb_id})

        fb_id2 = self.test_user2_private["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user2["id"],
                                   "match_user_id":self.test_user1["id"],
                                   "liked":True},
                             headers={"Authorization":fb_id2})

        #ensure that test_user1 websocket client got update
        received = client.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "mutual_match_added"

        #ensure that test_user2 websocket client got update
        received = client2.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "mutual_match_added"
        
    def test_add_match_user_not_found(self):
        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":0,
                                   "match_user_id":self.test_user2["id"],
                                   "liked":True},
                             headers={"Authorization":fb_id})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"]=="User not found."
        

    def test_add_match_matched_user_not_found(self):
        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "match_user_id":0,
                                   "liked":True},
                             headers={"Authorization":fb_id})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"]=="Matched user not found."

    def test_add_match_not_authorized(self):
        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "match_user_id":self.test_user2["id"],
                                   "liked":True},
                             headers={"Authorization":fb_id + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"]=="Not Authorized."
        
    def test_add_match_could_not_create(self):
        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "match_user_id":self.test_user1["id"],
                                   "liked":True},
                             headers={"Authorization":fb_id})
        assert resp.status_code == 400
        assert json.loads(resp.data)["message"]=="Could not create match."
        
    def test_get_matches(self):
        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.get("/matches?user_id=%d" % self.test_user1["id"],
                            headers={"Authorization":fb_id})
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"]=="Matches found."

    def test_get_matches_user_not_found(self):
        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.get("/matches?user_id=%d" % 0,
                            headers={"Authorization":fb_id})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"]=="User not found."

    def test_get_matches_not_authorized(self):
        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.get("/matches?user_id=%d" % self.test_user1["id"],
                            headers={"Authorization":fb_id + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"]=="Not Authorized."
        
    def test_get_matches_liked(self):
        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.get("/matches?user_id=%d&liked=true" % self.test_user1["id"],
                            headers={"Authorization":fb_id})
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"]=="Matches found."
        
    def test_delete_match(self):
        #log in test_user1 to chat web socke
        client = socketio.test_client(app)
        client.emit("join", self.test_user1_private)

        #create match
        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "match_user_id":self.test_user2["id"],
                                   "liked":True},
                             headers={"Authorization":fb_id})
        match_id = json.loads(resp.data)["value"]["id"]
        
        #delete match
        resp = self.app.delete("/matches/%d" % match_id,
                               headers={"Authorization":fb_id})
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"]=="Match deleted."

        #ensure that test_user1 websocket client got update
        received = client.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "match_deleted"
        
    def test_delete_match_not_found(self):
        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.delete("/matches/%d" % 0,
                               headers={"Authorization":fb_id})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"]=="Match not found."

    def test_delete_match_not_authorized(self):
        #create match
        fb_id = self.test_user1_private["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "match_user_id":self.test_user2["id"],
                                   "liked":True},
                             headers={"Authorization":fb_id})
        match_id = json.loads(resp.data)["value"]["id"]
        
        #delete match
        resp = self.app.delete("/matches/%d" % match_id,
                               headers={"Authorization":fb_id + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"]=="Not Authorized."
