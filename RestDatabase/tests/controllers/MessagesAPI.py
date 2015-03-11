import unittest
import simplejson as json
from app import app,db,socketio,reset_app
from app.models import *
from datetime import date

class MessagesApiTestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

        self.test_user1 = User.query.filter(User.fb_id=="fbTestUser1").first()
        if not self.test_user1:
            self.test_user1 = User("fbTestUser1",dob=date(1990,1,1))
            db.session.add(self.test_user1)
            db.session.commit()
            self.test_user1 = self.test_user1.dict_repr(public=False)

        self.test_user2 = User.query.filter(User.fb_id=="fbTestUser2").first()
        if not self.test_user2:
            self.test_user2 = User("fbTestUser2",dob=date(1990,1,1))
            db.session.add(self.test_user2)
            db.session.commit()
            self.test_user2 = self.test_user2.dict_repr(public=False)
            
        self.test_user3 = User.query.filter(User.fb_id=="fbTestUser3").first()
        if not self.test_user3:
            self.test_user3 = User("fbTestUser3",dob=date(1990,1,1))
            db.session.add(self.test_user3)
            db.session.commit()
            self.test_user3 = self.test_user3.dict_repr(public=False)

    def tearDown(self):
        reset_app()
        
    def test_get_message_threads(self):
        resp = self.app.get("/message_threads?user2_id=%s"\
                             % self.test_user1["fb_id"],
                             headers={"Authorization":self.test_user1["fb_id"]})
        assert resp.status_code==200

    def test_get_message_threads_invalid_auth_token(self):
        resp = self.app.get("/message_threads?user2_id=%s"\
                             % self.test_user1["fb_id"],
                             headers={"Authorization":
                                      self.test_user1["fb_id"] + "junk"})
        assert resp.status_code==400

    def test_create_message_thread(self):
        #log in test_user1 to chat web socket
        client = socketio.test_client(app)
        client.emit("join", self.test_user1)

        #make request
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"user2_id":self.test_user2["id"]})
        
        #ensure request worked correctly
        assert resp.status_code==201
        value = json.loads(resp.data)["value"]
        assert value["user1_id"] == self.test_user1["id"]
        assert value["user2_id"] == self.test_user2["id"]
        thread_id = value["id"]
        
        #ensure that test_user1 websocket client got update
        received = client.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "message_thread_created"
        
    def test_create_message_thread_invalid_fb_id(self):
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fb_id"] + "junk"},
                             data={"user2_id":self.test_user2["id"]})
        assert resp.status_code==400
        assert json.loads(resp.data)["message"]=="Invalid Authorization Token."
        
    def test_create_message_thread_no_user2(self):
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"user2_id":-1})
        assert resp.status_code==400
        assert json.loads(resp.data)["message"]=="user2_id does not exist."
        
    def test_delete_message_thread(self):
        #log in test_user1 to chat web socket
        client = socketio.test_client(app)
        client.emit("join", self.test_user1)

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
        
        #ensure that test_user1 websocket client got update
        received = client.get_received()
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
        assert resp.status_code==400
        assert json.loads(resp.data)["message"]=="Invalid Authorization Token."

    def test_delete_message_thread_not_found(self):
        #attempt thread delete
        resp = self.app.delete("/message_threads/0",
                             headers={"Authorization":
                                      self.test_user1["fb_id"]})
        assert resp.status_code==400
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
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]

        #get messages for user
        resp = self.app.get("/messages?message_thread_id=%d" % thread_id,
                             headers={"Authorization":self.test_user1["fb_id"]})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Messages found."
        
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
        assert resp.status_code==400
        assert json.loads(resp.data)["message"]=="Invalid Authorization Token."
        
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
        #log in test_user1 to chat web socket
        client1 = socketio.test_client(app)
        client1.emit("join", self.test_user1)

        #log in test_user2 to chat web socket
        client2 = socketio.test_client(app)
        client2.emit("join", self.test_user2)

        #create thread
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"user2_id":self.test_user2["id"]})
        thread_id = json.loads(resp.data)["value"]["id"]

        #ensure message was created correctly
        resp = self.app.post("/messages",
                             headers={"Authorization":self.test_user1["fb_id"]},
                             data={"message_thread_id":thread_id,
                                   "direction":0,
                                   "body":"yo dawg"})
        assert resp.status_code == 201

        #ensure that test_user1 websocket client got new message
        received = client1.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "message_received"

        #ensure that test_user2 websocket client got new message
        received = client2.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "message_received"
        
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
        assert resp.status_code==400
        assert json.loads(resp.data)["message"]=="Invalid Authorization Token."
        
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
        assert resp.status_code==400
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
        assert resp.status_code==400
        assert json.loads(resp.data)["message"]=="Message thread has been closed."
