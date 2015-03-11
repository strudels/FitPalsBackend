from tests.utils.FitPalsTestCase import *

class UsersApiTestCase(FitPalsTestCase):
    def test_create_user(self):
        resp = self.app.post("/users",data={"fb_id":"some fb_id",
                                            "dob_year":1990,
                                            "dob_month":2,
                                            "dob_day":17})
        assert resp.status_code==201
        assert json.loads(resp.data)["message"] == "User created."

    def test_create_user_found(self):
        resp = self.app.post("/users",data={"fb_id":self.test_user1["fb_id"]})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"] == "User found."

    def test_get_users(self):
        fb_id = self.test_user1["fb_id"]
        setting_id = self.test_user1["search_settings_id"]
        activity_id = json.loads(self.app.get("/activities").data)["value"][0]["id"]

        #update search settings
        resp = self.app.put("/search_settings/%d" % setting_id,
                            data={"activity_id":activity_id,
                                  "men_only":0, "women_only":1},
                            headers={"Authorization":fb_id})

        resp = self.app.get("/users?longitude=20&latitude=20&radius=17000",
                            headers={"Authorization":fb_id})
        assert resp.status_code==200
        
    def test_get_users_not_authorized(self):
        fb_id = self.test_user1["fb_id"]
        resp = self.app.get("/users?longitude=20&latitude=20&radius=17000",
                            headers={"Authorization":fb_id + "junk"})
        assert resp.status_code==401
        
    def test_get_users_invalid_gps_params(self):
        fb_id = self.test_user1["fb_id"]
        setting_id = self.test_user1["search_settings_id"]
        activity_id = json.loads(self.app.get("/activities").data)["value"][0]["id"]

        #update search settings
        resp = self.app.put("/search_settings/%d" % setting_id,
                            data={"activity_id":activity_id,
                                  "men_only":0, "women_only":1},
                            headers={"Authorization":fb_id})

        resp = self.app.get("/users?longitude=200&latitude=20&radius=17000",
                            headers={"Authorization":fb_id})
        assert resp.status_code==400
        
    def test_get_user(self):
        test_user1_public = self.test_user1
        del test_user1_public["fb_id"]
        del test_user1_public["password"]
        resp = self.app.get("/users/" + str(self.test_user1["id"]))
        assert resp.status_code==200
        assert json.loads(resp.data)["value"] == test_user1_public

    def test_get_user_name(self):
        resp = self.app.get("/users/" + str(self.test_user1["id"])\
                            + "?attributes=name")
        assert resp.status_code==200
        assert json.loads(resp.data)["value"] == {"name":self.test_user1["name"]}
        
    def test_get_user_not_found(self):
        resp = self.app.get("/users/0")
        assert resp.status_code==404
        assert json.loads(resp.data)["message"] == "User not found."
        
    def test_get_user_authorized(self):
        resp = self.app.get("/users/" + str(self.test_user1["id"]),
                            headers={"Authorization":self.test_user1["fb_id"]})
        assert resp.status_code==200
        assert json.loads(resp.data)["value"] == self.test_user1

    def test_get_user_not_authorized(self):
        resp = self.app.get("/users/" + str(self.test_user1["id"]),
                            headers={"Authorization":
                                     self.test_user1["fb_id"] + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"] == "Not Authorized."

    def test_update_user(self):
        #update the user
        user_id = self.test_user1["id"]
        fb_id = self.test_user1["fb_id"]
        resp = self.app.put("/users/" + str(user_id),
                            data={
                                "longitude":20,
                                "latitude":20,
                                "about me":"I'm a test user!"},
                            headers = {"Authorization":fb_id})
        assert resp.status_code==202
        
        #ensure that test_user websocket self.websocket_client1 got new user update
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "user_update"
        assert received[-1]["args"][0] == json.loads(resp.data)["value"]
        
    def test_update_user_not_found(self):
        user_id = 0
        fb_id = self.test_user1["fb_id"]
        resp = self.app.put("/users/" + str(user_id),
                            data={
                                "longitude":20,
                                "latitude":20,
                                "about me":"I'm a test user!"},
                            headers = {"Authorization":fb_id})
        assert resp.status_code==400
        assert json.loads(resp.data)["message"] == "Could not find user."
        
    def test_update_user_not_authorized(self):
        user_id = self.test_user1["id"]
        fb_id = self.test_user1["fb_id"] + "junk"
        resp = self.app.put("/users/" + str(user_id),
                            data={
                                "longitude":20,
                                "latitude":20,
                                "about me":"I'm a test user!"},
                            headers = {"Authorization":fb_id})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"] == "Not Authorized."
        
    def test_delete_user(self):
        user_id = self.test_user1["id"]
        fb_id = self.test_user1["fb_id"]
        resp = self.app.delete("/users/" + str(user_id),
                               headers={"Content-Type": "application/x-www-form-urlencoded",
                                        "Authorization":fb_id})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"] == "User deleted."
        
    def test_delete_user_not_found(self):
        user_id = 0
        fb_id = self.test_user1["fb_id"]
        resp = self.app.delete("/users/" + str(user_id),
                               headers={"Content-Type": "application/x-www-form-urlencoded",
                                        "Authorization":fb_id})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"] == "Could not find user."

    def test_delete_user_not_authorized(self):
        user_id = self.test_user1["id"]
        fb_id = self.test_user1["fb_id"] + "junk"
        resp = self.app.delete("/users/" + str(user_id),
                               headers={"Content-Type": "application/x-www-form-urlencoded",
                                        "Authorization":fb_id})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"] == "Not Authorized."
