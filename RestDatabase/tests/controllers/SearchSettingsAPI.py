from tests.utils.FitPalsTestCase import *

class SearchSettingsApiTestCase(FitPalsTestCase):
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
        fb_id = self.test_user1["fb_id"]
        setting_id = self.test_user1["search_settings_id"]
        resp = self.app.put("/search_settings/%d" % setting_id,
                            data={"men_only":0, "women_only":1},
                            headers={"Authorization":fb_id})
        assert resp.status_code == 202
        assert json.loads(resp.data)["message"] == "Search settings updated."
        assert json.loads(resp.data)["value"]["men_only"] == False
        assert json.loads(resp.data)["value"]["women_only"] == True

        #ensure that test_user websocket self.websocket_client1 got new user update
        received = self.websocket_client1.get_received()
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
