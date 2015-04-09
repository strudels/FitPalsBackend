from tests.utils.FitPalsTestCase import *

class SearchSettingsApiTestCase(FitPalsTestCase):
    def test_get_search_settings(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        setting_id = self.test_user1["search_settings_id"]
        user_id = self.test_user1["id"]
        setting = {"id":setting_id,
                   "user_id":self.test_user1["id"],
                   "friends_only":False,
                   "men_only":False,
                   "women_only":False,
                   "age_lower_limit":18,
                   "age_upper_limit":130,
                   "radius":1,
                   "radius_unit":"mile"}
        resp = self.app.get("/search_settings?user_id=%d" % user_id,
                            headers={"Authorization":fitpals_secret})
        assert resp.status_code == 200
        assert json.loads(resp.data)["message"] == "Search settings found."
        assert json.loads(resp.data)["value"] == setting

    def test_get_search_settings_not_found(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        setting_id = 0
        resp = self.app.get("/search_settings?user_id=%d" % setting_id,
                            headers={"Authorization":fitpals_secret})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"] == "User not found."

    def test_update_search_settings(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        setting_id = self.test_user1["search_settings_id"]

        #get settings previous state
        resp = self.app.get("/search_settings?user_id=%d"%self.test_user1["id"],
                            headers={"Authorization":fitpals_secret})
        settings = json.loads(resp.data)["value"]

        #update settings
        resp = self.app.put("/search_settings/%d" % settings["id"],
                            data={"men_only":0, "women_only":1,
                                  "radius":12,"radius_unit":"kilometer"},
                            headers={"Authorization":fitpals_secret})
        assert resp.status_code == 202
        assert json.loads(resp.data)["message"] == "Search settings updated."
        settings["men_only"] = False
        settings["women_only"] = True
        settings["radius"] = 12
        settings["radius_unit"] = "kilometer"
        assert json.loads(resp.data)["value"] == settings

        #ensure that test_user websocket self.websocket_client1 got new user update
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["args"][0]["path"] == "/search_settings/%d" % setting_id
        assert received[-1]["args"][0]["http_method"] == "PUT"
        assert received[-1]["args"][0]["value"] == json.loads(resp.data)["value"]
        
    def test_update_search_settings_not_found(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        setting_id = 0
        resp = self.app.put("/search_settings/%d" % setting_id,
                            data={"men_only":0, "women_only":1},
                            headers={"Authorization":fitpals_secret})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"] == "Search settings not found."
        
    def test_update_search_settings_not_authorized(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        setting_id = self.test_user1["search_settings_id"]
        resp = self.app.put("/search_settings/%d" % setting_id,
                            data={"men_only":0, "women_only":1},
                            headers={"Authorization":fitpals_secret + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"] == "Not Authorized."
