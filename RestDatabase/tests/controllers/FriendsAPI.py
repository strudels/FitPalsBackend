from tests.utils.FitPalsTestCase import *

class APNTokensApiTestCase(FitPalsTestCase):
    def test_add_friend(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        friend = {"id":self.test_user2["id"]}
        resp = self.app.post("/friends",data=friend,
                             headers={"Authorization":fitpals_secret})
        assert resp.status_code == 201
        assert json.loads(resp.data)["message"] == "Friend added."
        received_friend = json.loads(resp.data)["value"]
        del self.test_user2["password"]
        del self.test_user2["fitpals_secret"]
        self.test_user2["online"] = True
        assert self.test_user2 == received_friend

    def test_add_friend_user_not_found(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        friend = {"id":0}
        resp = self.app.post("/friends",data=friend,
                             headers={"Authorization":fitpals_secret})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"] == "User not found."
   
    def test_add_friend_not_authorized(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        friend = {"id":self.test_user2["id"]}
        resp = self.app.post("/friends",data=friend,
                             headers={"Authorization":fitpals_secret + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"] == "Not Authorized."
        
    def test_get_friends(self):
        #create friend to get
        fitpals_secret = self.test_user1["fitpals_secret"]
        friend = {"id":self.test_user2["id"]}
        resp = self.app.post("/friends",data=friend,
                             headers={"Authorization":fitpals_secret})
        friend = json.loads(resp.data)["value"]
        
        #get friend
        resp = self.app.get("/friends",headers={"Authorization":fitpals_secret})
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"] == "Friends found."
        friends = json.loads(resp.data)["value"]
        assert len(friends) == 1
        assert friend == friends[0]
        
    def test_get_friends_not_authorized(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.get("/friends",headers={"Authorization":fitpals_secret+"junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"] == "Not Authorized."

    def test_delete_friend(self):
        #create friend to delete
        fitpals_secret = self.test_user1["fitpals_secret"]
        friend = {"id":self.test_user2["id"]}
        resp = self.app.post("/friends",data=friend,
                             headers={"Authorization":fitpals_secret})
        friend = json.loads(resp.data)["value"]
        
        #delete friend
        resp = self.app.delete("/friends/%d" % friend["id"],
                               headers={"Authorization":fitpals_secret})
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"] == "Friend deleted."
        
        #ensure that friend was deleted
        resp = self.app.get("/friends",headers={"Authorization":fitpals_secret})
        friends = json.loads(resp.data)["value"]
        assert len(friends) == 0
        
    def test_delete_friend_not_found(self):
        #delete friend
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.delete("/friends/%d" % 0,
                               headers={"Authorization":fitpals_secret})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"] == "Friend not found."

    def test_delete_friend_not_authorized(self):
        #create friend to delete
        fitpals_secret = self.test_user1["fitpals_secret"]
        friend = {"id":self.test_user2["id"]}
        resp = self.app.post("/friends",data=friend,
                             headers={"Authorization":fitpals_secret})
        friend = json.loads(resp.data)["value"]

        #delete friend
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.delete("/friends/%d" % friend["id"],
                               headers={"Authorization":fitpals_secret + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"] == "Not Authorized."
