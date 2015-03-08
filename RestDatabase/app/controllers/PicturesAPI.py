from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from app import db, api, socketio
from app.models import *
from app.utils.Response import Response

@api.resource("/pictures")
class PicturesAPI(Resource):
    #get all pictures for user_id
    def get(self):
        """
        Get all (secondary)pictures for a user.

        :param int user_id: Id of user.

        :status 400: Could not find user.
        :status 200: Pictures found.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("user_id",
            type=int, location="args", required=True)
        args = parser.parse_args()

        #get user from database
        user = User.query.filter(User.id==args.user_id).first()
        if not user:
            return Response(status=404,
                message="User not found.").__dict__,404

        return Response(status=200, message="Pictures found.",
            value=[p.dict_repr() for p in user.pictures.all()])\
            .__dict__, 200

    def post(self):
        """
        Post new (secondary)picture for a user.

        :reqheader Authorization: fb_id token needed here

        :form int user_id: Id of user.
        :form str uri: Facebook Picture Id string.
        :form int ui_index: Index of the ui.
        :form float top: Top position for crop
        :form float bottom: Bottom position for crop
        :form float left: Left position for crop
        :form float right: Right position for crop

        :status 400: Picture data invalid.
        :status 401: Not Authorized.
        :status 404: Could not find user.
        :status 201: Picture added.
        """

        parser = reqparse.RequestParser()
        parser.add_argument("user_id",
            type=int, location="form", required=True)
        parser.add_argument("uri",
            type=str, location="form", required=True)
        parser.add_argument("ui_index",
            type=int, location="form", required=True)
        parser.add_argument("top",
            type=float, location="form", required=True)
        parser.add_argument("bottom",
            type=float, location="form", required=True)
        parser.add_argument("left",
            type=float, location="form", required=True)
        parser.add_argument("right",
            type=float, location="form", required=True)
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()

        #get user from database
        user = User.query.filter(User.id==args.user_id).first()
        if not user:
            return Response(status=404,
                message="User not found.").__dict__,404

        #ensure user is valid by checking if fb_id is correct
        if user.fb_id != args.Authorization:
            return Response(status=401,message="Not Authorized.").__dict__,401
            
        if args.ui_index in [p.ui_index for p in user.pictures.all()]:
            user.pictures.delete(
                Picture.query.filter(Picture.ui_index==args.ui_index).first())

        try: picture = Picture(user,
                               args.uri,
                               args.ui_index,
                               args.top,
                               args.bottom,
                               args.left,
                               args.right)
        except:
            db.session.rollback()
            return Response(status=400, message="Picture data invalid.")\
              .__dict__,400
            
        #send new picture to user's other devices
        socketio.emit("picture_added",picture.dict_repr(),
                      room=str(picture.user.id))

        user.pictures.append(picture)
        db.session.commit()

        return Response(status=201, message="Picture added.",
                        value=picture.dict_repr()).__dict__,201

@api.resource("/pictures/<int:pic_id>")
class PictureAPI(Resource):
    def put(self, pic_id):
        """
        Delete picture for a user.

        :reqheader Authorization: fb_id token needed here

        :param int pic_id: Id of user.
        
        :form int user_id: Id of user.
        :form str uri: Facebook Picture Id string.
        :form int ui_index: Index of the ui.
        :form float top: Top position for crop
        :form float bottom: Bottom position for crop
        :form float left: Left position for crop
        :form float right: Right position for crop

        :status 400: Picture data invalid.
        :status 401: Not Authorized.
        :status 404: Picture not found.
        :status 201: Picture removed.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        parser.add_argument("uri",
            type=str, location="form", required=False)
        parser.add_argument("ui_index",
            type=int, location="form", required=False)
        parser.add_argument("top",
            type=float, location="form", required=False)
        parser.add_argument("bottom",
            type=float, location="form", required=False)
        parser.add_argument("left",
            type=float, location="form", required=False)
        parser.add_argument("right",
            type=float, location="form", required=False)
        args = parser.parse_args()
        
        pic = Picture.query.get(pic_id)
        if not pic:
            return Response(status=404,
                message="Picture not found.").__dict__,404

        #ensure user is valid by checking if fb_id is correct
        if pic.user.fb_id != args.Authorization:
            return Response(status=401,message="Not Authorized.").__dict__,401
            
        try:
            if args.uri != None: pic.uri = args.uri
            if args.ui_index != None:
                old_pic = Picture.query.filter(
                    Picture.ui_index==args.ui_index).first()
                if old_pic and old_pic!=pic: old_pic.user.pictures.remove(old_pic)
                pic.ui_index = args.ui_index
            if args.top != None: pic.top = args.top
            if args.bottom != None: pic.bottom = args.bottom
            if args.left != None: pic.left = args.left
            if args.right != None: pic.right = args.right
            db.session.commit()
        except: return Response(status=400, message="Picture data invalid.")\
              .__dict__, 400

        #send pic update to user's other devices
        socketio.emit("picture_updated",pic.dict_repr(),room=str(pic.user.id))
        
        return Response(status=202, message="Picture updated.")\
            .__dict__, 202

    #delete either a single, or all pictures for a user
    def delete(self, pic_id):
        """
        Delete picture for a user.

        :reqheader Authorization: fb_id token needed here

        :param int pic_id: Id of user.

        :status 401: Not Authorized.
        :status 404: "Picture not found.".
        :status 201: "Picture removed."
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()
        
        pic = Picture.query.get(pic_id)
        if not pic:
            return Response(status=404,
                message="Picture not found.").__dict__,404
        user = pic.user

        #ensure user is valid by checking if fb_id is correct
        if user.fb_id != args.Authorization:
            return Response(status=401,message="Not Authorized.").__dict__,401

        #delete picture
        user.pictures.remove(pic)
        db.session.commit()

        #alert user that picture has been deleted
        socketio.emit("picture_deleted",pic_id,room=str(user.id))

        return Response(status=200, message="Picture removed.").__dict__, 200
