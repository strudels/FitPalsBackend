from tests.utils.FitPalsTestCase import *

class MessagesApiTestCase(FitPalsTestCase):
    def test_get_message_threads(self):
        #create thread to get
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})

        #get threads
        resp = self.app.get("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"] == "Message threads found."
        received_thread = json.loads(resp.data)["value"]
        assert type(received_thread[0]["id"]) == type(int())
        assert received_thread[0]["user1_id"] == self.test_user1["id"]
        assert received_thread[0]["user2_id"] == self.test_user2["id"]

        #get threads for user2
        resp = self.app.get("/message_threads",
                             headers={"Authorization":self.test_user2["fitpals_secret"]})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"] == "Message threads found."
        received_thread = json.loads(resp.data)["value"]
        assert type(received_thread[0]["id"]) == type(int())
        assert received_thread[0]["user1_id"] == self.test_user1["id"]
        assert received_thread[0]["user2_id"] == self.test_user2["id"]

    def test_get_message_threads_invalid_auth_token(self):
        resp = self.app.get("/message_threads",
                             headers={"Authorization":
                                      self.test_user1["fitpals_secret"] + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"] == "Not Authorized."

    def test_create_message_thread(self):
        #log in test_user1 to chat web socket
        client = socketio.test_client(app)
        client.emit("join", self.test_user1)

        #make request
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        received_thread = json.loads(resp.data)["value"]
        
        #ensure request worked correctly
        assert resp.status_code==201
        value = json.loads(resp.data)["value"]
        assert value["user1_id"] == self.test_user1["id"]
        assert value["user2_id"] == self.test_user2["id"]
        assert type(value["id"]) == int
        
        #ensure that test_user1 websocket client got update
        sleep(0.01) #so that the async thread has time to send the message
        received = client.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "update"
        assert received[-1]["args"][0]["path"] == "/message_threads"
        assert received[-1]["args"][0]["http_method"] == "POST"
        assert received[-1]["args"][0]["value"] == received_thread

        #ensure that test_user2 websocket client got update
        received = self.websocket_client2.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "update"
        assert received[-1]["args"][0]["path"] == "/message_threads"
        assert received[-1]["args"][0]["http_method"] == "POST"
        assert received[-1]["args"][0]["value"] == received_thread
        
    def test_create_message_thread_invalid_fitpals_secret(self):
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"] + "junk"},
                             data={"user2_id":self.test_user2["id"]})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."
        
    def test_create_message_thread_no_user2(self):
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":-1})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="user2_id not found."
        
    def test_update_message_thread_user1(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        received_thread = json.loads(resp.data)["value"]
        
        assert received_thread["user1_has_unread"] == False
        assert received_thread["user2_has_unread"] == False
        
        #have user1 send message to user2
        resp = self.app.post("/messages",
                             data={"message_thread_id":received_thread["id"],
                                   "direction":0,
                                   "body":"sup"},
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        unread_message = json.loads(resp.data)["value"]
        
        #get thread to ensure that user2_has_unread has been set to True
        resp = self.app.get("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        threads = json.loads(resp.data)["value"]
        
        assert len(threads) == 1
        received_thread["user2_has_unread"] = True
        threads[0]["last_message"] = None
        assert threads[0] == received_thread
        
        #update message_thread to set thread.user2_has_unread back to false
        resp = self.app.put("/message_threads/%d" % threads[0]["id"],
                             headers={"Authorization":self.test_user2["fitpals_secret"]})
        updated_thread = json.loads(resp.data)["value"]
        
        received_thread["user2_has_unread"] = False
        updated_thread["last_message"] = None
        assert updated_thread == received_thread
        assert resp.status_code == 202
        assert json.loads(resp.data)["message"] == "Message thread updated."
        
        #get thread to ensure all changes have persisted
        resp = self.app.get("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        threads = json.loads(resp.data)["value"]
        
        assert len(threads) == 1
        threads[0]["last_message"] = None
        assert threads[0] == updated_thread
        
    def test_update_message_thread_user2(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        received_thread = json.loads(resp.data)["value"]
        
        assert received_thread["user1_has_unread"] == False
        assert received_thread["user2_has_unread"] == False
        
        #have user1 send message to user2
        resp = self.app.post("/messages",
                             data={"message_thread_id":received_thread["id"],
                                   "direction":0,
                                   "body":"sup"},
                             headers={"Authorization":self.test_user2["fitpals_secret"]})
        unread_message = json.loads(resp.data)["value"]
        
        #get thread to ensure that user2_has_unread has been set to True
        resp = self.app.get("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        threads = json.loads(resp.data)["value"]
        
        assert len(threads) == 1
        threads[0]["last_message"] = None
        assert threads[0] == received_thread
        
        #update message_thread to set thread.user1_has_unread back to false
        resp = self.app.put("/message_threads/%d" % threads[0]["id"],
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        updated_thread = json.loads(resp.data)["value"]
        
        received_thread["user1_has_unread"] = False
        updated_thread["last_message"] = None
        assert updated_thread == received_thread
        assert resp.status_code == 202
        assert json.loads(resp.data)["message"] == "Message thread updated."
        
        #get thread to ensure all changes have persisted
        resp = self.app.get("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        threads = json.loads(resp.data)["value"]
        
        assert len(threads) == 1
        threads[0]["last_message"] = None
        assert threads[0] == updated_thread
        
    def test_update_message_thread_not_authorized_bad_secret(self):
         #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        received_thread = json.loads(resp.data)["value"]
        
        assert received_thread["user1_has_unread"] == False
        assert received_thread["user2_has_unread"] == False
        
        #have user1 send message to user2
        resp = self.app.post("/messages",
                             data={"message_thread_id":received_thread["id"],
                                   "direction":0,
                                   "body":"sup"},
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        unread_message = json.loads(resp.data)["value"]
        
        #update message_thread to set thread.user2_has_unread back to false
        resp = self.app.put("/message_threads/%d" % received_thread["id"],
                             headers={"Authorization":self.test_user1["fitpals_secret"] + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"] == "Not Authorized."

    def test_update_message_thread_not_authorized_user_not_permitted(self):
         #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        received_thread = json.loads(resp.data)["value"]
        
        assert received_thread["user1_has_unread"] == False
        assert received_thread["user2_has_unread"] == False
        
        #have user1 send message to user2
        resp = self.app.post("/messages",
                             data={"message_thread_id":received_thread["id"],
                                   "direction":0,
                                   "body":"sup"},
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        unread_message = json.loads(resp.data)["value"]
        
        #update message_thread to set thread.user2_has_unread back to false
        resp = self.app.put("/message_threads/%d" % received_thread["id"],
                             headers={"Authorization":self.test_user3["fitpals_secret"]})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"] == "Not Authorized."
        
    def test_update_message_thread_not_found(self):
        resp = self.app.put("/message_threads/%d" % 0,
                             headers={"Authorization":self.test_user3["fitpals_secret"]})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"] == "Message thread not found."


        
    def test_delete_message_thread(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]
        
        #post message to thread
        resp = self.app.post("/messages",
                             data={"message_thread_id":thread_id,
                                   "direction":0,
                                   "body":"wat up"},
                             headers={"Authorization":self.test_user1["fitpals_secret"]})

        #delete thread for user 1
        resp = self.app.delete("/message_threads/%d" % thread_id,
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Message thread deleted."
        
        #ensure that test_user1 websocket self.websocket_client1 got update
        sleep(0.01) #so that the async thread has time to send the message
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "update"
        assert received[-1]["args"][0]["path"] == "/message_threads/%d" % thread_id
        assert received[-1]["args"][0]["http_method"] == "DELETE"
        assert received[-1]["args"][0]["value"] == None
        
        #ensure that GET /message_threads returns nothing for user1
        resp = self.app.get("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        assert len(json.loads(resp.data)["value"]) == 0
        
        #ensure that GET /messages returns nothing for user1
        resp = self.app.get("/messages",
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        assert len(json.loads(resp.data)["value"]) == 0

        #ensure that GET /message_threads still returns thread for user2
        resp = self.app.get("/message_threads",
                             headers={"Authorization":self.test_user2["fitpals_secret"]})
        assert len(json.loads(resp.data)["value"]) == 1

        #ensure that GET /messages returns 1 message for user2
        resp = self.app.get("/messages",
                             headers={"Authorization":self.test_user2["fitpals_secret"]})
        assert len(json.loads(resp.data)["value"]) == 1

        #recreate deleted thread to see if it still works
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        assert thread_id == json.loads(resp.data)["value"]["id"]
        
        #send a second message to the thread
        message = {"message_thread_id":thread_id,
                   "direction":1,
                   "body":"yo dawg"}
        resp = self.app.post("/messages",
                             headers={"Authorization":self.test_user2["fitpals_secret"]},
                             data=message)

        #ensure that GET /message_threads returns the thread for user1 again
        resp = self.app.get("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        assert len(json.loads(resp.data)["value"]) == 1
        
        #ensure that GET /messages returns 1 message for user1
        resp = self.app.get("/messages",
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        assert len(json.loads(resp.data)["value"]) == 1

        #ensure that GET /message_threads still returns thread for user2
        resp = self.app.get("/message_threads",
                             headers={"Authorization":self.test_user2["fitpals_secret"]})
        assert len(json.loads(resp.data)["value"]) == 1

        #ensure that GET /messages returns 2 message for user2
        resp = self.app.get("/messages",
                             headers={"Authorization":self.test_user2["fitpals_secret"]})
        assert len(json.loads(resp.data)["value"]) == 2

    def test_delete_message_thread_invalid_auth_token(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]

        #attempt thread delete
        resp = self.app.delete("/message_threads/%d" % thread_id,
                             headers={"Authorization":
                                      self.test_user1["fitpals_secret"] + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_delete_message_thread_not_found(self):
        #attempt thread delete
        resp = self.app.delete("/message_threads/0",
                             headers={"Authorization":
                                      self.test_user1["fitpals_secret"]})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Message thread not found."
        
    def test_delete_message_thread_not_authorized(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]

        #attempt thread delete
        resp = self.app.delete("/message_threads/%d" % thread_id,
                             headers={"Authorization":
                                      self.test_user3["fitpals_secret"]})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."
        
    def test_get_messages(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        thread1_id = json.loads(resp.data)["value"]["id"]

        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        thread2_id = json.loads(resp.data)["value"]["id"]
        
        for thread_id in [thread1_id,thread2_id]:
            message = {"message_thread_id":thread_id,
                    "body":"sup",
                    "direction":0}
            #create message in thread
            resp = self.app.post("/messages",
                                data=message,
                                headers={"Authorization":self.test_user1["fitpals_secret"]})

        #get messages for user
        resp = self.app.get("/messages",
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Messages found."
        messages_received = json.loads(resp.data)["value"]
        assert len(messages_received) == 2
        for message in messages_received:
            assert type(message["id"]) == type(int())
            assert type(datetime.fromtimestamp(message["time"])) == datetime
        
    def test_get_messages_since(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        thread1_id = json.loads(resp.data)["value"]["id"]

        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        thread2_id = json.loads(resp.data)["value"]["id"]
        
        times = []
        for thread_id in [thread1_id,thread2_id]:
            message = {"message_thread_id":thread_id,
                    "body":"sup",
                    "direction":0}
            #create message in thread
            resp = self.app.post("/messages",
                                data=message,
                                headers={"Authorization":self.test_user1["fitpals_secret"]})
            created_message = json.loads(resp.data)["value"]
            times.append(created_message["time"])

        #get messages for user
        resp = self.app.get("/messages?since=%d" % (times[-1] + 1),
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Messages found."
        messages_received = json.loads(resp.data)["value"]
        assert len(messages_received) == 0
 
    def test_get_messages_by_message_thread_id(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        thread1_id = json.loads(resp.data)["value"]["id"]

        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user3["id"]})
        thread2_id = json.loads(resp.data)["value"]["id"]
        
        for thread_id in [thread1_id,thread2_id]:
            message = {"message_thread_id":thread_id,
                    "body":"sup",
                    "direction":0}
            #create message in thread
            resp = self.app.post("/messages",
                                data=message,
                                headers={"Authorization":self.test_user1["fitpals_secret"]})

        #get messages for user
        resp = self.app.get("/messages?message_thread_id=%d" % thread1_id,
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Messages found."
        messages_received = json.loads(resp.data)["value"]
        assert len(messages_received) == 1
        for message in messages_received:
            assert type(message["id"]) == type(int())
            assert type(datetime.fromtimestamp(message["time"])) == datetime
            
    def test_get_messages_from_currently_blocked_user(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        thread1_id = json.loads(resp.data)["value"]["id"]
        
        #have user2 block user1
        resp = self.app.post("/user_blocks",
                             headers={"Authorization":self.test_user2["fitpals_secret"]},
                             data={"blocked_user_id":self.test_user1["id"]})
        
        #have user1 send a message to user2
        message = {"message_thread_id":thread1_id,
                "body":"sup",
                "direction":0}
        resp = self.app.post("/messages",
                            data=message,
                            headers={"Authorization":self.test_user1["fitpals_secret"]})
        
        #ensure that user2 did not receive message
        resp = self.app.get("/messages",
                            headers={"Authorization":self.test_user2["fitpals_secret"]})
        assert len(json.loads(resp.data)["value"]) == 0
        
    def test_get_messages_from_previously_blocked_user(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        thread1_id = json.loads(resp.data)["value"]["id"]
        
        #have user2 block user1
        resp = self.app.post("/user_blocks",
                             headers={"Authorization":self.test_user2["fitpals_secret"]},
                             data={"blocked_user_id":self.test_user1["id"]})
        block = json.loads(resp.data)["value"]
        #have user2 unblock user1
        resp = self.app.delete("/user_blocks/%d" % block["id"],
                             headers={"Authorization":self.test_user2["fitpals_secret"]})
        unblock = json.loads(resp.data)["value"]
        
        sleep(1) #make sure that time on server has progressed past blocking timespan
        #have user1 send a message to user2
        message = {"message_thread_id":thread1_id,
                "body":"sup",
                "direction":0}
        resp = self.app.post("/messages",
                            data=message,
                            headers={"Authorization":self.test_user1["fitpals_secret"]})
        
        #ensure that user2 did received message
        resp = self.app.get("/messages",
                            headers={"Authorization":self.test_user2["fitpals_secret"]})
        assert len(json.loads(resp.data)["value"]) == 1
           
    def test_get_messages_thread_not_found(self):
        #get messages for user
        resp = self.app.get("/messages?message_thread_id=%d" % -1,
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Message thread not found."
        
    def test_get_messages_invalid_auth_token(self):
        #get messages for user
        resp = self.app.get("/messages?message_thread_id=%d" % -1,
                             headers={"Authorization":
                                      self.test_user1["fitpals_secret"] + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."
        
    def test_get_messages_not_authorized(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]

        #get messages for user
        resp = self.app.get("/messages?message_thread_id=%d" % thread_id,
                             headers={"Authorization":
                                      self.test_user3["fitpals_secret"]})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_create_message(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]

        #ensure message was created correctly
        message = {"message_thread_id":thread_id,
                   "direction":0,
                   "body":"yo dawg"}
        resp = self.app.post("/messages",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data=message)
        assert resp.status_code == 201
        assert json.loads(resp.data)["message"]=="Message created."
        message_received = json.loads(resp.data)["value"]
        assert type(message_received["id"]) == type(int())
        assert type(datetime.fromtimestamp(message_received["time"])) == datetime
        for key in message.keys():
            assert message_received[key] == message[key]

        #ensure that test_user1 websocket client got new message
        sleep(0.01) #so that the async thread has time to send the message
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["args"][0]["path"] == "/messages"
        assert received[-1]["args"][0]["http_method"] == "POST"
        assert received[-1]["args"][0]["value"] == message_received

        #ensure that test_user2 websocket client got new message
        sleep(0.01) #so that the async thread has time to send the message
        received = self.websocket_client2.get_received()
        assert len(received) != 0
        assert received[-1]['args'][0]["path"] == "/messages"
        assert received[-1]["args"][0]["http_method"] == "POST"
        assert received[-1]["args"][0]["value"] == message_received
        
    def test_create_message_thread_user1_blocked(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]
        
        #have user2 block user1
        resp = self.app.post("/user_blocks",
                             headers={"Authorization":self.test_user2["fitpals_secret"]},
                             data={"blocked_user_id":self.test_user1["id"]})

        #clear user2's websocket receive queue
        sleep(0.1)
        received = self.websocket_client2.get_received()

        #create message
        message = {"message_thread_id":thread_id,
                   "direction":0,
                   "body":"yo dawg"}
        resp = self.app.post("/messages",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data=message)
        
        #ensure that user2 did not receive a message over websocket
        sleep(0.1)
        received = self.websocket_client2.get_received()
        assert len(received) == 0
        
    def test_create_message_thread_user2_blocked(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]
        
        #have user2 block user1
        resp = self.app.post("/user_blocks",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"blocked_user_id":self.test_user2["id"]})

        #clear user2's websocket receive queue
        sleep(0.1)
        received = self.websocket_client1.get_received()

        #create message
        message = {"message_thread_id":thread_id,
                   "direction":1,
                   "body":"yo dawg"}
        resp = self.app.post("/messages",
                             headers={"Authorization":self.test_user2["fitpals_secret"]},
                             data=message)
        
        #ensure that user2 did not receive a message over websocket
        sleep(0.1)
        received = self.websocket_client1.get_received()
        assert len(received) == 0
 
    def test_create_message_invalid_auth_token(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]

        #create message
        resp = self.app.post("/messages",
                             headers={"Authorization":self.test_user1["fitpals_secret"] + "junk"},
                             data={"message_thread_id":thread_id,
                                   "direction":0,
                                   "body":"yo dawg"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."
        
    def test_create_message_not_found(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        
        #create message
        resp = self.app.post("/messages",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"message_thread_id":-1,
                                   "direction":0,
                                   "body":"yo dawg"})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Message thread not found."

    def test_create_message_not_authorized(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]
        
        #create message
        resp = self.app.post("/messages",
                             headers={"Authorization":self.test_user2["fitpals_secret"]},
                             data={"message_thread_id":thread_id,
                                   "direction":0,
                                   "body":"yo dawg"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."
        
    def test_update_message(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        thread = json.loads(resp.data)["value"]

        #create message1(from user1 to user2)
        resp = self.app.post("/messages",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"message_thread_id":thread["id"],
                                   "direction":0,
                                   "body":"yo dawg"})
        message1 = json.loads(resp.data)["value"]
        message1["user2_read"] = True
        
        #create message2(from user2 to user1)
        resp = self.app.post("/messages",
                             headers={"Authorization":self.test_user2["fitpals_secret"]},
                             data={"message_thread_id":thread["id"],
                                   "direction":1,
                                   "body":"what up"})
        message2 = json.loads(resp.data)["value"]
        message2["user1_read"] = True
        
        #update message for user1
        resp = self.app.put("/messages/%d" % message2["id"],
                            headers={"Authorization":self.test_user1["fitpals_secret"]})
        assert resp.status_code == 202
        assert json.loads(resp.data)["message"] == "Message updated."
        message_received_user1 = json.loads(resp.data)["value"]
        assert message_received_user1 == message2
        
        #update message for user2
        resp = self.app.put("/messages/%d" % message1["id"],
                            headers={"Authorization":self.test_user2["fitpals_secret"]})
        assert resp.status_code == 202
        assert json.loads(resp.data)["message"] == "Message updated."
        message_received_user2 = json.loads(resp.data)["value"]
        assert message_received_user2 == message1
        
        #get message to ensure that message update persisted
        resp = self.app.get("/messages",
                            headers={"Authorization":self.test_user2["fitpals_secret"]})
        messages = json.loads(resp.data)["value"]
        assert len(messages) == 2
        assert messages[1] == message1
        assert messages[0] == message2
        
        #ensure that test_user1 websocket client got new message
        sleep(0.01) #so that the async thread has time to send the message
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]['args'][0]["path"] == "/messages/%d" % message2["id"]
        assert received[-1]["args"][0]["http_method"] == "PUT"
        assert received[-1]["args"][0]["value"] == message2
        
        #ensure that test_user2 websocket client got new message
        sleep(0.01) #so that the async thread has time to send the message
        received = self.websocket_client2.get_received()
        assert len(received) != 0
        assert received[-1]['args'][0]["path"] == "/messages/%d" % message1["id"]
        assert received[-1]["args"][0]["http_method"] == "PUT"
        assert received[-1]["args"][0]["value"] == message1
        
    def test_update_message_not_found(self):
        resp = self.app.put("/messages/0",
                            headers={"Authorization":self.test_user1["fitpals_secret"]})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"] == "Message not found."
        
    def test_update_message_not_authorized_user_not_found(self):
         #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        thread = json.loads(resp.data)["value"]

        #create message1(from user1 to user2)
        resp = self.app.post("/messages",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"message_thread_id":thread["id"],
                                   "direction":0,
                                   "body":"yo dawg"})
        message1 = json.loads(resp.data)["value"]
        message1["user2_read"] = True
       
        resp = self.app.put("/messages/%d" % message1["id"],
                             headers={"Authorization":self.test_user1["fitpals_secret"] + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"] == "Not Authorized."
        
    def test_update_message_not_authorized_wrong_user(self):
        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"user2_id":self.test_user2["id"]})
        thread = json.loads(resp.data)["value"]

        #create message1(from user1 to user2)
        resp = self.app.post("/messages",
                             headers={"Authorization":self.test_user1["fitpals_secret"]},
                             data={"message_thread_id":thread["id"],
                                   "direction":0,
                                   "body":"yo dawg"})
        message1 = json.loads(resp.data)["value"]
        message1["user2_read"] = True
        
        resp = self.app.put("/messages/%d" % message1["id"],
                             headers={"Authorization":self.test_user3["fitpals_secret"]})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"] == "Not Authorized."
