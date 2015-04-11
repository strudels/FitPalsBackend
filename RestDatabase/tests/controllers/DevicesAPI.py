from tests.utils.FitPalsTestCase import *

class APNTokensApiTestCase(FitPalsTestCase):
    def test_add_device(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        device = {"token":"some apn token","user_id":self.test_user1["id"]}
        resp = self.app.post("/devices",
                             data=device,
                             headers={"Authorization":fitpals_secret})
        assert resp.status_code==201
        assert json.loads(resp.data)["message"]=="Device registered."
        received_device = json.loads(resp.data)["value"]
        assert type(received_device["id"]) == int
        device["id"] = received_device["id"]
        assert received_device == device

    def test_add_device_already_registered(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        #post same device twice
        resp = self.app.post("/devices",
                             data={"token":"some apn token","user_id":self.test_user1["id"]},
                             headers={"Authorization":fitpals_secret})
        resp = self.app.post("/devices",
                             data={"token":"some apn token","user_id":self.test_user1["id"]},
                             headers={"Authorization":fitpals_secret})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Device already registered."

    def test_add_device_user_not_found(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/devices",
                             data={"token":"some apn token","user_id":0},
                             headers={"Authorization":fitpals_secret})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="User not found."

    def test_add_device_not_authorized(self):
        fitpals_secret = self.test_user1["fitpals_secret"] + "junk"
        resp = self.app.post("/devices",
                             data={"token":"some apn token","user_id":self.test_user1["id"]},
                             headers={"Authorization":fitpals_secret})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_add_device_could_not_register(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        resp = self.app.post("/devices",
                             data={"token":"some apn token"*9000,
                                   "user_id":self.test_user1["id"]},
                             headers={"Authorization":fitpals_secret})
        assert resp.status_code==400
        assert json.loads(resp.data)["message"]=="Device data invalid."

    def test_delete_device(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        #create device
        resp = self.app.post("/devices",
                             data={"token":"some apn token","user_id":self.test_user1["id"]},
                             headers={"Authorization":fitpals_secret})
        device = json.loads(resp.data)["value"]

        #delete device
        resp = self.app.delete("/devices/%d" % device["id"],
                               headers={"Authorization":fitpals_secret})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Device deleted."
        
        #ensure device was deleted by creating it again and not getting a 200
        resp = self.app.post("/devices",
                             data={"token":"some apn token","user_id":self.test_user1["id"]},
                             headers={"Authorization":fitpals_secret})
        assert resp.status_code==201
        

    def test_delete_device_not_found(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        #create device
        resp = self.app.post("/devices",
                             data={"token":"some apn token","user_id":self.test_user1["id"]},
                             headers={"Authorization":fitpals_secret})
        device_id = json.loads(resp.data)["value"]["id"]

        #delete device
        resp = self.app.delete("/devices/%d" % 0,
                               headers={"Authorization":fitpals_secret})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Device not found."

    def test_delete_device_not_authorized(self):
        fitpals_secret = self.test_user1["fitpals_secret"]
        #create device
        resp = self.app.post("/devices",
                             data={"token":"some apn token","user_id":self.test_user1["id"]},
                             headers={"Authorization":fitpals_secret})
        device_id = json.loads(resp.data)["value"]["id"]

        #delete device
        resp = self.app.delete("/devices/%d" % device_id,
                               headers={"Authorization":fitpals_secret + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."
