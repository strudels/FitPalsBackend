from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from app import db, api
from app.models import *
from app.utils.Response import Response

@api.resource('/users')
class UserListAPI(Resource):
    def _age_to_day(self,age):
        day = datetime.now().date() - relativedelta(years=age)
        return int(time.mktime(day.timetuple()))

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("longitude",
            type=float, location='args', required=False)
        parser.add_argument("latitude",
            type=float, location='args', required=False)
        parser.add_argument("radius",
            type=float, location='args', required=False)
        parser.add_argument("limit",
            type=int, location="args", required=False)
        parser.add_argument("index",
            type=int, location="args", required=False)
        parser.add_argument("last_updated",
            type=int, location="args", required=False)
        parser.add_argument("min_age",
            type=int, location="args", required=False)
        parser.add_argument("max_age",
            type=int, location="args", required=False)
        parser.add_argument("activity_name",
            type=str, location="args", required=False)
        parser.add_argument("activity_distance",
            type=int, location="args", required=False)
        parser.add_argument("activity_time",
            type=int, location="args", required=False)
        parser.add_argument("jabber_id",
            type=str, location="args", required=False)
        args = parser.parse_args()

        #apply filters specified by user to matches
        if not (args.radius and args.longitude and args.latitude):
            matches = database.get_users()
        else: 
            #ensure GPS parameters are valid
            if (args.radius <= 0) or not (-180 <= args.longitude <= 180)\
                or not (-90 <= args.latitude <= 90):
                return Response(status=400,message="Invalid GPS parameters"),400
            matches = database.get_nearby_users(args.longitude,
                args.latitude, args.radius)

        if args.last_updated:
            matches = [m for m in matches\
                if m["last_updated"] <= args.last_updated]

        if args.min_age:
            matches = [m for m in matches\
                if m["dob"] <= self._age_to_day(args.min_age)]

        if args.max_age:
            matches = [m for m in matches\
                if m["dob"] >= self._age_to_day(args.max_age)]

        if args.activity_name:
            matches = [m for m in matches
                if m['activity']['name'] == args.activity_name]

        if args.jabber_id:
            matches = [m for m in matches
                if m['jabber_id'] == args.jabber_id]

        if args.activity_distance:
            for m in matches:
                m['activity']['distance'] =\
                    abs(m['activity']['distance'] - args.activity_distance)
            matches.sort(key=lambda x:x['activity']['distance'])

        if args.activity_time:
            for m in matches:
                m['activity']['time'] =\
                    abs(m['activity']['time'] - user['activity']['time'])
            matches.sort(key=lambda x:x['activity']['time'])

        if args.limit!=None and args.index!=None:
            matches = matches[args.index:args.index+args.limit]

        #return matches' user_ids
        return Response(status=200,message="Matches found.",
            value={"users":[str(m["user_id"]) for m in matches]}).__dict__,200

    def post(self):
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

        #return user_id, jabber_id, and password if user already exists
        try:
            user = database.find_user_by_fb_id(args.fb_id)
            user["user_id"] = str(user["user_id"])
            return Response(status=200,message="User found.",
                value=user_id).__dict__,200
        except: pass

        #create new user and return it's new user_id, jabber_id, and password
        try: new_user = database.insert_user(args.fb_id)
        except:
            return Response(status=400,
                message="Invalid fb_id.").__dict__,400

        #update fields specified by client
        if args.longitude and args.latitude:
            new_user["location"] = [args.longitude,args.latitude]
        if args.primary_picture:
            new_user["primary_picture"] = args.primary_picture
        if args.secondary_pictures:
            new_user["secondary_pictures"] = args.secondary_pictures
        if args.about_me: new_user["about_me"] = args.about_me
        if args.available: new_user["available"] = args.available
        if args.dob: new_user["dob"] = args.dob
        if args.apn_tokens: new_user["apn_tokens"] = args.apn_tokens

        #Update database and return whether or not the update was a success
        try: update_status = database.update_user(new_user["user_id"],new_user)
        except: update_status = None #update failed
        if not update_status or update_status["ok"]!=1:
            #delete newly created user, since update failed
            if not database.delete_user(new_user["user_id"]):
                #log that a user fragment was created
                pass
            return Response(status=400,
                message="Could not create user.").__dict__,400

        #delete _id field, user_id is still in new_user
        #hack
        del new_user["_id"]
        return Response(status=201, message="User created.", value=new_user).__dict__, 201
