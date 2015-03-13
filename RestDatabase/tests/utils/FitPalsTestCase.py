import unittest
import simplejson as json
from app import app,db,socketio,reset_app
from app.models import *
from datetime import date

class FitPalsTestCase(unittest.TestCase):
    def setUp(self):
        reset_app()
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

        #log in test_user1 to chat web socket
        self.websocket_client1 = socketio.test_client(app)
        self.websocket_client1.emit("join", self.test_user1)

        #log in test_user2 to chat web socket
        self.websocket_client2 = socketio.test_client(app)
        self.websocket_client2.emit("join", self.test_user2)

        #log in test_user3 to chat web socket
        self.websocket_client3 = socketio.test_client(app)
        self.websocket_client3.emit("join", self.test_user3)

    def tearDown(self):
        reset_app()
