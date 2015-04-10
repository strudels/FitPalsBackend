import unittest
import simplejson as json
from app import app,db,socketio,reset_app
from app.models import *
from datetime import date
from app.utils import Facebook
import requests
from app.utils import AsyncNotifications
from time import sleep

def _get_access_tokens(fb_id, password):
    url = "https://graph.facebook.com/v2.3/645422265578276/accounts/test-users"
    resp = requests.get(url)
    known_test_fb_ids = ["1380493978943440",
                         "1390508901271602",
                         "1420288438286360",
                         "1377938879200557"]
    test_users = [x for x in json.loads(resp.text)["data"]\
                  if x["id"] in known_test_fb_ids]

class FitPalsTestCase(unittest.TestCase):
    def setUp(self):
        reset_app()
        app.testing = True
        self.app = app.test_client()
        
        #get access tokens for test users
        self.access_tokens = {x["id"]:x["access_token"] for x in Facebook.get_test_users()}
        
        #test_user1 and test_user2 are facebook friends
        #create test_user1
        self.test_user1 = User("1380493978943440","fbTestUser1",
                               gender="male",dob=date(1990,1,1),name="Ben")
        db.session.add(self.test_user1)
        db.session.commit()
        self.test_user1 = self.test_user1.dict_repr(public=False)

        #create test_user2
        self.test_user2 = User("1390508901271602","fbTestUser2",
                               gender="male",dob=date(1990,1,1),name="Ricky")
        db.session.add(self.test_user2)
        db.session.commit()
        self.test_user2 = self.test_user2.dict_repr(public=False)
            
        #create test_user3
        self.test_user3 = User("1420288438286360","fbTestUser3",gender="female",
                               dob=date(1990,1,1))
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
