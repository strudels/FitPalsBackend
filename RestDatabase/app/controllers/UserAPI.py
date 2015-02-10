from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from sqlalchemy import or_

from app import db, api
from app.models import *
from app.utils.Response import Response

@api.resource('/users')
class UsersAPI(Resource):
    def _age_to_day(self,age):
        day = datetime.now().date() - relativedelta(years=age)
        return int(time.mktime(day.timetuple()))

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("longitude",
            type=float, location='args', required=False)
        parser.add_argument("latitude",
            type=float, location='args', required=False)
        #radius in meters
        parser.add_argument("radius",
            type=float, location='args', required=False)
        parser.add_argument("limit",
            type=int, location="args", required=False)
        parser.add_argument("offset",
            type=int, location="args", required=False)
        parser.add_argument("last_updated",
            type=int, location="args", required=False)
        parser.add_argument("jabber_id",
            type=str, location="args", required=False)
        parser.add_argument("activity_name",
            type=str, location="args", required=False)
        parser.add_argument("question_ids",
            type=int, location="args", required=False, default=[])
        parser.add_argument("answers",
            type=float, location="args", required=False, default=[])
        args = parser.parse_args()

        #apply filters specified by user to matches
        query = User.query
        if (args.radius and args.longitude and args.latitude):
            #ensure GPS parameters are valid
            if (args.radius <= 0) or not (-180 <= args.longitude <= 180)\
                or not (-90 <= args.latitude <= 90):
                return Response(status=400,message="Invalid GPS parameters"),400
            point = func.ST_GeomFromText('POINT(-82.319645 27.924475)') 
            arg = func.ST_DWithin(point, User.location, args.radius, True)
            query = query.filter(arg)

        #args.last_updated probably needs to be converted to a datetime
        if args.last_updated:
            query = query.filter(User.last_update<=args.last_updated)

        if args.jabber_id:
            query = query.filter(User.last_update==args.jabber_id)

        if args.activity_name:
            query = query.join(User.activity_settings)\
                .filter(ActivitySetting.activity.name==args.activity_name)

        #right now this only matches if questions have the same answers
        if len(args.question_ids) == len(args.answers):
            or_expr = False
            for q_id,answer in zip(args.question_ids, args.answers):
                or_expr = or_(or_expr,ActivitySetting.question.id==q_id,
                    ActivitySetting.answer==answer)
            if or_expr != False: query = query.filter(or_expr)

        if args.offset != None: query = query.offset(args.offset)

        if args.limit != None: users = query.limit(args.limit)
        else: users = query.all()
        #return matches' ids
        return Response(status=200,message="Users found.",
            value={"users":[u.id for u in users]}).__dict__,200

    def post(self):
        parser = reqparse.RequestParser()
        #skip these args for now
        parser.add_argument("fb_id",
            type=str, location='form', required=True)
        parser.add_argument("longitude",
            type=float, location='form', required=False)
        parser.add_argument("latitude",
            type=float, location='form', required=False)
        parser.add_argument("about_me",
            type=str, location='form', required=False)
        parser.add_argument("primary_picture",
            type=str, location='form', required=False)
        parser.add_argument("dob",
            type=int, location='form', required=False)
        parser.add_argument("available",
            type=bool, location='form', required=False)
        parser.add_argument("name",
            type=str, location='form', required=False)
        parser.add_argument("gender",
            type=str, location='form', required=False)
        args = parser.parse_args()

        #return user if already exists
        user = User.query.filter(User.fb_id==args.fb_id).first()
        if user:
            return Response(status=200,
                message="User found.",
                value=user.dict_repr(public=False)).__dict__,200

        #create new user
        new_user = User(
            fb_id=args.fb_id,
            longitude=args.longitude,
            latitude=args.latitude,
            about_me=args.about_me,
            primary_picture=args.primary_picture,
            dob=args.dob,
            available=args.available,
            name=args.name,
            gender=args.gender
        )
        db.session.add(new_user)
        db.session.commit()

        #register jabber user
        try: new_user.register_jabber()
        except:
            db.session.delete(new_user)
            return Response(status=400,
               message="Could not create user.").__dict__,400 

        #return json for new user
        return Response(status=201,
            message="User created.",
            value=new_user.dict_repr(public=False)).__dict__,201

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
            user_dict = {x:user_dict[x] for x in user_dict\
                if x in args.attributes}

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
            type=str, location='form', required=False)
        parser.add_argument("secondary_pictures",
            type=str, location='form', required=False, action="append")
        parser.add_argument("about_me",
            type=str, location='form', required=False)
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
        if args.secondary_pictures:
            for pic in args.secondary_pictures:
                self.secondary_pictures.append(Picture(user,pic))
        if args.apn_tokens:
            for token in args.apn_tokens:
                self.apn_tokens.append(APNToken(user,pic))

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
            user.unregister_jabber()
            db.session.delete(user)
            db.session.commit()
        except:
            return Response(status=500,message="User not deleted.").__dict__,500

        return Response(status=200, message="User deleted.").__dict__,200
