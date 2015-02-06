from response import Response

from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from app import db, api
from app.models import *

@api.resource('/users/<user_id>')
class UserAPI(Resource):
    def get(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("attributes",
            type=str, location='args', required=False, action="append")
        args = parser.parse_args()

        #Get user from db
        try: user = database.get_user(user_id)
        except:
            return Response(status=400,message="Invalid user id.").__dict__,400

        #cast id from ObjectId() to str()
        user["user_id"] = str(user["user_id"])

        #don't allow user to get secrets of other users
        del user["fb_id"]
        del user["apn_tokens"]

        #if attributes were specified, only return specified attributes
        if args.attributes:
            user = {attr:user[attr]\
                for attr in args.attributes if attr in user.keys()
            }
        return Response(status=200,
            message="User found.",value=user).__dict__,200
    
    def put(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("fb_id",
            type=str, location='form', required=True)
        parser.add_argument("apn_tokens",
            type=str, location='form', required=False, action="append")
        parser.add_argument("longitude",
            type=float, location='form', required=False)
        parser.add_argument("latitude",
            type=float, location='form', required=False)
        parser.add_argument("primary_picture",
            type=str, location='form', required=False, action="append")
        parser.add_argument("secondary_pictures",
            type=str, location='form', required=False, action="append")
        parser.add_argument("about_me",
            type=str, location='form', required=False, action="append")
        parser.add_argument("available",
            type=bool, location='form', required=False)
        parser.add_argument("dob",
            type=int, location='form', required=False)
        args = parser.parse_args()

        #get user to update from db
        try: user = database.get_user(user_id)
        except:
            return Response(status=400,message="Invalid user id.").__dict__,400

        #ensure user is valid by checking if fb_id is correct
        if user["fb_id"] != args.fb_id:
            return Response(status=401,message="Incorrect fb_id.").__dict__,401

        #update fields specified by client
        if args.longitude and args.latitude:
            user["location"] = [args.longitude,args.latitude]
        if args.primary_picture: user["primary_picture"] = args.primary_picture
        if args.secondary_pictures:
            user["secondary_pictures"] = args.secondary_pictures
        if args.about_me: user["about_me"] = args.about_me
        if args.available: user["available"] = args.available
        if args.dob: user["dob"] = args.dob
        if args.apn_tokens: user["apn_tokens"] = args.apn_tokens

        #Update database and return whether or not the update was a success
        try:
            update_status = database.update_user(user_id,user)
            if update_status["ok"]==1:
                return Response(status=202,message="User updated").__dict__,202
            else:
                return Response(status=400,
                    message="User update failed.").__dict__,400
        except:
            return Response(status=400,
                message="Invalid user data.").__dict__,400

    def delete(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("fb_id",
            type=str, location='form', required=True)
        args = parser.parse_args()

        #ensure user is authorized to delete
        user = database.get_user(user_id) 
        if user["fb_id"] != args.fb_id:
            return Response(status=401,
                message="Incorrect fb_id.").__dict__,401
            
        #Delete user
        if not database.delete_user(user_id):
            return Response(status=500,
                message="User not deleted.").__dict__,500
        return Response(status=200, message="User deleted.").__dict__,200
