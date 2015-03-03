import unittest
import simplejson as json
from app import app,db,socketio
from app.models import *

class WebSocketTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_websocket_connect_chat(self):
        app.testing = True
        client = socketio.test_client(app, namespace="/chat")
        received = client.get_received("/chat")
        assert len(received) == 1
        client.disconnect(namespace="/chat")
    
    def test_websocket_connect_sync(self):
        app.testing = True
        client = socketio.test_client(app, namespace="/sync")
        received = client.get_received("/sync")
        assert len(received) == 1
        client.disconnect(namespace="/sync")
