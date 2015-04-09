from tests.utils.FitPalsTestCase import *
from app.utils.Facebook import *
from nose.tools import nottest

class FacebookFreindsApiTestCase(FitPalsTestCase):
    def test_get_user_facebook_friends(self):
        resp = self.app.get("/facebook_friends",
                            headers={"Authorization":self.test_user1["fitpals_secret"]})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"] == "Friends found."
        friends = json.loads(resp.data)["value"]
        assert len(friends) == 1
        assert friends[0]["name"]=="Ricky"

    def test_get_user_facebook_friends_not_authorized(self):
        resp = self.app.get("/facebook_friends",
                            headers={"Authorization":self.test_user1["fitpals_secret"] + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"] == "Not Authorized."
