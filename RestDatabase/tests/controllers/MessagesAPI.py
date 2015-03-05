import unittest
import simplejson as json
from app import app,db
from app.models import *

class MessagesApiTestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

        self.test_user1 = User.query.filter(User.fb_id=="fbTestUser1").first()
        if not self.test_user1:
            self.test_user1 = User("fbTestUser1")
            db.session.add(self.test_user1)
            db.session.commit()

        self.test_user2 = User.query.filter(User.fb_id=="fbTestUser2").first()
        if not self.test_user2:
            self.test_user2 = User("fbTestUser2")
            db.session.add(self.test_user2)
            db.session.commit()

    def tearDown(self):
        if hasattr(self, "test_user1"):
            db.session.delete(self.test_user1)
            db.session.commit()
        if hasattr(self, "test_user2"):
            db.session.delete(self.test_user2)
            db.session.commit()

    def test_create_message_thread(self):
        test_user1_id = self.test_user1.id
        test_user2_id = self.test_user2.id
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1.fb_id},
                             data={"user2_id":self.test_user2.id})
        assert resp.status_code==201
        value = json.loads(resp.data)["value"]
        assert value["user1_id"] == test_user1_id
        assert value["user2_id"] == test_user2_id
        thread_id = value["id"]
        db.session.delete(MessageThread.query.get(thread_id))
        db.session.commit()
        
    def test_create_message_thread_invalid_fb_id(self):
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1.fb_id + "junk"},
                             data={"user2_id":self.test_user2.id})
        assert resp.status_code==400
        assert json.loads(resp.data)["message"]=="Invalid Authorization Token."
        
    def test_create_message_thread_no_user2(self):
        resp = self.app.post("/message_threads",
                             headers={"Authorization":self.test_user1.fb_id},
                             data={"user2_id":1})
        assert resp.status_code==400
        assert json.loads(resp.data)["message"]=="user2_id does not exist."

    """
    def test_get_messages(self):
        resp = self.app.get("/users/" + str(self.test_user1.id)\
            + "/messages/" + str(self.test_user2.id),
            headers={"Authorization":self.test_user1.fb_id})
        assert resp.status_code==200 #user created

    def test_get_messages_unauthorized(self):
        resp = self.app.get("/users/" + str(self.test_user1.id)\
            + "/messages/" + str(self.test_user2.id),
            headers={"Authorization":self.test_user1.fb_id + "junk"})
        assert resp.status_code==401 #user created

    def test_delete_messages(self):
        resp = self.app.delete("/users/" + str(self.test_user1.id)\
            + "/messages/" + str(self.test_user2.id),
            headers={'Content-Type': 'application/x-www-form-urlencoded',
                     "Authorization":self.test_user1.fb_id})
        assert resp.status_code==200

    def test_delete_messages_unauthorized(self):
        resp = self.app.delete("/users/" + str(self.test_user1.id)\
            + "/messages/" + str(self.test_user2.id),
            headers={'Content-Type': 'application/x-www-form-urlencoded',
                     "Authorization":self.test_user1.fb_id + "junk"})
        assert resp.status_code==401
    """
