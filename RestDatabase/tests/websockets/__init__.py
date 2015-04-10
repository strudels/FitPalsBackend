import unittest
from app import app,socketio,reset_app
from app.models import *
from datetime import date
from time import sleep

class WebSocketTestCase(unittest.TestCase):
    def setUp(self):
        reset_app()
        app.testing = True
        self.client = socketio.test_client(app)
        sleep(0.01) #so that the async thread has time to send the message
        self.client.get_received()

        self.test_user = User("fbTestUser1","fbTestUser1",gender="male",dob=date(1990,1,1))
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        reset_app()

    def test_websocket_connect(self):
        client = socketio.test_client(app)
        sleep(0.01) #so that the async thread has time to send the message
        received = client.get_received()
        assert len(received) == 1
        client.disconnect()
        
    def test_websocket_join_room(self):
        #ensure client does not receive messages before joining chat room
        socketio.emit("user_update", self.test_user.dict_repr(),\
                      room=str(self.test_user.id))
        sleep(0.01) #so that the async thread has time to send the message
        received = self.client.get_received()
        assert len(received) == 0

        #ensure client can join chat room
        self.client.emit("join", self.test_user.dict_repr(public=False))
        sleep(0.01) #so that the async thread has time to send the message
        received = self.client.get_received()
        assert len(received) != 0
        assert received[-1]["name"] ==\
            "joined_room"

        #ensure client receives messages after joining chat room
        socketio.emit("user_update", self.test_user.dict_repr(),\
                      room=str(self.test_user.id))
        sleep(0.01) #so that the async thread has time to send the message
        received = self.client.get_received()
        assert len(received) != 0
        assert received[-1]["name"] ==\
            "user_update"
        
        #disconnect client
        self.client.disconnect()
