from tests.utils.FitPalsTestCase import *

class UsersApiTestCase(FitPalsTestCase):
    def test_create_user(self):
        user = {"fb_secret":"some fb_secret",
                "fb_id":"some fb_id",
                "dob_year":1990,
                "dob_month":2,
                "dob_day":17,
                "longitude":20.0,
                "latitude":20.0}
        resp = self.app.post("/users",data=user)
        assert resp.status_code==201
        assert json.loads(resp.data)["message"] == "User created."
        received_user = json.loads(resp.data)["value"]
        for key in user.keys():
            assert user[key] == received_user[key]

    def test_create_user_found(self):
        resp = self.app.post("/users",data={"fb_secret":self.test_user1["fb_secret"],
                                            "fb_id":self.test_user1["fb_id"]})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"] == "User found."
        
    def test_create_user_not_authorized(self):
        resp = self.app.post("/users",data={"fb_secret":self.test_user1["fb_secret"] + "junk",
                                            "fb_id":self.test_user1["fb_id"]})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"] == "Not Authorized."
        
    def test_create_user_no_dob(self):
        user = {"fb_secret":"some fb_secret",
                "fb_id":"some fb_id",
                "dob_month":2,
                "dob_day":17,
                "longitude":20.0,
                "latitude":20.0}
        resp = self.app.post("/users",data=user)
        assert resp.status_code==400
        assert json.loads(resp.data)["message"] == "Must specify DOB."
        
    def test_create_user_bad_coords(self):
        user = {"fb_secret":"some fb_secret",
                "fb_id":"some fb_id",
                "dob_year":1990,
                "dob_month":2,
                "dob_day":17,
                "longitude":200.0,
                "latitude":200.0}
        resp = self.app.post("/users",data=user)
        assert resp.status_code==400
        assert json.loads(resp.data)["message"] == "Coordinates invalid."

    def test_get_users(self):
        fb_secret = self.test_user1["fb_secret"]
        setting_id = self.test_user1["search_settings_id"]
        activity_id = json.loads(self.app.get("/activities").data)["value"][0]["id"]

        #update search settings and location for each user to be the same
        resp = self.app.put("/search_settings/%d"
                            % self.test_user1["search_settings_id"],
                            data={"activity_id":activity_id},
                            headers={"Authorization":self.test_user1["fb_secret"]})
        resp = self.app.put("/users/%d" % self.test_user1["id"],
                            data={"longitude":40, "latitude":20},
                            headers={"Authorization":self.test_user1["fb_secret"]})
        self.test_user1["longitude"] = 40.0
        self.test_user1["latitude"] = 20.0
        resp = self.app.put("/search_settings/%d"
                            % self.test_user2["search_settings_id"],
                            data={"activity_id":activity_id},
                            headers={"Authorization":self.test_user2["fb_secret"]})
        resp = self.app.put("/users/%d" % self.test_user2["id"],
                            data={"longitude":40, "latitude":20},
                            headers={"Authorization":self.test_user2["fb_secret"]})
        self.test_user2["longitude"] = 40.0
        self.test_user2["latitude"] = 20.0
        resp = self.app.put("/search_settings/%d"
                            % self.test_user3["search_settings_id"],
                            data={"activity_id":activity_id},
                            headers={"Authorization":self.test_user3["fb_secret"]})
        resp = self.app.put("/users/%d" % self.test_user3["id"],
                            data={"longitude":40, "latitude":20},
                            headers={"Authorization":self.test_user3["fb_secret"]})
        self.test_user3["longitude"] = 40.0
        self.test_user3["latitude"] = 20.0
        
        #delete private fields from test_users
        del self.test_user1["fb_secret"]
        del self.test_user1["password"]
        del self.test_user2["fb_secret"]
        del self.test_user2["password"]
        del self.test_user3["fb_secret"]
        del self.test_user3["password"]

        #import pdb; pdb.set_trace()
        resp = self.app.get("/users?longitude=40&latitude=20&radius=17000",
                            headers={"Authorization":fb_secret})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"] == "Users found."
        users = json.loads(resp.data)["value"]
        #there are 3 users created by FitPalsTestCase setUp()
        assert len(users) == 3
        assert users[0] == self.test_user1
        assert users[1] == self.test_user2
        assert users[2] == self.test_user3
        
    def test_get_users_not_authorized(self):
        fb_secret = self.test_user1["fb_secret"]
        resp = self.app.get("/users?longitude=20&latitude=20&radius=17000",
                            headers={"Authorization":fb_secret + "junk"})
        assert resp.status_code==401
        
    def test_get_users_invalid_gps_params(self):
        fb_secret = self.test_user1["fb_secret"]
        setting_id = self.test_user1["search_settings_id"]
        activity_id = json.loads(self.app.get("/activities").data)["value"][0]["id"]

        #update search settings
        resp = self.app.put("/search_settings/%d" % setting_id,
                            data={"activity_id":activity_id,
                                  "men_only":0, "women_only":1},
                            headers={"Authorization":fb_secret})

        resp = self.app.get("/users?longitude=200&latitude=20&radius=17000",
                            headers={"Authorization":fb_secret})
        assert resp.status_code==400
        
    def test_get_user(self):
        test_user1_public = self.test_user1
        del test_user1_public["fb_secret"]
        del test_user1_public["password"]
        resp = self.app.get("/users/" + str(self.test_user1["id"]))
        assert resp.status_code==200
        assert json.loads(resp.data)["message"] == "User found."
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

    def test_update_user(self):
        #update the user
        user_id = self.test_user1["id"]
        fb_secret = self.test_user1["fb_secret"]
        resp = self.app.put("/users/" + str(user_id),
                            data={
                                "longitude":20,
                                "latitude":20,
                                "about_me":"I'm a test user!"},
                            headers = {"Authorization":fb_secret})
        assert resp.status_code==202
        
        #update user on our end
        self.test_user1["longitude"] = 20.0
        self.test_user1["latitude"] = 20.0
        self.test_user1["about_me"] = "I'm a test user!"
        del self.test_user1["password"]
        del self.test_user1["fb_secret"]
        
        #ensure that test_user websocket self.websocket_client1 got new user update
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "user_update"
        assert received[-1]["args"][0] == self.test_user1
        assert received[-1]["args"][0] == json.loads(resp.data)["value"]
        
    def test_update_user_not_found(self):
        user_id = 0
        fb_secret = self.test_user1["fb_secret"]
        resp = self.app.put("/users/" + str(user_id),
                            data={
                                "longitude":20,
                                "latitude":20,
                                "about me":"I'm a test user!"},
                            headers = {"Authorization":fb_secret})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"] == "User not found."
        
    def test_update_user_not_authorized(self):
        user_id = self.test_user1["id"]
        fb_secret = self.test_user1["fb_secret"] + "junk"
        resp = self.app.put("/users/" + str(user_id),
                            data={
                                "longitude":20,
                                "latitude":20,
                                "about me":"I'm a test user!"},
                            headers = {"Authorization":fb_secret})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"] == "Not Authorized."
        
    def test_delete_user(self):
        #delete test_user1
        user_id = self.test_user1["id"]
        fb_secret = self.test_user1["fb_secret"]
        resp = self.app.delete("/users/" + str(user_id),
                               headers={"Content-Type": "application/x-www-form-urlencoded",
                                        "Authorization":fb_secret})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"] == "User deleted."
        
        #ensure that user was deleted
        resp = self.app.get("/users/%d" % user_id)
        assert resp.status_code == 404
        assert json.loads(resp.data)["message"] == "User not found."

        
    def test_delete_user_not_found(self):
        user_id = 0
        fb_secret = self.test_user1["fb_secret"]
        resp = self.app.delete("/users/" + str(user_id),
                               headers={"Content-Type": "application/x-www-form-urlencoded",
                                        "Authorization":fb_secret})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"] == "User not found."

    def test_delete_user_not_authorized(self):
        user_id = self.test_user1["id"]
        fb_secret = self.test_user1["fb_secret"] + "junk"
        resp = self.app.delete("/users/" + str(user_id),
                               headers={"Content-Type": "application/x-www-form-urlencoded",
                                        "Authorization":fb_secret})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"] == "Not Authorized."
