from flask import Flask, request
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from app import db, api, app, exception_is_validation_error
from app.utils.AsyncNotifications import send_message
from app.models import *
from app.utils.Response import Response

@api.resource("/pictures")
class PicturesAPI(Resource):
    #get all pictures for user_id
    def get(self):
        """
        Get all pictures for a user.

        :query int user_id: Id of user.

        :status 404: User not found.
        :status 200: Pictures found.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("user_id",
            type=int, location="args", required=True)
        args = parser.parse_args()

        try:
            #get user from database
            user = User.query.filter(User.id==args.user_id).first()
            if not user:
                return Response(status=404,
                    message="User not found.").__dict__,404

            return Response(status=200, message="Pictures found.",
                value=[p.dict_repr() for p in user.pictures.all()])\
                .__dict__, 200
        except Exception as e:
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500

    def post(self):
        """
        Post new picture.

        :reqheader Authorization: facebook secret

        :form int user_id: Id of user.
        :form str uri: Facebook Picture Id string.
        :form int ui_index: Index of the ui.
        :form float top: Top position for crop. Must be between 0 and 1.
        :form float bottom: Bottom position for crop. Must be between 0 and 1.
        :form float left: Left position for crop. Must be between 0 and 1.
        :form float right: Right position for crop. Must be between 0 and 1.

        :status 400: Picture data invalid.
        :status 401: Not Authorized.
        :status 404: User not found.
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

        try:
            #get user from database
            user = User.query.filter(User.id==args.user_id).first()
            if not user:
                return Response(status=404,
                    message="User not found.").__dict__,404

            #ensure user is valid by checking if fb_id is correct
            if user.fitpals_secret != args.Authorization:
                return Response(status=401,message="Not Authorized.").__dict__,401

            if args.ui_index in [p.ui_index for p in user.pictures.all()]:
                user.pictures.delete(
                    Picture.query.filter(Picture.ui_index==args.ui_index).first())

            picture = Picture(user,
                            args.uri,
                            args.ui_index,
                            args.top,
                            args.bottom,
                            args.left,
                            args.right)
            user.pictures.append(picture)
            db.session.commit()

            #send new picture to user's other devices
            send_message(picture.user,request.path,request.method,
                         value=picture.dict_repr())

            return Response(status=201, message="Picture added.",
                            value=picture.dict_repr()).__dict__,201
        except Exception as e:
            if exception_is_validation_error(e):
                return Response(status=400,
                    message="Picture data invalid.").__dict__,400
            db.session.rollback()
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500

@api.resource("/pictures/<int:pic_id>")
class PictureAPI(Resource):
    def put(self, pic_id):
        """
        Delete picture.

        :reqheader Authorization: facebook secret

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
        
        try:
            pic = Picture.query.get(pic_id)
            if not pic:
                return Response(status=404,
                    message="Picture not found.").__dict__,404

            #ensure user is valid by checking if fb_id is correct
            if pic.user.fitpals_secret != args.Authorization:
                return Response(status=401,message="Not Authorized.").__dict__,401

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

            #send pic update to user's other devices
            send_message(pic.user,request.path,request.method,
                         value=pic.dict_repr())

            return Response(status=202, message="Picture updated.",
                            value=pic.dict_repr()).__dict__, 202
        except Exception as e:
            if exception_is_validation_error(e):
                return Response(status=400,
                    message="Picture data invalid.").__dict__,400
            db.session.rollback()
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500

    #delete either a single, or all pictures for a user
    def delete(self, pic_id):
        """
        Delete picture.

        :reqheader Authorization: facebook secret

        :param int pic_id: Id of user.

        :status 401: Not Authorized.
        :status 404: Picture not found.
        :status 500: Internal error. Changes not committed.
        :status 201: Picture removed.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()
        
        try:
            pic = Picture.query.get(pic_id)
            if not pic:
                return Response(status=404,
                    message="Picture not found.").__dict__,404
            user = pic.user

            #ensure user is valid by checking if fb_id is correct
            if user.fitpals_secret != args.Authorization:
                return Response(status=401,message="Not Authorized.").__dict__,401

            try:
                #delete picture
                user.pictures.remove(pic)
                db.session.delete(pic)
                db.session.commit()
            except:
                db.session.rollback()
                return Response(status=500,
                    message="Internal error. Changes not committed.").__dict__,500

            #alert user that picture has been deleted
            send_message(user, request.path, request.method)

            return Response(status=200, message="Picture removed.").__dict__, 200
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500
