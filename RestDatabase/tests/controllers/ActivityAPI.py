from tests.utils.FitPalsTestCase import *

class ActivitySettingsAPITestCase(FitPalsTestCase):
    def test_get_activities(self):
        resp = self.app.get("/activities")
        assert resp.status_code==200
        assert json.loads(resp.data)["message"] == "Activites found."
        activity = json.loads(resp.data)["value"][0]
        
        #These values are based off of the reset_app() function in app/__init__.py
        assert activity["id"] == 1
        assert activity["name"] == "Walking"
        assert activity["active_image"] == "IcnWalking.png"
        assert activity["inactive_image"] == "IcnWalkingInactive.png"
        
    def test_get_questions(self):
        resp = self.app.get("/questions")
        assert resp.status_code==200
        assert json.loads(resp.data)["message"] == "Questions found."
        assert len(json.loads(resp.data)["value"]) > 0
    
    def test_get_activity_settings(self):
        #create activity setting to get
        fitpals_secret = self.test_user1["fitpals_secret"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        questions = json.loads(self.app.get("/questions").data)["value"]
        questions = [q for q in questions if q["activity_id"]==activity["id"]]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":questions[0]["id"],
                                     "lower_value":15.3,
                                     "upper_value":18.6,
                                     "unit_type":"minute"},
                             headers = {"Authorization":fitpals_secret})

        #get activity settings
        resp =\
            self.app.get("/activity_settings", headers={"Authorization":fitpals_secret})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Activity settings found."
        setting = json.loads(resp.data)["value"][0]
        assert setting["id"]==1
        assert setting["user_id"]==self.test_user1["id"]
        assert setting["question_id"] == questions[0]["id"]
        assert round(setting["lower_value"],1) == 15.3
        assert round(setting["upper_value"],1) == 18.6
        assert setting["unit_type"] == "minute"

    def test_get_activitys_setting_user_not_found(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp =\
            self.app.get("/activity_settings",
                         headers={"Authorization":fitpals_secret + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."
        
    def test_create_activity_setting(self):
        #create activity
        fitpals_secret = self.test_user1["fitpals_secret"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        questions = json.loads(self.app.get("/questions").data)["value"]
        questions = [q for q in questions if q["activity_id"]==activity["id"]]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":questions[0]["id"],
                                     "lower_value":15.3,
                                     "upper_value":18.6,
                                     "unit_type":"minute"},
                             headers = {"Authorization":fitpals_secret})
        assert resp.status_code==201
        assert json.loads(resp.data)["message"]=="Activity setting created."
        setting = json.loads(resp.data)["value"]
        assert setting["id"]==1
        assert setting["user_id"]==self.test_user1["id"]
        assert setting["question_id"] == questions[0]["id"]
        assert round(setting["lower_value"],1) == 15.3
        assert round(setting["upper_value"],1) == 18.6
        assert setting["unit_type"] == "minute"

        #ensure that test_user1 websocket self.websocket_client1 got update
        sleep(0.01) #so that the async thread has time to send the message
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["args"][0]["path"] == "/activity_settings"
        assert received[-1]["args"][0]["http_method"] == "POST"
        assert received[-1]["args"][0]["value"] == setting
        
    def test_create_activity_setting_question_not_found(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":0,
                                     "lower_value":15.3,
                                     "upper_value":18.6,
                                     "unit_type":"minute"},
                             headers = {"Authorization":fitpals_secret})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Question not found."

    def test_create_activity_setting_user_not_found(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        questions = json.loads(self.app.get("/questions").data)["value"]
        questions = [q for q in questions if q["activity_id"]==activity["id"]]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":0,
                                     "question_id":questions[0]["id"],
                                     "lower_value":15.3,
                                     "upper_value":18.6,
                                     "unit_type":"minute"},
                             headers = {"Authorization":fitpals_secret})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="User not found."
        
    def test_create_activity_setting_not_authorized(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        questions = json.loads(self.app.get("/questions").data)["value"]
        questions = [q for q in questions if q["activity_id"]==activity["id"]]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":questions[0]["id"],
                                     "lower_value":15.3,
                                     "upper_value":18.6,
                                     "unit_type":"minute"},
                             headers = {"Authorization":fitpals_secret + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_create_activity_setting_cant_create(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        questions = json.loads(self.app.get("/questions").data)["value"]
        questions = [q for q in questions if q["activity_id"]==activity["id"]]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":questions[0]["id"],
                                     "lower_value":15.3,
                                     "upper_value":2.6,
                                     "unit_type":"minute"},
                             headers = {"Authorization":fitpals_secret})
        assert resp.status_code==400
        assert json.loads(resp.data)["message"]=="Activity setting data invalid."
        
    def test_get_activity_setting(self):
        #create setting
        fitpals_secret = self.test_user1["fitpals_secret"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        questions = json.loads(self.app.get("/questions").data)["value"]
        questions = [q for q in questions if q["activity_id"]==activity["id"]]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":questions[0]["id"],
                                     "lower_value":15.3,
                                     "upper_value":18.6,
                                     "unit_type":"minute"},
                             headers = {"Authorization":fitpals_secret})
        setting_id = json.loads(resp.data)["value"]["id"]

        #get setting
        resp = self.app.get("/activity_settings/%d" % setting_id,
                            headers={"Authorization":fitpals_secret})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Activity setting found."
        setting = json.loads(resp.data)["value"]
        assert setting["id"] == 1
        assert setting["user_id"]==self.test_user1["id"]
        assert setting["question_id"] == questions[0]["id"]
        assert round(setting["lower_value"],1) == 15.3
        assert round(setting["upper_value"],1) == 18.6
        assert setting["unit_type"] == "minute"
        
    def test_get_activity_setting_not_found(self):
        #get setting
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.get("/activity_settings/%d" % 0,
                            headers={"Authorization":fitpals_secret})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Activity setting not found."
        
    def test_get_activity_setting_not_authorized(self):
        #create setting
        fitpals_secret = self.test_user1["fitpals_secret"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        questions = json.loads(self.app.get("/questions").data)["value"]
        questions = [q for q in questions if q["activity_id"]==activity["id"]]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":questions[0]["id"],
                                     "lower_value":15.3,
                                     "upper_value":18.6,
                                     "unit_type":"minute"},
                             headers = {"Authorization":fitpals_secret})
        setting_id = json.loads(resp.data)["value"]["id"]
        
        #get setting
        resp = self.app.get("/activity_settings/%d" % setting_id,
                            headers={"Authorization":fitpals_secret + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_update_activity_setting(self):
        #create setting
        fitpals_secret = self.test_user1["fitpals_secret"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        questions = json.loads(self.app.get("/questions").data)["value"]
        questions = [q for q in questions if q["activity_id"]==activity["id"]]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":questions[0]["id"],
                                     "lower_value":15.3,
                                     "upper_value":18.6,
                                     "unit_type":"minute"},
                             headers = {"Authorization":fitpals_secret})
        setting_id = json.loads(resp.data)["value"]["id"]
        
        #update setting
        resp = self.app.put("/activity_settings/%d" % setting_id,
                            data={"lower_value":15.8, "upper_value":22.4},
                            headers={"Authorization":fitpals_secret})
        assert resp.status_code==202
        assert json.loads(resp.data)["message"]=="Activity setting updated."
        setting = json.loads(resp.data)["value"]
        assert setting["id"] == 1
        assert setting["user_id"]==self.test_user1["id"]
        assert setting["question_id"] == questions[0]["id"]
        assert round(setting["lower_value"],1) == 15.8
        assert round(setting["upper_value"],1) == 22.4

        #ensure that test_user1 websocket self.websocket_client1 got update
        sleep(0.01) #so that the async thread has time to send the message
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["args"][0]["path"] == "/activity_settings/%d" % setting_id
        assert received[-1]["args"][0]["http_method"] == "PUT"
        assert received[-1]["args"][0]["value"] == setting

    def test_update_activity_setting_not_found(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        #update setting
        resp = self.app.put("/activity_settings/%d" % 0,
                            data={"lower_value":4.6, "upper_value":5.7},
                            headers={"Authorization":fitpals_secret})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Activity setting not found."

    def test_update_activity_setting_not_authorized(self):
        #create setting
        fitpals_secret = self.test_user1["fitpals_secret"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        questions = json.loads(self.app.get("/questions").data)["value"]
        questions = [q for q in questions if q["activity_id"]==activity["id"]]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":questions[0]["id"],
                                     "lower_value":15.3,
                                     "upper_value":18.6,
                                     "unit_type":"minute"},
                             headers = {"Authorization":fitpals_secret})
        setting_id = json.loads(resp.data)["value"]["id"]
        
        #update setting
        resp = self.app.put("/activity_settings/%d" % setting_id,
                            data={"lower_value":4.6, "upper_value":5.7},
                            headers={"Authorization":fitpals_secret + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_update_activity_setting_could_not_update(self):
        #create setting
        fitpals_secret = self.test_user1["fitpals_secret"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        questions = json.loads(self.app.get("/questions").data)["value"]
        questions = [q for q in questions if q["activity_id"]==activity["id"]]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":questions[0]["id"],
                                     "lower_value":15.3,
                                     "upper_value":18.6,
                                     "unit_type":"minute"},
                             headers = {"Authorization":fitpals_secret})
        setting_id = json.loads(resp.data)["value"]["id"]
        
        #update setting
        resp = self.app.put("/activity_settings/%d" % setting_id,
                            data={"lower_value":4.6, "upper_value":3.7},
                            headers={"Authorization":fitpals_secret})
        assert resp.status_code==400
        assert json.loads(resp.data)["message"]=="Activity setting data invalid."
        
    def test_delete_activity_setting(self):
        #create setting
        fitpals_secret = self.test_user1["fitpals_secret"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        questions = json.loads(self.app.get("/questions").data)["value"]
        questions = [q for q in questions if q["activity_id"]==activity["id"]]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":questions[0]["id"],
                                     "lower_value":15.3,
                                     "upper_value":18.6,
                                     "unit_type":"minute"},
                             headers = {"Authorization":fitpals_secret})
        setting_id = json.loads(resp.data)["value"]["id"]

        #delete setting
        resp = self.app.delete("/activity_settings/%d" % setting_id,
                               headers={"Authorization":fitpals_secret})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Activity setting deleted."

        #ensure that test_user1 websocket self.websocket_client1 got update
        sleep(0.01) #so that the async thread has time to send the message
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["args"][0]["path"] == "/activity_settings/%d" % setting_id
        assert received[-1]["args"][0]["http_method"] == "DELETE"
        assert received[-1]["args"][0]["value"] == None

    def test_delete_activity_setting_not_found(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.delete("/activity_settings/%d" % 0,
                               headers={"Authorization":fitpals_secret})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Activity setting not found."
        
    def test_delete_activity_setting_not_authorized(self):
        #create setting
        fitpals_secret = self.test_user1["fitpals_secret"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        questions = json.loads(self.app.get("/questions").data)["value"]
        questions = [q for q in questions if q["activity_id"]==activity["id"]]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user1["id"],
                                     "question_id":questions[0]["id"],
                                     "lower_value":15.3,
                                     "upper_value":18.6,
                                     "unit_type":"minute"},
                             headers = {"Authorization":fitpals_secret})
        setting_id = json.loads(resp.data)["value"]["id"]

        #delete setting
        resp = self.app.delete("/activity_settings/%d" % setting_id,
                               headers={"Authorization":fitpals_secret})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Activity setting deleted."

        #ensure setting id was deleted
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.get("/activity_settings/%d" % setting_id,
                            headers={"Authorization":fitpals_secret})
        assert resp.status_code==404
