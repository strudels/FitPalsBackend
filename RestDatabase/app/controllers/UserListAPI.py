from sqlalchemy import func
from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from app import api, db, jabber_db
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
        #radius in meters
        parser.add_argument("radius",
            type=float, location='args', required=False)
        parser.add_argument("limit",
            type=int, location="args", required=False)
        parser.add_argument("offset",
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

        #currently the database does not hold age information
        """
        if args.min_age:
            matches = [m for m in matches\
                if m["dob"] <= self._age_to_day(args.min_age)]

        if args.max_age:
            matches = [m for m in matches\
                if m["dob"] >= self._age_to_day(args.max_age)]
        """

        #Skipping activity filtering for now
        """
        if args.activity_name:
            query_args.append()
            matches = [m for m in matches
                if m['activity']['name'] == args.activity_name]

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
        """
        if args.offset != None: query = query.offset(args.offset)

        if args.limit != None: users = query.limit(args.limit)
        else: users = query.all()
        #return matches' ids
        return Response(status=200,message="Users found.",
            value={"users":[u.id for u in users]}).__dict__,200

    def post(self):
        parser = reqparse.RequestParser()
        #skip these args for now
        """
        parser.add_argument("apn_tokens",
            type=str, location='form', required=False, action="append")
        parser.add_argument("secondary_pictures",
            type=str, location='form', required=False, action="append")
        """
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
        except Exception as e:
            print "Exception: ", e
            db.session.delete(new_user)
            return Response(status=400,
               message="Could not create user.").__dict__,400 

        #return json for new user
        return Response(status=201,
            message="User created.",
            value=new_user.dict_repr(public=False)).__dict__,201
