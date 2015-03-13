from tests.utils.FitPalsTestCase import *

class PicturesApiTestCase(FitPalsTestCase):
    def tearDown(self):
        reset_app()

    def test_add_picture(self):
        #add picture
        fb_secret = self.test_user1["fb_secret"]
        picture = {"user_id":self.test_user1["id"],
                   "uri":"some uri",
                   "ui_index":0,
                   "top":0.5,
                   "bottom":0.5,
                   "left":0.5,
                   "right":0.5}
        resp = self.app.post("/pictures",
                             data=picture,
                             headers={"Authorization":fb_secret})
        assert resp.status_code==201
        assert json.loads(resp.data)["message"]=="Picture added."
        picture_added = json.loads(resp.data)["value"]
        assert type(picture_added["id"]) == int
        picture["id"] = picture_added["id"]
        assert picture == picture_added

        #ensure that test_user1 websocket self.websocket_client1 got update
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "picture_added"

    def test_add_picture_user_not_found(self):
        fb_secret = self.test_user1["fb_secret"]
        resp = self.app.post("/pictures",
                             data={"user_id":0,
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_secret})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="User not found."

    def test_add_picture_not_authorized(self):
        fb_secret = self.test_user1["fb_secret"] + "junk"
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user1["id"],
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_secret})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_add_picture_invalid_data(self):
        fb_secret = self.test_user1["fb_secret"]
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user1["id"],
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":1.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_secret})
        assert resp.status_code==400
        assert json.loads(resp.data)["message"]=="Picture data invalid."

    def test_get_pictures(self):
        #add picture to get
        fb_secret = self.test_user1["fb_secret"]
        picture = {"user_id":self.test_user1["id"],
                   "uri":"some uri",
                   "ui_index":0,
                   "top":0.5,
                   "bottom":0.5,
                   "left":0.5,
                   "right":0.5}
        resp = self.app.post("/pictures",
                             data=picture,
                             headers={"Authorization":fb_secret})
        assert resp.status_code==201
        assert json.loads(resp.data)["message"]=="Picture added."

        resp = self.app.get("/pictures?user_id=%d" % self.test_user1["id"])
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Pictures found."
        received_picture = json.loads(resp.data)["value"][0]
        assert type(received_picture["id"]) == int
        picture["id"] = received_picture["id"]
        assert picture == received_picture

    def test_get_pictures_user_not_found(self):
        resp = self.app.get("/pictures?user_id=%d" % 0)
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="User not found."
        
    def test_update_picture(self):
        #create picture 1
        fb_secret = self.test_user1["fb_secret"]
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user1["id"],
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_secret})
        pic1 = json.loads(resp.data)["value"]

        #create picture 2
        fb_secret = self.test_user1["fb_secret"]
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user1["id"],
                                   "uri":"some uri 2",
                                   "ui_index":1,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_secret})
        pic2 = json.loads(resp.data)["value"]["id"]
        
        #update picture
        resp = self.app.put("/pictures/%d" % self.test_user1["id"],
                             data={"uri":"some other uri",
                                   "ui_index":0,
                                   "top":0.6,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_secret})
        assert resp.status_code==202
        assert json.loads(resp.data)["message"]=="Picture updated."
        pic_updated = json.loads(resp.data)["value"]
        pic1["top"] = 0.6
        pic1["uri"] = "some other uri"
        assert pic_updated == pic1


        #ensure that test_user1 websocket self.websocket_client1 got update
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "picture_updated"

    def test_update_picture_not_found(self):
        fb_secret = self.test_user1["fb_secret"]
        resp = self.app.put("/pictures/%d" % 0,
                             data={"uri":"some other uri",
                                   "ui_index":0,
                                   "top":0.6,
                                   "bottom":0.6,
                                   "left":0.6,
                                   "right":0.6},
                             headers={"Authorization":fb_secret})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Picture not found."

    def test_update_picture_not_authorized(self):
        #create picture 1
        fb_secret = self.test_user1["fb_secret"]
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user1["id"],
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_secret})
        pic1_id = json.loads(resp.data)["value"]["id"]

        #update picture
        resp = self.app.put("/pictures/%d" % pic1_id,
                             data={"uri":"some other uri",
                                   "ui_index":0,
                                   "top":0.6,
                                   "bottom":0.6,
                                   "left":0.6,
                                   "right":0.6},
                             headers={"Authorization":fb_secret + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."

    def test_update_picture_invalid(self):
        #create picture 1
        fb_secret = self.test_user1["fb_secret"]
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user1["id"],
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_secret})
        pic1_id = json.loads(resp.data)["value"]["id"]

        #update picture
        resp = self.app.put("/pictures/%d" % pic1_id,
                             data={"uri":"some other uri",
                                   "ui_index":0,
                                   "top":0.6,
                                   "bottom":0.6,
                                   "left":1.6,
                                   "right":0.6},
                             headers={"Authorization":fb_secret})
        assert resp.status_code==400
        assert json.loads(resp.data)["message"]=="Picture data invalid."
       
    def test_delete_picture(self):
        fb_secret = self.test_user1["fb_secret"]

        #add picture to delete
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user1["id"],
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_secret})
        pic_id = json.loads(resp.data)["value"]["id"]
        
        #delete picture
        resp = self.app.delete("/pictures/%d" % pic_id,
            headers={"Content-Type": "application/x-www-form-urlencoded",
                    "Authorization":fb_secret})
        assert resp.status_code==200
        assert json.loads(resp.data)["message"]=="Picture removed."

        #ensure that test_user1 websocket self.websocket_client1 got update
        received = self.websocket_client1.get_received()
        assert len(received) != 0
        assert received[-1]["name"] == "picture_deleted"
        
        #ensure picture was actually deleted
        resp = self.app.get("/pictures?user_id=%d" % self.test_user1["id"])
        assert len(json.loads(resp.data)["value"]) == 0

    def test_delete_picture_not_found(self):
        fb_secret = self.test_user1["fb_secret"]
        #delete picture
        resp = self.app.delete("/pictures/%d" % 0,
            headers={"Content-Type": "application/x-www-form-urlencoded",
                    "Authorization":fb_secret})
        assert resp.status_code==404
        assert json.loads(resp.data)["message"]=="Picture not found."

    def test_delete_picture_not_authorized(self):
        fb_secret = self.test_user1["fb_secret"]

        #add picture to delete
        resp = self.app.post("/pictures",
                             data={"user_id":self.test_user1["id"],
                                   "uri":"some uri",
                                   "ui_index":0,
                                   "top":0.5,
                                   "bottom":0.5,
                                   "left":0.5,
                                   "right":0.5},
                             headers={"Authorization":fb_secret})
        pic_id = json.loads(resp.data)["value"]["id"]
        
        #delete picture
        resp = self.app.delete("/pictures/%d" % pic_id,
            headers={"Content-Type": "application/x-www-form-urlencoded",
                     "Authorization":fb_secret + "junk"})
        assert resp.status_code==401
        assert json.loads(resp.data)["message"]=="Not Authorized."
