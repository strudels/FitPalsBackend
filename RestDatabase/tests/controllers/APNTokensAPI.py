import unittest
import simplejson as json
from app import app,db
from app.models import *

class APNTokensApiTestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

        self.test_user = User.query.filter(User.fb_id=="fbTestUser1").first()
        if not self.test_user:
            self.test_user = User("fbTestUser1")
            db.session.add(self.test_user)
            db.session.commit()

    def tearDown(self):
        if hasattr(self, "test_user"):
            db.session.delete(self.test_user)
            db.session.commit()

    def test_add_apn_token(self):
        fb_id = self.test_user.fb_id
        db.session.add(self.test_user)
        resp = self.app.post("/users/" + str(self.test_user.id) + "/apn_tokens",
                             data={"token":"some apn token"},
                             headers={"Authorization":fb_id})
        db.session.commit()
        assert resp.status_code==201 #user created

    def test_add_apn_token_unauthorized(self):
        fb_id = self.test_user.fb_id
        db.session.add(self.test_user)
        resp = self.app.post("/users/" + str(self.test_user.id) + "/apn_tokens",
                             data={"token":"some apn token"},
                             headers={"Authorization": fb_id + "junk"})
        db.session.commit()
        assert resp.status_code==401 #user created

    def test_delete_apn_tokens(self):
        fb_id = self.test_user.fb_id
        self.test_user.apn_tokens.append(APNToken(self.test_user,"some apn token"))
        db.session.commit()
        resp = self.app.delete("/users/" + str(self.test_user.id) + "/apn_tokens",
                               headers={"Authorization": fb_id})
        db.session.commit()
        assert resp.status_code==200

    def test_delete_apn_tokens_unauthorized(self):
        fb_id = self.test_user.fb_id
        self.test_user.apn_tokens.append(APNToken(self.test_user,"some apn token"))
        db.session.commit()
        resp = self.app.delete("/users/" + str(self.test_user.id) + "/apn_tokens",
                               headers={"Authorization": fb_id + "junk"})
        db.session.commit()
        assert resp.status_code==401

    def test_delete_one_apn_token(self):
        fb_id = self.test_user.fb_id
        self.test_user.apn_tokens.append(APNToken(self.test_user,"some apn token"))
        db.session.commit()
        token = self.test_user.apn_tokens.first()
        resp = self.app.delete("/users/" + str(self.test_user.id) + "/apn_tokens",
                               data={"token":token.token},
                               headers={'Content-Type': 'application/x-www-form-urlencoded',
                                        "Authorization":fb_id})
        print "delete_one: ", resp.data
        assert resp.status_code==200
