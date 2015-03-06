import unittest
from app import app,socketio
from app.models import *

class WebSocketTestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = socketio.test_client(app)
        self.client.get_received()

        self.test_user = User.query.filter(User.fb_id=="fbTestUser1").first()
        if not self.test_user:
            self.test_user = User("fbTestUser1")
            db.session.add(self.test_user)
            db.session.commit()

    def tearDown(self):
        if hasattr(self, "test_user"):
            db.session.delete(self.test_user)
            db.session.commit()

    def test_websocket_connect(self):
        client = socketio.test_client(app)
        received = client.get_received()
        assert len(received) == 1
        client.disconnect()
        
    def test_websocket_join_room(self):
        #ensure client does not receive messages before joining chat room
        socketio.emit("user_update", self.test_user.dict_repr(),\
                      room=str(self.test_user.id))
        received = self.client.get_received()
        assert len(received) == 0

        #ensure client can join chat room
        self.client.emit("join", self.test_user.dict_repr(public=False))
        received = self.client.get_received()
        assert len(received) != 0
        assert received[-1]["name"] ==\
            "joined_room"

        #ensure client receives messages after joining chat room
        socketio.emit("user_update", self.test_user.dict_repr(),\
                      room=str(self.test_user.id))
        received = self.client.get_received()
        assert len(received) != 0
        assert received[-1]["name"] ==\
            "user_update"
        
        #disconnect client
        self.client.disconnect()
