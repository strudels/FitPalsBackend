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
        
    def test_create_actitivy_setting(self):
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

    def test_create_actitivy_setting_user_not_found(self):
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
        
    def test_create_actitivy_setting_not_authorized(self):
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

    def test_create_actitivy_setting_cant_create(self):
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
    """
    def test_get_user_activities(self):
        resp = self.app.get("/users/" + str(self.test_user.id) + "/activity_settings")
        assert resp.status_code==200

    def test_add_user_activity(self):
        user_id = self.test_user.id
        fb_id = self.test_user.fb_id
        resp = self.app.post("/users/" + str(user_id) + "/activity_settings",
            data={
                "activity_id":1,
                "question_ids":[1,2],
                "answers":[30, 5000]
            }, headers= {"Authorization":fb_id})
        assert resp.status_code==201

    def test_add_user_activity_unauthorized(self):
        user_id = self.test_user.id
        fb_id = self.test_user.fb_id
        resp = self.app.post("/users/" + str(user_id) + "/activity_settings",
            data={
                "activity_id":1,
                "question_ids":[1,2],
                "answers":[30, 5000]
            }, headers= {"Authorization":fb_id + "junk"})
        assert resp.status_code==401

    def test_delete_user_activities(self):
        user_id = self.test_user.id
        fb_id = self.test_user.fb_id
        resp = self.app.delete("/users/" + str(user_id) + "/activity_settings",
            headers={'Content-Type': 'application/x-www-form-urlencoded',
                     "Authorization":fb_id})
        assert resp.status_code==200

    def test_delete_user_activities_unauthorized(self):
        user_id = self.test_user.id
        fb_id = self.test_user.fb_id
        resp = self.app.delete("/users/" + str(user_id) + "/activity_settings",
            headers={'Content-Type': 'application/x-www-form-urlencoded',
                     "Authorization":fb_id + "junk"})
        assert resp.status_code==401
    """

"""
class UserActivitySettingAPITestCase(unittest.TestCase):
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

    def test_get_user_activity(self):
        user_id = self.test_user.id
        fb_id = self.test_user.fb_id
        activity = Activity.query.get(1)
        setting = ActivitySetting(self.test_user,activity,activity.questions[0])
        self.test_user.activity_settings.append(setting)
        db.session.commit()
        resp = self.app.get("/users/" + str(user_id) + "/activity_settings")
        assert resp.status_code==200

    def test_update_user_activity(self):
        user_id = self.test_user.id
        fb_id = self.test_user.fb_id
        activity = Activity.query.get(1) #running
        setting = ActivitySetting(self.test_user,activity,activity.questions[0])
        self.test_user.activity_settings.append(setting)
        db.session.commit()
        resp = self.app.put("/users/" + str(user_id) +\
            "/activity_settings/" + str(activity.id),
            data = {
                "question_ids":[q.id for q in activity.questions],
                "answers":[1 for x in activity.questions]
            }, headers = {"Authorization":fb_id})
        assert resp.status_code==202

    def test_update_user_activity_unauthorized(self):
        user_id = self.test_user.id
        fb_id = self.test_user.fb_id
        activity = Activity.query.get(1) #running
        setting = ActivitySetting(self.test_user,activity,activity.questions[0])
        self.test_user.activity_settings.append(setting)
        db.session.commit()
        resp = self.app.put("/users/" + str(user_id) +\
            "/activity_settings/" + str(activity.id),
            data = {
                "question_ids":[q.id for q in activity.questions],
                "answers":[1 for x in activity.questions]
            }, headers = {"Authorization":fb_id + "junk"})
        assert resp.status_code==401

    def test_delete_user_activity(self):
        user_id = self.test_user.id
        fb_id = self.test_user.fb_id
        activity = Activity.query.get(1) #running
        setting = ActivitySetting(self.test_user,activity, activity.questions[0])
        self.test_user.activity_settings.append(setting)
        db.session.commit()
        resp = self.app.delete("/users/" + str(user_id) +\
            "/activity_settings/" + str(activity.id),
            headers={'Content-Type': 'application/x-www-form-urlencoded',
                     "Authorization":fb_id})
        assert resp.status_code==200

    def test_delete_user_activity_unauthorized(self):
        user_id = self.test_user.id
        fb_id = self.test_user.fb_id
        activity = Activity.query.get(1) #running
        setting = ActivitySetting(self.test_user,activity, activity.questions[0])
        self.test_user.activity_settings.append(setting)
        db.session.commit()
        resp = self.app.delete("/users/" + str(user_id) +\
            "/activity_settings/" + str(activity.id),
            headers={'Content-Type': 'application/x-www-form-urlencoded',
                     "Authorization":fb_id + "junk"})
        assert resp.status_code==401

"""
