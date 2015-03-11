from tests.utils.FitPalsTestCase import *

class ActivitySettingsAPITestCase(FitPalsTestCase):
    def test_get_activities(self):
        resp = self.app.get("/activities")
        assert resp.status_code==200
        assert json.loads(resp.data)["message"] == "Activites found."
        activity = json.loads(resp.data)["value"][0]
        
        #These values are based off of the reset_app() function in app/__init__.py
        assert activity["id"] == 1
        assert activity["name"] == "running"
        assert activity["questions"][0]["id"] == 1
        assert activity["questions"][0]["activity_id"] == 1
        assert activity["questions"][0]["question"] == "How much time do you want to spend running?"
        assert activity["questions"][1]["id"] == 2
        assert activity["questions"][1]["activity_id"] == 1
        assert activity["questions"][1]["question"] == "How far do you want to run?"
    
    def test_get_activity_settings(self):
        #create activity setting to get
        fb_id = self.test_user1["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":activity["questions"][0]["id"],
                                     "lower_value":8.3,
                                     "upper_value":20.6,},
                             headers = {"Authorization":fb_id})

        #get activity settings
        resp =\
            self.app.get("/activity_settings", headers={"Authorization":fb_id})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Activity settings found."
        setting = json.loads(resp.data)["value"][0]
        assert setting["id"]==1
        assert setting["user_id"]==self.test_user1["id"]
        assert setting["question_id"] == activity["questions"][0]["id"]
        assert setting["lower_value"] == 8.3
        assert setting["upper_value"] == 20.6

    def test_get_activitys_setting_user_not_found(self):
        fb_id = self.test_user1["fb_id"]
        resp =\
            self.app.get("/activity_settings",
                         headers={"Authorization":fb_id + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."
        
    def test_create_activity_setting(self):
        #create activity
        fb_id = self.test_user1["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":activity["questions"][0]["id"],
                                     "lower_value":8.3,
                                     "upper_value":20.6,},
                             headers = {"Authorization":fb_id})
        assert resp.status_code==201
        assert json.loads(resp.data)["message"]=="Activity setting created."
        setting = json.loads(resp.data)["value"]
        assert setting["id"]==1
        assert setting["user_id"]==self.test_user1["id"]
        assert setting["question_id"] == activity["questions"][0]["id"]
        assert setting["lower_value"] == 8.3
        assert setting["upper_value"] == 20.6

        #ensure that test_user1 websocket self.websocket_client1 got update
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "activity_setting_added"
        assert received[-1]["args"][0] == setting
        
    def test_create_activity_setting_question_not_found(self):
        fb_id = self.test_user1["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":0,
                                     "lower_value":8.3,
                                     "upper_value":20.6,},
                             headers = {"Authorization":fb_id})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Question not found."

    def test_create_activity_setting_user_not_found(self):
        fb_id = self.test_user1["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":0,
                                     "question_id":activity["questions"][0]["id"],
                                     "lower_value":8.3,
                                     "upper_value":20.6,},
                             headers = {"Authorization":fb_id})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="User not found."
        
    def test_create_activity_setting_not_authorized(self):
        fb_id = self.test_user1["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":activity["questions"][0]["id"],
                                     "lower_value":8.3,
                                     "upper_value":20.6,},
                             headers = {"Authorization":fb_id + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_create_activity_setting_cant_create(self):
        fb_id = self.test_user1["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":activity["questions"][0]["id"],
                                     "lower_value":8.3,
                                     "upper_value":2.6,},
                             headers = {"Authorization":fb_id})
        assert resp.status_code==400
        assert json.loads(resp.data)["message"]=="Could not create activity setting."
        
    def test_get_activity_setting(self):
        #create setting
        fb_id = self.test_user1["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":activity["questions"][0]["id"],
                                     "lower_value":8.3,
                                     "upper_value":20.6,},
                             headers = {"Authorization":fb_id})
        setting_id = json.loads(resp.data)["value"]["id"]

        #get setting
        resp = self.app.get("/activity_settings/%d" % setting_id,
                            headers={"Authorization":fb_id})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Activity setting found."
        setting = json.loads(resp.data)["value"]
        assert setting["id"] == 1
        assert setting["user_id"]==self.test_user1["id"]
        assert setting["question_id"] == activity["questions"][0]["id"]
        assert setting["lower_value"] == 8.3
        assert setting["upper_value"] == 20.6
        
    def test_get_activity_setting_not_found(self):
        #get setting
        fb_id = self.test_user1["fb_id"]
        resp = self.app.get("/activity_settings/%d" % 0,
                            headers={"Authorization":fb_id})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Activity setting not found."
        
    def test_get_activity_setting_not_authorized(self):
        #create setting
        fb_id = self.test_user1["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":activity["questions"][0]["id"],
                                     "lower_value":8.3,
                                     "upper_value":20.6,},
                             headers = {"Authorization":fb_id})
        setting_id = json.loads(resp.data)["value"]["id"]
        
        #get setting
        resp = self.app.get("/activity_settings/%d" % setting_id,
                            headers={"Authorization":fb_id + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_update_activity_setting(self):
        #create setting
        fb_id = self.test_user1["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":activity["questions"][0]["id"],
                                     "lower_value":8.3,
                                     "upper_value":20.6,},
                             headers = {"Authorization":fb_id})
        setting_id = json.loads(resp.data)["value"]["id"]
        
        #update setting
        resp = self.app.put("/activity_settings/%d" % setting_id,
                            data={"lower_value":4.6, "upper_value":5.7},
                            headers={"Authorization":fb_id})
        assert resp.status_code==202
        assert json.loads(resp.data)["message"]=="Activity setting updated."

        #ensure that test_user1 websocket self.websocket_client1 got update
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "activity_setting_updated"

    def test_update_activity_setting_not_found(self):
        fb_id = self.test_user1["fb_id"]
        #update setting
        resp = self.app.put("/activity_settings/%d" % 0,
                            data={"lower_value":4.6, "upper_value":5.7},
                            headers={"Authorization":fb_id})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Activity setting not found."

    def test_update_activity_setting_not_authorized(self):
        #create setting
        fb_id = self.test_user1["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":activity["questions"][0]["id"],
                                     "lower_value":8.3,
                                     "upper_value":20.6,},
                             headers = {"Authorization":fb_id})
        setting_id = json.loads(resp.data)["value"]["id"]
        
        #update setting
        resp = self.app.put("/activity_settings/%d" % setting_id,
                            data={"lower_value":4.6, "upper_value":5.7},
                            headers={"Authorization":fb_id + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_update_activity_setting_could_not_update(self):
        #create setting
        fb_id = self.test_user1["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":activity["questions"][0]["id"],
                                     "lower_value":8.3,
                                     "upper_value":20.6,},
                             headers = {"Authorization":fb_id})
        setting_id = json.loads(resp.data)["value"]["id"]
        
        #update setting
        resp = self.app.put("/activity_settings/%d" % setting_id,
                            data={"lower_value":4.6, "upper_value":3.7},
                            headers={"Authorization":fb_id})
        assert resp.status_code==400
        assert json.loads(resp.data)["message"]=="Could not update activity setting."
        
    def test_delete_activity_setting(self):
        #create setting
        fb_id = self.test_user1["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":activity["questions"][0]["id"],
                                     "lower_value":8.3,
                                     "upper_value":20.6,},
                             headers = {"Authorization":fb_id})
        setting_id = json.loads(resp.data)["value"]["id"]

        #delete setting
        resp = self.app.delete("/activity_settings/%d" % setting_id,
                               headers={"Authorization":fb_id})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Activity setting deleted."

        #ensure that test_user1 websocket self.websocket_client1 got update
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "activity_setting_deleted"

    def test_delete_activity_setting_not_found(self):
        fb_id = self.test_user1["fb_id"]
        resp = self.app.delete("/activity_settings/%d" % 0,
                               headers={"Authorization":fb_id})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Activity setting not found."
        
    def test_delete_activity_setting_not_authorized(self):
        #create setting
        fb_id = self.test_user1["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":activity["questions"][0]["id"],
                                     "lower_value":8.3,
                                     "upper_value":20.6,},
                             headers = {"Authorization":fb_id})
        setting_id = json.loads(resp.data)["value"]["id"]

        #delete setting
        resp = self.app.delete("/activity_settings/%d" % setting_id,
                               headers={"Authorization":fb_id})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Activity setting deleted."
