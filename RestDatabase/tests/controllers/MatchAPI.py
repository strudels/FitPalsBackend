from tests.utils.FitPalsTestCase import *

class MatchApiTestCase(FitPalsTestCase):
    def test_add_match(self):
        fb_id = self.test_user1["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "match_user_id":self.test_user2["id"],
                                   "liked":1},
                             headers={"Authorization":fb_id})
        assert resp.status_code == 201
        assert json.loads(resp.data)["message"]=="Match created."

        #ensure that test_user1 websocket self.websocket_client1 got update
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "match_added"

    def test_add_match_mutual_match(self):
        fb_id = self.test_user1["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "match_user_id":self.test_user2["id"],
                                   "liked":1},
                             headers={"Authorization":fb_id})

        fb_id2 = self.test_user2["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user2["id"],
                                   "match_user_id":self.test_user1["id"],
                                   "liked":1},
                             headers={"Authorization":fb_id2})

        #ensure that test_user1 websocket self.websocket_client1 got update
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "mutual_match_added"

        #ensure that test_user2 websocket self.websocket_client1 got update
        received = self.websocket_client2.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "mutual_match_added"
        
    def test_add_match_user_not_found(self):
        fb_id = self.test_user1["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":0,
                                   "match_user_id":self.test_user2["id"],
                                   "liked":1},
                             headers={"Authorization":fb_id})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"]=="User not found."
        

    def test_add_match_matched_user_not_found(self):
        fb_id = self.test_user1["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "match_user_id":0,
                                   "liked":1},
                             headers={"Authorization":fb_id})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"]=="Match user not found."

    def test_add_match_not_authorized(self):
        fb_id = self.test_user1["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "match_user_id":self.test_user2["id"],
                                   "liked":1},
                             headers={"Authorization":fb_id + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"]=="Not Authorized."
        
    def test_add_match_could_not_create(self):
        fb_id = self.test_user1["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "match_user_id":self.test_user1["id"],
                                   "liked":1},
                             headers={"Authorization":fb_id})
        assert resp.status_code == 400
        assert json.loads(resp.data)["message"]=="Could not create match."
        
    def test_get_matches(self):
        #create match to get
        fb_id = self.test_user1["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "match_user_id":self.test_user2["id"],
                                   "liked":1},
                             headers={"Authorization":fb_id})
        assert resp.status_code == 201
        match = json.loads(resp.data)["value"]

        fb_id = self.test_user1["fb_id"]
        resp = self.app.get("/matches",
                            headers={"Authorization":fb_id})
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"]=="Matches found."
        assert json.loads(resp.data)["value"][0] == match

    def test_get_matches_not_authorized(self):
        fb_id = self.test_user1["fb_id"]
        resp = self.app.get("/matches",
                            headers={"Authorization":fb_id + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"]=="Not Authorized."
        
    def test_get_matches_liked(self):
        #create liked match to get
        fb_id = self.test_user1["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "match_user_id":self.test_user2["id"],
                                   "liked":1},
                             headers={"Authorization":fb_id})
        assert resp.status_code == 201

        #create unliked match to get
        fb_id = self.test_user1["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "match_user_id":self.test_user3["id"],
                                   "liked":0},
                             headers={"Authorization":fb_id})
        assert resp.status_code == 201

        match = json.loads(resp.data)["value"]
        match = json.loads(resp.data)["value"]
        fb_id = self.test_user1["fb_id"]

        #ensure only 1 liked match
        resp = self.app.get("/matches?liked=1",
                            headers={"Authorization":fb_id})
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"]=="Matches found."
        assert len(json.loads(resp.data)["value"]) == 1

        #ensure only 1 unliked match
        resp = self.app.get("/matches?liked=0",
                            headers={"Authorization":fb_id})
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"]=="Matches found."
        assert len(json.loads(resp.data)["value"]) == 1
        
    def test_delete_match(self):
        #create match
        fb_id = self.test_user1["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "match_user_id":self.test_user2["id"],
                                   "liked":1},
                             headers={"Authorization":fb_id})
        match_id = json.loads(resp.data)["value"]["id"]
        
        #delete match
        resp = self.app.delete("/matches/%d" % match_id,
                               headers={"Authorization":fb_id})
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"]=="Match deleted."

        #ensure that test_user1 websocket self.websocket_client1 got update
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "match_deleted"

        #ensure that match no longer stored
        resp = self.app.get("/matches",
                            headers={"Authorization":fb_id})
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"]=="Matches found."
        assert len(json.loads(resp.data)["value"]) == 0
        
    def test_delete_match_not_found(self):
        fb_id = self.test_user1["fb_id"]
        resp = self.app.delete("/matches/%d" % 0,
                               headers={"Authorization":fb_id})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"]=="Match not found."

    def test_delete_match_not_authorized(self):
        #create match
        fb_id = self.test_user1["fb_id"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "match_user_id":self.test_user2["id"],
                                   "liked":1},
                             headers={"Authorization":fb_id})
        match_id = json.loads(resp.data)["value"]["id"]
        
        #delete match
        resp = self.app.delete("/matches/%d" % match_id,
                               headers={"Authorization":fb_id + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"]=="Not Authorized."
