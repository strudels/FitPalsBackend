from tests.utils.FitPalsTestCase import *

class APNTokensApiTestCase(FitPalsTestCase):
    def test_add_friend(self):
        fb_id = self.test_user1["fb_id"]
        friend = {"user_id":self.test_user1["id"],
                  "friend_user_id":self.test_user2["id"]}
        resp = self.app.post("/friends",data=friend,
                             headers={"Authorization":fb_id})
        assert resp.status_code == 201
        assert json.loads(resp.data)["message"] == "Friend added."
        received_friend = json.loads(resp.data)["value"]
        assert type(received_friend["id"]) == int
        friend["id"] = received_friend["id"]
        assert friend == received_friend

    def test_add_friend_user_not_found(self):
        fb_id = self.test_user1["fb_id"]
        friend = {"user_id":0,
                  "friend_user_id":self.test_user2["id"]}
        resp = self.app.post("/friends",data=friend,
                             headers={"Authorization":fb_id})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"] == "User not found."

    def test_add_friend_friend_user_not_found(self):
        fb_id = self.test_user1["fb_id"]
        friend = {"user_id":self.test_user1["id"],
                  "friend_user_id":0}
        resp = self.app.post("/friends",data=friend,
                             headers={"Authorization":fb_id})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"] == "User not found."
    
    def test_add_friend_not_authorized(self):
        fb_id = self.test_user1["fb_id"]
        friend = {"user_id":self.test_user1["id"],
                  "friend_user_id":self.test_user2["id"]}
        resp = self.app.post("/friends",data=friend,
                             headers={"Authorization":fb_id + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"] == "Not Authorized."
        
    def test_get_friends(self):
        #create friend to get
        fb_id = self.test_user1["fb_id"]
        friend = {"user_id":self.test_user1["id"],
                  "friend_user_id":self.test_user2["id"]}
        resp = self.app.post("/friends",data=friend,
                             headers={"Authorization":fb_id})
        friend = json.loads(resp.data)["value"]
        
        #get friend
        resp = self.app.get("/friends",headers={"Authorization":fb_id})
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"] == "Friends found."
        friends = json.loads(resp.data)["value"]
        assert len(friends) == 1
        assert friend == friends[0]
        
    def test_get_friends_not_authorized(self):
        fb_id = self.test_user1["fb_id"]
        resp = self.app.get("/friends",headers={"Authorization":fb_id+"junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"] == "Not Authorized."

    def test_delete_friend(self):
        #create friend to delete
        fb_id = self.test_user1["fb_id"]
        friend = {"user_id":self.test_user1["id"],
                  "friend_user_id":self.test_user2["id"]}
        resp = self.app.post("/friends",data=friend,
                             headers={"Authorization":fb_id})
        friend = json.loads(resp.data)["value"]
        
        #delete friend
        resp = self.app.delete("/friends/%d" % friend["id"],
                               headers={"Authorization":fb_id})
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"] == "Friend deleted."
        
        #ensure that friend was deleted
        resp = self.app.get("/friends",headers={"Authorization":fb_id})
        friends = json.loads(resp.data)["value"]
        assert len(friends) == 0
        
    def test_delete_friend_not_found(self):
        #delete friend
        fb_id = self.test_user1["fb_id"]
        resp = self.app.delete("/friends/%d" % 0,
                               headers={"Authorization":fb_id})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"] == "Friend not found."

    def test_delete_friend_not_authorized(self):
        #create friend to delete
        fb_id = self.test_user1["fb_id"]
        friend = {"user_id":self.test_user1["id"],
                  "friend_user_id":self.test_user2["id"]}
        resp = self.app.post("/friends",data=friend,
                             headers={"Authorization":fb_id})
        friend = json.loads(resp.data)["value"]

        #delete friend
        fb_id = self.test_user1["fb_id"]
        resp = self.app.delete("/friends/%d" % friend["id"],
                               headers={"Authorization":fb_id + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"] == "Not Authorized."
