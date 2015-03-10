import unittest
import simplejson as json
from app import app,db,socketio,reset_app
from app.models import *
from datetime import date

class SearchSettingsApiTestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

        self.test_user1 = User.query.filter(User.fb_id=="fbTestUser1").first()
        if not self.test_user1:
            self.test_user1 = User("fbTestUser1",dob=date(1990,1,1))
            db.session.add(self.test_user1)
            db.session.commit()
            self.test_user1 = self.test_user1.dict_repr(public=False)
    def tearDown(self):
        reset_app()
        
    def test_get_search_settings(self):
        fb_id = self.test_user1["fb_id"]
        setting_id = self.test_user1["search_settings_id"]
        resp = self.app.get("/search_settings/%d" % setting_id,
                            headers={"Authorization":fb_id})
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"] == "Search settings found."

    def test_get_search_settings_not_found(self):
        fb_id = self.test_user1["fb_id"]
        setting_id = 0
        resp = self.app.get("/search_settings/%d" % setting_id,
                            headers={"Authorization":fb_id})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"] == "Search settings not found."
        
    def test_get_search_settings_not_authorized(self):
        fb_id = self.test_user1["fb_id"]
        setting_id = self.test_user1["search_settings_id"]
        resp = self.app.get("/search_settings/%d" % setting_id,
                            headers={"Authorization":fb_id + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"] == "Not Authorized."

    def test_update_search_settings(self):
        #log in test_user1 to chat web socket
        client = socketio.test_client(app)
        client.emit("join", self.test_user1)

        fb_id = self.test_user1["fb_id"]
        setting_id = self.test_user1["search_settings_id"]
        resp = self.app.put("/search_settings/%d" % setting_id,
                            data={"men_only":0, "women_only":1},
                            headers={"Authorization":fb_id})
        assert resp.status_code == 202
        assert json.loads(resp.data)["message"] == "Search settings updated."
        assert json.loads(resp.data)["value"]["men_only"] == False
        assert json.loads(resp.data)["value"]["women_only"] == True

        #ensure that test_user websocket client got new user update
        received = client.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "search_settings_update"
        assert received[-1]["args"][0] == json.loads(resp.data)["value"]
        
    def test_update_search_settings_not_found(self):
        fb_id = self.test_user1["fb_id"]
        setting_id = 0
        resp = self.app.put("/search_settings/%d" % setting_id,
                            data={"men_only":0, "women_only":1},
                            headers={"Authorization":fb_id})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"] == "Search settings not found."
        
    def test_update_search_settings_not_authorized(self):
        fb_id = self.test_user1["fb_id"]
        setting_id = self.test_user1["search_settings_id"]
        resp = self.app.put("/search_settings/%d" % setting_id,
                            data={"men_only":0, "women_only":1},
                            headers={"Authorization":fb_id + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"] == "Not Authorized."
