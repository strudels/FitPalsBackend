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
        
    #helper function for running test_get_users for a bunch of diff possibilities
    @unittest.skip("Skipping a non-test function")
    def generate_test_user_and_get_users(self,
                           user,
                           activity_setting,
                           search_settings):
        #update search settings, activity_settings, and location for each user to be the same
        resp = self.app.put("/search_settings/%d" % user["search_settings_id"],
                            data=search_settings,
                            headers={"Authorization":user["fb_secret"]})
        resp = self.app.put("/users/%d" % user["id"],
                            data={"longitude":user["longitude"],
                                  "latitude":user["latitude"]},
                            headers={"Authorization":user["fb_secret"]})
        resp = self.app.put("/activity_settings",
                             data=activity_setting,
                            headers={"Authorization":user["fb_secret"]})
        resp = self.app.get("/users?longitude=40&latitude=20&radius=17000",
                            headers={"Authorization":fb_secret})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"] == "Users found."
        users = json.loads(resp.data)["value"]
        return users
       
    def test_get_users(self):
        fb_secret = self.test_user1["fb_secret"]
        setting_id = self.test_user1["search_settings_id"]
        activity_resp = json.loads(self.app.get("/activities").data)
        activity_id = activity_resp["value"][0]["id"]
        question_id = activity_resp["value"][0]["questions"][0]["id"]
        
        #a bit less than 12 miles away from user1
        location1 = (27.924458,-82.320241)
        location2 = (28.074511,-82.412251)

        #initialize user1
        user1_search_settings = {"activity_id":activity_id,
                                  "radius":12, 
                                  "radius_unit":"mile"}
        self.test_user1["longitude"] = location1[0]
        self.test_user1["latitude"] = location1[1]
        user1_activity_setting = {"user_id":self.test_user1["id"],
                                   "question_id":question_id,
                                   "lower_value":5,
                                   "upper_value":25,
                                   "unit_type":"mile"}
        resp = self.app.post("/activity_settings",
                             data=user1_activity_setting,
                             headers={"Authorization":self.test_user1["fb_secret"]})
        
        #initialize user2
        user2_search_settings = {"activity_id":activity_id,
                                  "radius":12, 
                                  "radius_unit":"mile"}
        self.test_user2["longitude"] = location2[0]
        self.test_user2["latitude"] = location2[1]
        user2_activity_setting = {"user_id":self.test_user2["id"],
                                   "question_id":question_id,
                                   "lower_value":5,
                                   "upper_value":25,
                                   "unit_type":"mile"}
        resp = self.app.post("/activity_settings",
                             data=user2_activity_setting,
                             headers={"Authorization":self.test_user2["fb_secret"]})
        
        # GET /users while both users are the same
        matches = self.generate_test_user_and_get_users(
            user=self.test_user2,
            activity_setting=user2_activity_setting,
            search_settings=user2_search_settings
        )
        assert len(matches) == 1
        match = matches[0]
        assert match["id"] == self.test_user2["id"]
        
        # GET /users user2's radius too short
        user2_search_settings["radius"] = 5
        matches = self.generate_test_user_and_get_users(
            user=self.test_user2,
            activity_setting=user2_activity_setting,
            search_settings=user2_search_settings
        )
        assert len(matches) == 0
        
        # GET /users user2's diff activity_setting
        user2_search_settings["radius"] = 12
        user2_activity_setting["lower_value"]=1
        user2_activity_setting["upper_value"]=4
        matches = self.generate_test_user_and_get_users(
            user=self.test_user2,
            activity_setting=user2_activity_setting,
            search_settings=user2_search_settings
        )
        assert len(matches) == 0

        # GET /users user2's radius too short
        user2_search_settings["radius"] = 5
        matches = self.generate_test_user_and_get_users(
            user=self.test_user2,
            activity_setting=user2_activity_setting,
            search_settings=user2_search_settings
        )
        assert len(matches) == 0
        
    def test_get_users_not_authorized(self):
        fb_secret = self.test_user1["fb_secret"]
        resp = self.app.get("/users?longitude=20&latitude=20&radius=17000",
                            headers={"Authorization":fb_secret + "junk"})
        assert resp.status_code==401
       
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
