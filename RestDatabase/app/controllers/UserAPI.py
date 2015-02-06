from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from app import db, api
from app.models import *
from app.utils.Response import Response

@api.resource('/users/<user_id>')
class UserAPI(Resource):
    def get(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("attributes",
            type=str, location='args', required=False, action="append")
        args = parser.parse_args()
        
        try: user_id = int(user_id)
        except: 
            return Response(status=400,message="Invalid user id.").__dict__,400

        #Get user from db
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400,message="User not found.").__dict__,400

        #apply any attribute filters specified
        user_dict = user.dict_repr()
        if args.attributes:
            user_dict = {x:y for x,y in user_dict if x in args.attributes}

        #if attributes were specified, only return specified attributes
        return Response(status=200,
            message="User found.",value=user_dict).__dict__,200
    
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

        try: user_id = int(user_id)
        except: 
            return Response(status=400,message="Invalid user id.").__dict__,400

        #get user to update from db
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400,message="Could not find user.").__dict__,400

        #ensure user is valid by checking if fb_id is correct
        if user.fb_id != args.fb_id:
            return Response(status=401,message="Incorrect fb_id.").__dict__,401

        #update fields specified by client
        if args.longitude and args.latitude:
            user.location =\
                WKTElement("POINT(%f %f)"%(args.longitude,args.latitude))
        if args.primary_picture: user.primary_picture = args.primary_picture
        if args.about_me: user.about_me = args.about_me
        if args.available: user.available = args.available
        if args.dob: user.dob = args.dob
        """
        if args.secondary_pictures:
            user["secondary_pictures"] = args.secondary_pictures
        if args.apn_tokens: user["apn_tokens"] = args.apn_tokens
        """

        #Update database and return whether or not the update was a success
        try: db.session.commit()
        except: return Response(status=400,
            message="User update failed.").__dict__, 400

        return Response(status=202,message="User updated").__dict__,202

    def delete(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("fb_id",
            type=str, location='form', required=True)
        args = parser.parse_args()

        #cast user_id to int type
        try: user_id = int(user_id)
        except: 
            return Response(status=400,message="Invalid user id.").__dict__,400

        #get user from database
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400,
                message="Could not find user.").__dict__,400

        #ensure user is authorized to delete
        if user.fb_id != args.fb_id:
            return Response(status=401,
                message="Incorrect fb_id.").__dict__,401
            
        #Delete user
        try:
            db.session.delete(user)
            db.session.commit()
        except:
            return Response(status=500,message="User not deleted.").__dict__,500

        return Response(status=200, message="User deleted.").__dict__,200
