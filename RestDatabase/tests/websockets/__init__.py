import unittest
from app import app,socketio
from app.models import *

class WebSocketTestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.chat_client = socketio.test_client(app, namespace="/chat")
        self.chat_client.get_received("/chat")
        self.sync_client = socketio.test_client(app, namespace="/sync")
        self.sync_client.get_received("/sync")

        self.test_user = User.query.filter(User.fb_id=="fbTestUser1").first()
        if not self.test_user:
            self.test_user = User("fbTestUser1")
            db.session.add(self.test_user)
            db.session.commit()

    def tearDown(self):
        if hasattr(self, "test_user"):
            db.session.delete(self.test_user)
            db.session.commit()

    def test_websocket_connect_chat(self):
        client = socketio.test_client(app, namespace="/chat")
        received = client.get_received("/chat")
        assert len(received) == 1
        client.disconnect(namespace="/chat")
        
    def test_websocket_join_chat(self):
        #ensure client does not receive messages before joining chat room
        socketio.emit("user_update", self.test_user.dict_repr(),\
                      room=str(self.test_user.id) + "-chat",
                      namespace="/chat")
        received = self.chat_client.get_received("/chat")
        assert len(received) == 0

        #ensure client can join chat room
        self.chat_client.emit("join", self.test_user.dict_repr(public=False),\
                              namespace="/chat")
        received = self.chat_client.get_received("/chat")
        assert len(received) == 1
        assert received[0]["name"] ==\
            "joined_room"

        #ensure client receives messages after joining chat room
        socketio.emit("user_update", self.test_user.dict_repr(),\
                      room=str(self.test_user.id) + "-chat",
                      namespace="/chat")
        received = self.chat_client.get_received("/chat")
        assert len(received) == 1
        assert received[0]["name"] ==\
            "user_update"
        
        #disconnect client
        self.chat_client.disconnect(namespace="/chat")
    
    def test_websocket_connect_sync(self):
        client = socketio.test_client(app, namespace="/sync")
        received = client.get_received("/sync")
        assert len(received) == 1
        client.disconnect(namespace="/sync")

    def test_websocket_join_sync(self):
        #ensure client does not receive messages before joining chat room
        socketio.emit("user_update", self.test_user.dict_repr(),\
                      room=str(self.test_user.id) + "-sync",
                      namespace="/sync")
        received = self.sync_client.get_received("/sync")
        assert len(received) == 0

        #ensure client can join chat room
        self.sync_client.emit("join", self.test_user.dict_repr(public=False),\
                              namespace="/sync")
        received = self.sync_client.get_received("/sync")
        assert len(received) == 1
        assert received[0]["name"] ==\
            "joined_room"

        #ensure client receives messages after joining chat room
        socketio.emit("user_update", self.test_user.dict_repr(),\
                      room=str(self.test_user.id) + "-sync",
                      namespace="/sync")
        received = self.sync_client.get_received("/sync")
        assert len(received) == 1
        assert received[0]["name"] ==\
            "user_update"
        
        #disconnect client
        self.sync_client.disconnect(namespace="/sync")
