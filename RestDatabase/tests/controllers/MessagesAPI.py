from tests.utils.FitPalsTestCase import *

class MessagesApiTestCase(FitPalsTestCase):
    def test_get_message_threads(self):
        #create thread to get
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"user2_id":self.test_user2["id"]})

        #get threads
        resp = self.app.get("/message_threads?user2_id=%s"\
                             % self.test_user1["fb_id"],
                             headers={"Authorization":self.test_user1["fb_id"]})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"] == "Message threads found."
        received_thread = json.loads(resp.data)["value"]
        assert type(received_thread[0]["id"]) == type(int())
        assert received_thread[0]["user1_id"] == self.test_user1["id"]
        assert received_thread[0]["user2_id"] == self.test_user2["id"]

    def test_get_message_threads_invalid_auth_token(self):
        resp = self.app.get("/message_threads?user2_id=%s"\
                             % self.test_user1["fb_id"],
                             headers={"Authorization":
                                      self.test_user1["fb_id"] + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"] == "Not Authorized."

    def test_create_message_thread(self):
        #log in test_user1 to chat web socket
        client = socketio.test_client(app)
        client.emit("join", self.test_user1)

        #make request
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"user2_id":self.test_user2["id"]})
        received_thread = json.loads(resp.data)["value"]
        
        #ensure request worked correctly
        assert resp.status_code==201
        value = json.loads(resp.data)["value"]
        assert value["user1_id"] == self.test_user1["id"]
        assert value["user2_id"] == self.test_user2["id"]
        assert type(value["id"]) == int
        
        #ensure that test_user1 websocket client got update
        received = client.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "message_thread_created"
        
    def test_create_message_thread_invalid_fb_id(self):
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fb_id"] + "junk"},
                             data={"user2_id":self.test_user2["id"]})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."
        
    def test_create_message_thread_no_user2(self):
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"user2_id":-1})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="user2_id not found."
        
    def test_delete_message_thread(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]

        #delete thread for user 1
        resp = self.app.delete("/message_threads/%d" % thread_id,
                             headers={"Authorization":self.test_user1["fb_id"]})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Message thread deleted."
        
        #ensure that test_user1 websocket self.websocket_client1 got update
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "message_thread_deleted"

        #ensure thread is still present for user 2
        resp = self.app.get("/messages?message_thread_id=%d" % thread_id,
                            headers={"Authorization":self.test_user2["fb_id"]})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Messages found."

        #delete thread for user 2
        resp = self.app.delete("/message_threads/%d" % thread_id,
                             headers={"Authorization":self.test_user2["fb_id"]})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Message thread deleted."
                            
        #ensure thread is deleted
        resp = self.app.get("/messages?message_thread_id=%d" % thread_id,
                            headers={"Authorization":self.test_user2["fb_id"]})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Message thread not found."
        
    def test_delete_message_thread_invalid_auth_token(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]

        #attempt thread delete
        resp = self.app.delete("/message_threads/%d" % thread_id,
                             headers={"Authorization":
                                      self.test_user1["fb_id"] + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_delete_message_thread_not_found(self):
        #attempt thread delete
        resp = self.app.delete("/message_threads/0",
                             headers={"Authorization":
                                      self.test_user1["fb_id"]})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Message thread not found."
        
    def test_delete_message_thread_not_authorized(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]

        #attempt thread delete
        resp = self.app.delete("/message_threads/%d" % thread_id,
                             headers={"Authorization":
                                      self.test_user3["fb_id"]})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_get_messages(self):
        #create thread
        resp = self.app.post("/message_threads?since=0",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]
        
        message = {"message_thread_id":thread_id,
                   "body":"sup",
                   "direction":0}
        #create message in thread
        resp = self.app.post("/messages",
                             data=message,
                             headers={"Authorization":self.test_user1["fb_id"]})

        #get messages for user
        resp = self.app.get("/messages?message_thread_id=%d" % thread_id,
                             headers={"Authorization":self.test_user1["fb_id"]})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Messages found."
        message_received = json.loads(resp.data)["value"][0]
        assert type(message_received["id"]) == type(int())
        assert type(datetime.fromtimestamp(message_received["time"])) == datetime
        for key in message.keys():
            assert message_received[key] == message[key]
        
    def test_get_messages_thread_not_found(self):
        #get messages for user
        resp = self.app.get("/messages?message_thread_id=%d" % -1,
                             headers={"Authorization":self.test_user1["fb_id"]})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Message thread not found."
        
    def test_get_messages_invalid_auth_token(self):
        #get messages for user
        resp = self.app.get("/messages?message_thread_id=%d" % -1,
                             headers={"Authorization":
                                      self.test_user1["fb_id"] + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."
        
    def test_get_messages_not_authorized(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]

        #get messages for user
        resp = self.app.get("/messages?message_thread_id=%d" % thread_id,
                             headers={"Authorization":
                                      self.test_user3["fb_id"]})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_create_message(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]

        #ensure message was created correctly
        message = {"message_thread_id":thread_id,
                   "direction":0,
                   "body":"yo dawg"}
        resp = self.app.post("/messages",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data=message)
        assert resp.status_code == 201
        assert json.loads(resp.data)["message"]=="Message created."
        message_received = json.loads(resp.data)["value"]
        assert type(message_received["id"]) == type(int())
        assert type(datetime.fromtimestamp(message_received["time"])) == datetime
        for key in message.keys():
            assert message_received[key] == message[key]

        #ensure that test_user1 websocket client got new message
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "message_received"
        assert received[-1]['args'][0] == message_received

        #ensure that test_user2 websocket client got new message
        received = self.websocket_client2.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "message_received"
        assert received[-1]['args'][0] == message_received
        
    def test_create_message_invalid_auth_token(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]

        #create message
        resp = self.app.post("/messages",
                             headers={"Authorization":self.test_user1["fb_id"] + "junk"},
                             data={"message_thread_id":thread_id,
                                   "direction":0,
                                   "body":"yo dawg"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."
        
    def test_create_message_not_found(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"user2_id":self.test_user2["id"]})
        
        #create message
        resp = self.app.post("/messages",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"message_thread_id":-1,
                                   "direction":0,
                                   "body":"yo dawg"})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Message thread not found."

    def test_create_message_not_authorized(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]
        
        #create message
        resp = self.app.post("/messages",
                             headers={"Authorization":self.test_user2["fb_id"]},
                             data={"message_thread_id":thread_id,
                                   "direction":0,
                                   "body":"yo dawg"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."
        
    def test_create_message_for_closed_thread(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]
        thread = MessageThread.query.get(thread_id)
        thread.user2_deleted = True
        db.session.commit()
        
        #create message
        resp = self.app.post("/messages",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"message_thread_id":thread_id,
                                   "direction":0,
                                   "body":"yo dawg"})
        assert resp.status_code==403
        assert json.loads(resp.data)["message"]=="Message thread has been closed."
