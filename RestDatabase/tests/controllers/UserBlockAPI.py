from tests.utils.FitPalsTestCase import *

class UserBlockTestCase(FitPalsTestCase):
    def test_add_block(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/user_blocks",
                             data={"blocked_user_id":self.test_user2["id"]},
                             headers={"Authorization":fitpals_secret})
        assert resp.status_code==201
        assert json.loads(resp.data)["message"]=="User block created."
        block = json.loads(resp.data)["value"]
        assert type(block["id"]) == int
        assert block["user_id"] == self.test_user1["id"]
        assert block["blocked_user_id"] == self.test_user2["id"]

        #ensure that test_user1 websocket self.websocket_client1 got update
        sleep(0.01) #so that the async thread has time to send the message
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["args"][0]["path"] == "/user_blocks"
        assert received[-1]["args"][0]["http_method"] == "POST"
        assert received[-1]["args"][0]["value"] == block
        
    def test_add_block_not_authorized(self):
        fitpals_secret = self.test_user1["fitpals_secret"] + "junk"
        resp = self.app.post("/user_blocks",
                             data={"blocked_user_id":self.test_user2["id"]},
                             headers={"Authorization":fitpals_secret})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"]=="Not Authorized."
        
    def test_add_block_user_not_found(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/user_blocks",
                             data={"blocked_user_id":0},
                             headers={"Authorization":fitpals_secret})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"]=="User not found."
        
    def test_get_blocks(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/user_blocks",
                             data={"blocked_user_id":self.test_user2["id"]},
                             headers={"Authorization":fitpals_secret})
        
        resp = self.app.get("/user_blocks",
                             headers={"Authorization":fitpals_secret})
        blocks = json.loads(resp.data)["value"]
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"] == "User blocks found."
        assert len(blocks) == 1
        assert blocks[0]["user_id"] == self.test_user1["id"]
        assert blocks[0]["blocked_user_id"] == self.test_user2["id"]
        
    def test_get_blocks_not_authorized(self):
        fitpals_secret = self.test_user1["fitpals_secret"] + "junk"
        resp = self.app.get("/user_blocks",
                             headers={"Authorization":fitpals_secret})
        assert resp.status_code == 401
        
    def test_delete_block(self):
        #create block
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/user_blocks",
                             data={"blocked_user_id":self.test_user2["id"]},
                             headers={"Authorization":fitpals_secret})
        block = json.loads(resp.data)["value"]
        
        #delete block
        resp = self.app.delete("/user_blocks/%d" % block["id"],
                               headers={"Authorization":fitpals_secret})
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"]=="User block removed."
        
        resp = self.app.get("/user_blocks",
                             headers={"Authorization":fitpals_secret})
        blocks = json.loads(resp.data)["value"]
        assert type(blocks[0]["unblock_time"]) == int

        #ensure that test_user1 websocket self.websocket_client1 got update
        sleep(0.01) #so that the async thread has time to send the message
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["args"][0]["path"] == "/user_blocks/%d" % block["id"]
        assert received[-1]["args"][0]["http_method"] == "DELETE"
        assert received[-1]["args"][0]["value"] == blocks[0]
        
    def test_delete_block_not_authorized_no_user_with_secret(self):
        #create block
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/user_blocks",
                             data={"blocked_user_id":self.test_user2["id"]},
                             headers={"Authorization":fitpals_secret})
        block = json.loads(resp.data)["value"]

        fitpals_secret = self.test_user1["fitpals_secret"] + "junk"
        resp = self.app.delete("/user_blocks/%d" % block["id"],
                               headers={"Authorization":fitpals_secret})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_delete_block_not_authorized_to_delete(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/user_blocks",
                             data={"blocked_user_id":self.test_user2["id"]},
                             headers={"Authorization":fitpals_secret})
        block = json.loads(resp.data)["value"]

        fitpals_secret2 = self.test_user2["fitpals_secret"]
        resp = self.app.delete("/user_blocks/%d" % block["id"],
                               headers={"Authorization":fitpals_secret2})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_delete_block_not_found(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.delete("/user_blocks/%d" % 0,
                               headers={"Authorization":fitpals_secret})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"]=="User block not found."
        
