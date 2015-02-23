import unittest
import simplejson as json
from app import app,db
from app.models import *

class ActivitiesApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_get_activities(self):
        resp = self.app.get("/activities")
        assert resp.status_code==200

class UserActivitySettingsAPITestCase(unittest.TestCase):
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

    def test_get_user_activities(self):
        resp = self.app.get("/users/" + str(self.test_user.id) + "/activity_settings")
        assert resp.status_code==200

    def test_add_user_activity(self):
        user_id = self.test_user.id
        fb_id = self.test_user.fb_id
        resp = self.app.post("/users/" + str(user_id) + "/activity_settings",
            data={
                "fb_id":fb_id,
                "activity_id":1,
                "question_ids":[1,2],
                "answers":[30, 5000]
            })
        assert resp.status_code==201

    def test_delete_user_activities(self):
        user_id = self.test_user.id
        fb_id = self.test_user.fb_id
        resp = self.app.delete("/users/" + str(user_id) + "/activity_settings",
            data={"fb_id":fb_id},
            headers={'Content-Type': 'application/x-www-form-urlencoded'})
        assert resp.status_code==200

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
                "fb_id":fb_id,
                "question_ids":[q.id for q in activity.questions],
                "answers":[1 for x in activity.questions]
            })
        assert resp.status_code==202

    def test_delete_user_activity(self):
        user_id = self.test_user.id
        fb_id = self.test_user.fb_id
        activity = Activity.query.get(1) #running
        setting = ActivitySetting(self.test_user,activity, activity.questions[0])
        self.test_user.activity_settings.append(setting)
        db.session.commit()
        resp = self.app.delete("/users/" + str(user_id) +\
            "/activity_settings/" + str(activity.id),
            data={"fb_id":fb_id},
            headers={'Content-Type': 'application/x-www-form-urlencoded'})
        assert resp.status_code==200
