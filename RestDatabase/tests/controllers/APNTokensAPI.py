import unittest
import simplejson as json
from app import app,db
from app.models import *

class APNTokensApiTestCase(unittest.TestCase):
    def setUp(self):
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
            data={"fb_id":fb_id, "token":"some apn token"})
        db.session.commit()
        assert resp.status_code==201 #user created

    def test_delete_apn_tokens(self):
        fb_id = self.test_user.fb_id
        self.test_user.apn_tokens.append(APNToken(self.test_user,"some apn token"))
        db.session.commit()
        resp = self.app.delete("/users/" + str(self.test_user.id) + "/apn_tokens",
            data={"fb_id":fb_id},
            headers={'Content-Type': 'application/x-www-form-urlencoded'})
        db.session.commit()
        assert resp.status_code==200

    def test_delete_one_apn_token(self):
        fb_id = self.test_user.fb_id
        self.test_user.apn_tokens.append(APNToken(self.test_user,"some apn token"))
        db.session.commit()
        token = self.test_user.apn_tokens.first()
        resp = self.app.delete("/users/" + str(self.test_user.id) + "/apn_tokens",
            data={"fb_id":fb_id, "token":token.token},
            headers={'Content-Type': 'application/x-www-form-urlencoded'})
        assert resp.status_code==200
