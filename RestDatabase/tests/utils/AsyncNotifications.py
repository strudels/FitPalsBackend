import unittest
import simplejson as json
from app import app,db,reset_app
from app.models import *
from datetime import date
from app.utils.AsyncNotifications import send_message

class AsyncNotificationsTestCase(unittest.TestCase):
    def setUp(self):
        reset_app()
        app.testing = True
        self.app = app.test_client()
        
        #test_user1 and test_user2 are facebook friends
        #create test_user1
        self.test_user1 = User("1380493978943440","fbTestUser1",
                               dob=date(1990,1,1),name="Ben")
        db.session.add(self.test_user1)
        device = Device(self.test_user1,"keDu6Piunk9TNL1fKgffX8b8sKCy/OmSGZGKvizNQw8=")
        db.session.add(device)
        db.session.commit()
        self.test_user1 = self.test_user1.dict_repr(public=False)

    def tearDown(self):
        reset_app()
        
    def test_apns_send(self):
        send_message(User.query.get(self.test_user1["id"]),"test_event")
        db.session.close()
        
    def test_websocket_send(self):
        #log in test_user1 to chat web socket
        self.websocket_client1 = socketio.test_client(app)
        self.websocket_client1.emit("join", self.test_user1)
        send_message(User.query.get(self.test_user1["id"]),"test_event")
        db.session.close()
