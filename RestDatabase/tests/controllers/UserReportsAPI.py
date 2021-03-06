from tests.utils.FitPalsTestCase import *

class UserReportsAPITestCase(FitPalsTestCase):
    def test_create_user_report(self):
        report = {
            #place owner line in for convience later in test
            "owner_user_id":self.test_user1["id"],
            "reported_user_id":self.test_user2["id"],
            "reason":"Test user 1 was mean!"
        }
        resp = self.app.post("/user_reports",
                             data=report,
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        assert resp.status_code == 201
        assert json.loads(resp.data)["message"] == "User report created."
        report_received = json.loads(resp.data)["value"]
        assert type(report_received["id"]) == int
        report["id"] = report_received["id"]
        report["reviewed"] = False
        assert report == report_received
        
    def test_create_user_report_owner_not_authorized(self):
        report = {
            "reported_user_id":self.test_user2["id"],
            "reason":"Test user 1 was mean!"
        }
        resp = self.app.post("/user_reports",
                             data=report,
                             headers={"Authorization":self.test_user1["fitpals_secret"] + "junk"})
        assert resp.status_code == 401
        assert json.loads(resp.data)["message"] == "Not Authorized."
        
    def test_create_user_report_reportee_not_found(self):
        report = {
            "reported_user_id":0,
            "reason":"Test user 1 was mean!"
        }
        resp = self.app.post("/user_reports",
                             data=report,
                             headers={"Authorization":self.test_user1["fitpals_secret"]})
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"] == "User not found."
