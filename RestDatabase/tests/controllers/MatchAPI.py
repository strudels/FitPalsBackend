from tests.utils.FitPalsTestCase import *

class MatchApiTestCase(FitPalsTestCase):
    def test_add_match(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "matched_user_id":self.test_user2["id"],
                                   "liked":1},
                             headers={"Authorization":fitpals_secret})
        assert resp.status_code == 201
        assert json.loads(resp.data)["message"]=="Match created."

        #ensure that test_user1 websocket self.websocket_client1 got update
        sleep(0.01) #so that the async thread has time to send the message
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["args"][0]["path"] == "/matches"
        assert received[-1]["args"][0]["http_method"] == "POST"
        assert received[-1]["args"][0]["value"] == json.loads(resp.data)["value"]

    def test_add_match_mutual_match(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "matched_user_id":self.test_user2["id"],
                                   "liked":1},
                             headers={"Authorization":fitpals_secret})
        first_match = json.loads(resp.data)["value"]
        received = self.websocket_client1.get_received()

        fitpals_secret2 = self.test_user2["fitpals_secret"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user2["id"],
                                   "matched_user_id":self.test_user1["id"],
                                   "liked":1},
                             headers={"Authorization":fitpals_secret2})
        second_match = json.loads(resp.data)["value"]

        #ensure that test_user1 websocket self.websocket_client1 got update
        sleep(0.01) #so that the async thread has time to send the message
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["args"][0]["path"] == "/matches"
        assert received[-1]["args"][0]["http_method"] == "POST"
        assert received[-1]["args"][0]["value"] == second_match

        #ensure that test_user2 websocket self.websocket_client1 got update
        sleep(0.01) #so that the async thread has time to send the message
        received = self.websocket_client2.get_received()
        assert len(received) != 0
        match_id = received[-1]["args"][0]["value"]["matched_user_id"]
        received[-1]["args"][0]["value"]["matched_user_id"] =\
            received[-1]["args"][0]["value"]["user_id"]
        received[-1]["args"][0]["value"]["user_id"] = match_id
        assert received[-1]["args"][0]["path"] == "/matches"
        assert received[-1]["args"][0]["http_method"] == "POST"
        received_via_api = json.loads(resp.data)["value"]
        del second_match["id"]
        del received[-1]["args"][0]["value"]["id"]
        del second_match["matched_user"]
        del received[-1]["args"][0]["value"]["matched_user"]
        assert received[-1]["args"][0]["value"] == second_match
        
    def test_add_match_user_not_found(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/matches",
                             data={"user_id":0,
                                   "matched_user_id":self.test_user2["id"],
                                   "liked":1},
                             headers={"Authorization":fitpals_secret})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"]=="User not found."
        

    def test_add_match_matched_user_not_found(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "matched_user_id":0,
                                   "liked":1},
                             headers={"Authorization":fitpals_secret})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"]=="Match user not found."

    def test_add_match_not_authorized(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "matched_user_id":self.test_user2["id"],
                                   "liked":1},
                             headers={"Authorization":fitpals_secret + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"]=="Not Authorized."
        
    def test_add_match_could_not_create(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "matched_user_id":self.test_user1["id"],
                                   "liked":1},
                             headers={"Authorization":fitpals_secret})
        assert resp.status_code == 400
        assert json.loads(resp.data)["message"]=="Match data invalid."
        
    def test_get_matches(self):
        #create match to get
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "matched_user_id":self.test_user2["id"],
                                   "liked":1},
                             headers={"Authorization":fitpals_secret})
        assert resp.status_code == 201
        match = json.loads(resp.data)["value"]

        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.get("/matches",
                            headers={"Authorization":fitpals_secret})
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"]=="Matches found."
        assert json.loads(resp.data)["value"][0] == match
        
    def test_get_mutual_matches(self):
        #create 2 matches, so that each makes the other a mutual match
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "matched_user_id":self.test_user2["id"],
                                   "liked":1},
                             headers={"Authorization":fitpals_secret})
        assert resp.status_code == 201
        match = json.loads(resp.data)["value"]
        fitpals_secret = self.test_user2["fitpals_secret"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user2["id"],
                                   "matched_user_id":self.test_user1["id"],
                                   "liked":1},
                             headers={"Authorization":fitpals_secret})
        assert resp.status_code == 201

        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.get("/matches?mutual=1",
                            headers={"Authorization":fitpals_secret})
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"]=="Matches found."
        assert json.loads(resp.data)["value"][0] == match

    def test_get_matches_not_authorized(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.get("/matches",
                            headers={"Authorization":fitpals_secret + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"]=="Not Authorized."
        
    def test_update_match(self):
        #create match
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "matched_user_id":self.test_user2["id"],
                                   "liked":1},
                             headers={"Authorization":fitpals_secret})
        match = json.loads(resp.data)["value"]
        
        #update match
        resp = self.app.put("/matches/%d" % match["id"],
                            headers={"Authorization":fitpals_secret})
        received_match = json.loads(resp.data)["value"]
        assert resp.status_code == 202
        assert json.loads(resp.data)["message"] == "Match updated."
        match["read"] = True
        assert match == received_match
        
        #get match, to see if update persisted
        resp = self.app.get("/matches",
                            headers={"Authorization":fitpals_secret})
        matches = json.loads(resp.data)["value"]
        assert len(matches) == 1
        assert matches[0] == received_match
        
        #ensure that test_user1 websocket self.websocket_client1 got update
        sleep(0.01) #so that the async thread has time to send the message
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["args"][0]["path"] == "/matches/%d" % match["id"]
        assert received[-1]["args"][0]["http_method"] == "PUT"
        assert received[-1]["args"][0]["value"] == received_match
        
    def test_update_match_not_found(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.put("/matches/0",
                            headers={"Authorization":fitpals_secret})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"] == "Match not found."
        
    def test_update_match_not_authorized_bad_secret(self):
        #create match
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "matched_user_id":self.test_user2["id"],
                                   "liked":1},
                             headers={"Authorization":fitpals_secret})
        match = json.loads(resp.data)["value"]

        #attempt to update match
        resp = self.app.put("/matches/%d" % match["id"],
                            headers={"Authorization":fitpals_secret + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"] == "Not Authorized."

    def test_update_match_not_authorized_wrong_user(self):
        #create match
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "matched_user_id":self.test_user2["id"],
                                   "liked":1},
                             headers={"Authorization":fitpals_secret})
        match = json.loads(resp.data)["value"]
        
        #attempt to update match
        resp = self.app.put("/matches/%d" % match["id"],
                            headers={"Authorization":self.test_user2["fitpals_secret"]})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"] == "Not Authorized."
        
    def test_delete_match(self):
        #create match
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "matched_user_id":self.test_user2["id"],
                                   "liked":1},
                             headers={"Authorization":fitpals_secret})
        match_id = json.loads(resp.data)["value"]["id"]
        
        #delete match
        resp = self.app.delete("/matches/%d" % match_id,
                               headers={"Authorization":fitpals_secret})
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"]=="Match deleted."

        #ensure that test_user1 websocket self.websocket_client1 got update
        sleep(0.01) #so that the async thread has time to send the message
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["args"][0]["path"] == "/matches/%d" % match_id
        assert received[-1]["args"][0]["http_method"] == "DELETE"
        assert received[-1]["args"][0]["value"] == None

        #ensure that match no longer stored
        resp = self.app.get("/matches",
                            headers={"Authorization":fitpals_secret})
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"]=="Matches found."
        assert len(json.loads(resp.data)["value"]) == 0
        
    def test_delete_match_not_found(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.delete("/matches/%d" % 0,
                               headers={"Authorization":fitpals_secret})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"]=="Match not found."

    def test_delete_match_not_authorized(self):
        #create match
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/matches",
                             data={"user_id":self.test_user1["id"],
                                   "matched_user_id":self.test_user2["id"],
                                   "liked":1},
                             headers={"Authorization":fitpals_secret})
        match_id = json.loads(resp.data)["value"]["id"]
        
        #delete match
        resp = self.app.delete("/matches/%d" % match_id,
                               headers={"Authorization":fitpals_secret + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"]=="Not Authorized."
