from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
from flask.ext.socketio import emit
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from sqlalchemy import func,or_, and_, not_

from app import db, api, socketio
from app.models import *
from app.utils.Response import Response

@api.resource('/users')
class UsersAPI(Resource):
    def _age_to_day(self,age):
        day = datetime.now().date() - relativedelta(years=age)
        return int(time.mktime(day.timetuple()))
        
    def today(self):
        return int(time.mktime(datetime.now().date().timetuple()))

    def get(self):
        """
        Gets users that fall inside the specified parameters.
        
        :reqheader Authorization: Facebook token.

        :query float longitude: Specify a longitude to search by.
        :query float latitude: Specify a latitude to search by.
        :query int radius: Specify a radius to search by in meters.
        :query int limit: Limit the number of results.
        :query int offset: Return users after a given offset.
        :query int last_updated: Number of seconds since epoch;
            Return users that were updated before a given time.

        :status 200: Users found.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        parser.add_argument("longitude",
            type=float, location='args', required=False)
        parser.add_argument("latitude",
            type=float, location='args', required=False)
        parser.add_argument("radius",
            type=float, location='args', required=False)
        parser.add_argument("limit",
            type=int, location="args", required=False)
        parser.add_argument("offset",
            type=int, location="args", required=False)
        parser.add_argument("last_updated",
            type=int, location="args", required=False)
        args = parser.parse_args()
        
        #get user by fb_id; if no user then 401
        user = User.query.filter(User.fb_id==args.Authorization).first()
        if not user:
            return Response(status=401,message="Not Authorized.").__dict__,401

        #apply filters in args
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
            
        #apply filters in search settings
        #STILL NEED TO FILTER BY FRIENDS
        if user.search_settings.friends_only:
            pass
        else:
            if user.search_settings.men_only:
                query = query.filter(User.gender=="male")
            elif user.search_settings.women_only:
                query = query.filter(User.gender=="female")
            query = query.filter(User.dob>=_age_to_day(
                user.search_settings.lower_age_limit))
            query = query.filter(User.dob<=_age_to_day(
                user.search_settings.upper_age_limit))
        query = query.join(User.search_settings)
        query = query.filter(SearchSettings.activity_id==
                             user.search_settings.activity_id)
        query = query.join(User.activity_settings)
        for s in user.activity_settings.filter(Activity_Setting.activity_id==
            user.search_settings.activity_id).all():
            #make this show an intersection of lower and upper values, not equality
            query = query\
                .filter(and_(ActivitySetting.question_id==s.question_id,
                             not_(or_(and_(ActivitySetting.lower_value < s.lower_value,
                                           ActivitySetting.upper_value < s.lower_value,),
                                      and_(ActivitySetting.lower_value > s.upper_value,
                                           ActivitySetting.upper_value > s.upper_value)))))

        #ensure no repeat users as a result from an earlier join
        query = query.distinct(User.id)

        if args.offset != None: query = query.offset(args.offset)

        if args.limit != None: users = query.limit(args.limit)
        else: users = query.all()
        #return matches' ids
        return Response(status=200,message="Users found.",
            value={"users":[u.dict_repr() for u in users]}).__dict__,200

    def post(self):
        """
        Create new user if not already exists; return user

        :form str fb_id: Specify fb_id for user; must be unique for every user.
        :form float longitude: Specify a longitude to search by.
        :form float latitude: Specify a latitude to search by.
        :form str about_me: "About me" description of the user.
        :form str primary_picture: Picture ID string for primary picture.
        :form int dob: Integer number to represent DOB. THIS MAY CHANGE!
        :form bool available: Specify whether or not user is available.
        :form str name: Specify user name
        :form str gender: Specify user gender; I DON'T THINK THIS WORKS

        :status 200: User found.
        :status 201: User created.
        :status 400: Could not create user.
        """

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
            dob=args.dob,
            available=args.available,
            name=args.name,
            gender=args.gender
        )
        db.session.add(new_user)
        db.session.commit()

        #return json for new user
        return Response(status=201,
            message="User created.",
            value=new_user.dict_repr(public=False)).__dict__,201

@api.resource('/users/<int:user_id>')
class UserAPI(Resource):
    def get(self, user_id):
        """
        Get a user object by user_id

        :reqheader Authorization: Facebook token.

        :param int user_id: User to delete.

        :query str-list attributes: list of user attribute names to receive;
            if left empty, all attributes will be returned

        :status 200: User found.
        :status 404: User not found.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("attributes",
            type=str, location='args', required=False, action="append")
        parser.add_argument("Authorization",
            type=str, location="headers", required=False)
        args = parser.parse_args()
        
        #Get user from db
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=404,message="User not found.").__dict__,404
            
        if args.Authorization != None:
            #ensure user is valid by checking if fb_id is correct
            if user.fb_id != args.Authorization:
                return Response(status=401,message="Not Authorized.").__dict__,401
            user_dict = user.dict_repr(public=False)
        else:
            user_dict = user.dict_repr()

        #apply any attribute filters specified
        #CHANGE THIS TO user_dict=user.dict_repr(public=is_authorized)
        if args.attributes:
            user_dict = {x:user_dict[x] for x in user_dict\
                if x in args.attributes}

        #if attributes were specified, only return specified attributes
        return Response(status=200,
            message="User found.",value=user_dict).__dict__,200
    
    def put(self, user_id):
        """
        Update a user
        
        :reqheader Authorization: fb_id token needed here

        :param int user_id: User to delete.

        :form float longitude: Update user's longitude.
            Latitude must also be specified.
        :form float latitude: Update user's latitude.
            Longitude must also be specified.
        :form str primary_picture: Update user's primary_picture
        :form str about_me: Update user's about_me
        :form bool available: Update user's availability
        :form int dob: Update user's DOB; THIS WILL LIKELY CHANGE

        :status 400: "Could not find user" or "User updated failed".
        :status 401: Not Authorized.
        :status 202: User updated.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location='headers', required=True)
        parser.add_argument("longitude",
            type=float, location='form', required=False)
        parser.add_argument("latitude",
            type=float, location='form', required=False)
        parser.add_argument("primary_picture",
            type=str, location='form', required=False)
        parser.add_argument("secondary_pictures",
            type=str, location="form", required=False, action="append")
        parser.add_argument("about_me",
            type=str, location='form', required=False)
        parser.add_argument("available",
            type=bool, location='form', required=False)
        parser.add_argument("dob",
            type=int, location='form', required=False)
        args = parser.parse_args()

        #get user to update from db
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400,message="Could not find user.").__dict__,400

        #ensure user is valid by checking if fb_id is correct
        if user.fb_id != args.Authorization:
            return Response(status=401,message="Not Authorized.").__dict__,401

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

        #Update database and return whether or not the update was a success
        try: db.session.commit()
        except: return Response(status=400,
            message="User update failed.").__dict__, 400
        
        #reflect update in user's other clients
        socketio.emit("user_update", user.dict_repr(), room=str(user.id))

        return Response(status=202,message="User updated").__dict__,202

    def delete(self, user_id):
        """
        Delete a user
        
        :reqheader Authorization: fb_id token needed here

        :param int user_id: User to delete.

        :status 400: Could not find user.
        :status 401: Not Authorized.
        :status 500: User not deleted.
        :status 202: User updated.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location='headers', required=True)
        args = parser.parse_args()

        #get user from database
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400,
                message="Could not find user.").__dict__,404

        #ensure user is authorized to delete
        if user.fb_id != args.Authorization:
            return Response(status=401,
                message="Not Authorized.").__dict__,401
            
        db.session.delete(user)
        db.session.commit()

        return Response(status=200, message="User deleted.").__dict__,200
