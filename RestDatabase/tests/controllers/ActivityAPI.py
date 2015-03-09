import unittest
import simplejson as json
from app import app,db,socketio,reset_app
from app.models import *

class ActivitiesApiTestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_get_activities(self):
        resp = self.app.get("/activities")
        assert resp.status_code==200

class ActivitySettingsAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

        self.test_user = User.query.filter(User.fb_id=="fbTestUser1").first()
        if not self.test_user:
            self.test_user = User("fbTestUser1")
            db.session.add(self.test_user)
            db.session.commit()
        self.test_user_private = self.test_user.dict_repr(public=False)
        self.test_user = self.test_user.dict_repr()

    def tearDown(self):
        reset_app()
    
    def test_get_activity_settings(self):
        resp =\
            self.app.get("/activity_settings?user_id=%d" % self.test_user["id"])
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Activity settings found."

    def test_get_activitys_setting_user_not_found(self):
        resp =\
            self.app.get("/activity_settings?user_id=%d" % 0)
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="User not found."
        
    def test_create_activity_setting(self):
        #log in test_user1 to chat web socke
        client = socketio.test_client(app)
        client.emit("join", self.test_user_private)

        #create activity
        fb_id = self.test_user_private["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user["id"],
                                     "question_id":activity["questions"][0]["id"],
                                     "lower_value":8.3,
                                     "upper_value":20.6,},
                             headers = {"Authorization":fb_id})
        assert resp.status_code==201
        assert json.loads(resp.data)["message"]=="Activity setting created."

        #ensure that test_user1 websocket client got update
        received = client.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "activity_setting_added"
        
    def test_create_activity_setting_question_not_found(self):
        fb_id = self.test_user_private["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user["id"],
                                     "question_id":0,
                                     "lower_value":8.3,
                                     "upper_value":20.6,},
                             headers = {"Authorization":fb_id})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Question not found."

    def test_create_activity_setting_user_not_found(self):
        fb_id = self.test_user_private["fb_id"]
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
        fb_id = self.test_user_private["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user["id"],
                                     "question_id":activity["questions"][0]["id"],
                                     "lower_value":8.3,
                                     "upper_value":20.6,},
                             headers = {"Authorization":fb_id + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_create_activity_setting_cant_create(self):
        fb_id = self.test_user_private["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user["id"],
                                     "question_id":activity["questions"][0]["id"],
                                     "lower_value":8.3,
                                     "upper_value":2.6,},
                             headers = {"Authorization":fb_id})
        assert resp.status_code==400
        assert json.loads(resp.data)["message"]=="Could not create activity setting."
        
    def test_get_activity_setting(self):
        #create setting
        fb_id = self.test_user_private["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user["id"],
                                     "question_id":activity["questions"][0]["id"],
                                     "lower_value":8.3,
                                     "upper_value":20.6,},
                             headers = {"Authorization":fb_id})
        setting_id = json.loads(resp.data)["value"]["id"]

        #get setting
        resp = self.app.get("/activity_settings/%d" % setting_id)
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Activity setting found."
        
    def test_get_activity_setting_not_found(self):
        #get setting
        resp = self.app.get("/activity_settings/%d" % 0)
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Activity setting not found."
        

    def test_update_activity_setting(self):
        #log in test_user1 to chat web socke
        client = socketio.test_client(app)
        client.emit("join", self.test_user_private)

        #create setting
        fb_id = self.test_user_private["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user["id"],
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

        #ensure that test_user1 websocket client got update
        received = client.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "activity_setting_updated"

    def test_update_activity_setting_not_found(self):
        fb_id = self.test_user_private["fb_id"]
        #update setting
        resp = self.app.put("/activity_settings/%d" % 0,
                            data={"lower_value":4.6, "upper_value":5.7},
                            headers={"Authorization":fb_id})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Activity setting not found."

    def test_update_activity_setting_not_authorized(self):
        #create setting
        fb_id = self.test_user_private["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user["id"],
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
        fb_id = self.test_user_private["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user["id"],
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
        #log in test_user1 to chat web socke
        client = socketio.test_client(app)
        client.emit("join", self.test_user_private)

        #create setting
        fb_id = self.test_user_private["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user["id"],
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

        #ensure that test_user1 websocket client got update
        received = client.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "activity_setting_deleted"

    def test_delete_activity_setting_not_found(self):
        fb_id = self.test_user_private["fb_id"]
        resp = self.app.delete("/activity_settings/%d" % 0,
                               headers={"Authorization":fb_id})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Activity setting not found."
        
    def test_delete_activity_setting_not_authorized(self):
        #create setting
        fb_id = self.test_user_private["fb_id"]
        activity = json.loads(self.app.get("/activities").data)["value"][0]
        resp = self.app.post("/activity_settings",
                             data = {"user_id":self.test_user["id"],
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
