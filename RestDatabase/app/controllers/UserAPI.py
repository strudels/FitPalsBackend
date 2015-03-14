from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
from flask.ext.socketio import emit
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from sqlalchemy import func,or_, and_, not_
from datetime import date

from app import db, api, socketio
from app.models import *
from app.utils.Response import Response

@api.resource('/users')
class UsersAPI(Resource):
    def _age_to_day(self,age):
        return datetime.now().date() - relativedelta(years=age)
        
    def today(self):
        return int(time.mktime(datetime.now().date().timetuple()))

    def get(self):
        """
        Gets users that fall inside the specified parameters
             and the authorized user's search settings
        
        :reqheader Authorization: facebook secret

        :query float longitude: Specify a longitude to search by.
        :query float latitude: Specify a latitude to search by.
        :query int radius: Specify a radius to search by in meters.
        :query int limit: Limit the number of results.
        :query int offset: Return users after a given offset.
        :query int last_updated: Number of seconds since epoch;
            Return users that were updated before a given time.

        :status 400: Invalid GPS parameters.
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
        user = User.query.filter(User.fb_secret==args.Authorization).first()
        if not user:
            return Response(status=401,message="Not Authorized.").__dict__,401
            
        #begin creating query
        query = User.query

        #apply filters in search settings
        #STILL NEED TO FILTER BY FRIENDS
        if user.search_settings.friends_only:
            pass
        else:
            if user.search_settings.men_only:
                query = query.filter(User.gender=="male")
            elif user.search_settings.women_only:
                query = query.filter(User.gender=="female")
            query = query.filter(User.dob>=self._age_to_day(
                user.search_settings.age_lower_limit))
            query = query.filter(User.dob<=self._age_to_day(
                user.search_settings.age_upper_limit))
        query = query.join(User.search_settings)
        query = query.filter(SearchSettings.activity_id==
                             user.search_settings.activity_id)

        #filter by activity preferences
        or_expr = None
        query = query.join(User.activity_settings)
        for s in user.activity_settings\
                     .join(ActivitySetting.question)\
                     .filter(Question.activity_id==
                            user.search_settings.activity_id).all():
            and_expr = and_(ActivitySetting.question_id==s.question_id,
                            not_(or_(and_(ActivitySetting.lower_value_converted <
                                              s.lower_value_converted,
                                          ActivitySetting.upper_value_converted <
                                              s.lower_value_converted,),
                                     and_(ActivitySetting.lower_value_converted >
                                              s.upper_value_converted,
                                          ActivitySetting.upper_value_converted >
                                              s.upper_value_converted))))
            or_expr = or_(or_expr,an_expr)
        query = query.filter(or_expr)

        #apply filters in args
        if args.last_updated:
            query = query.filter(User.last_updated<=args.last_updated)
        query = User.query
        if (args.radius and args.longitude and args.latitude):
            #ensure GPS parameters are valid
            if (args.radius <= 0) or not (-180 <= args.longitude <= 180)\
                or not (-90 <= args.latitude <= 90):
                return Response(status=400,message="Invalid GPS parameters.")\
                    .__dict__,400
            point = func.ST_GeomFromText("POINT(%f %f)" %\
                                         (args.longitude,args.latitude)) 
            arg = func.ST_DWithin(point, User.location, args.radius, True)
            query = query.filter(arg)
            
        #ensure no repeat users as a result from an earlier join
        query = query.distinct(User.id)

        if args.offset != None: query = query.offset(args.offset)

        if args.limit != None: users = query.limit(args.limit)
        else: users = query.all()
        #return matches' ids
        return Response(status=200,message="Users found.",
            value=[u.dict_repr() for u in users]).__dict__,200

    def post(self):
        """
        Create new user if not already exists; return user

        :form str fb_id: Specify fb_id for user; must be unique for every user.
        :form str fb_secret: Specify fb_secret for user; must be unique for every user.
        :form float longitude: Specify a longitude to search by.
        :form float latitude: Specify a latitude to search by.
        :form str about_me: "About me" description of the user.
        :form str primary_picture: Picture ID string for primary picture.
        :form int dob_year: Integer number to represent DOB year.
        :form int dob_month: Integer number to represent DOB month.
        :form int dob_day: Integer number to represent DOB day.
        :form bool available: Specify whether or not user is available.
        :form str name: Specify user name
        :form str gender: Specify user gender; I DON'T THINK THIS WORKS

        :status 400: Must specify DOB.
        :status 400: Could not create user.
        :status 401: Not Authorized.
        :status 500: Internal error. Changes not committed.
        :status 200: User found.
        :status 201: User created.
        """

        parser = reqparse.RequestParser()
        #skip these args for now
        parser.add_argument("fb_id",
            type=str, location='form', required=True)
        parser.add_argument("fb_secret",
            type=str, location='form', required=True)
        parser.add_argument("longitude",
            type=float, location='form', required=False)
        parser.add_argument("latitude",
            type=float, location="form", required=False)
        parser.add_argument("about_me",
            type=str, location="form", required=False)
        parser.add_argument("primary_picture",
            type=str, location="form", required=False)
        parser.add_argument("dob_year",
            type=int, location="form", required=False)
        parser.add_argument("dob_month",
            type=int, location="form", required=False)
        parser.add_argument("dob_day",
            type=int, location="form", required=False)
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
            #if user fb_secret is incorrect, 401
            if user.fb_secret != args.fb_secret:
                return Response(status=401, message="Not Authorized.")\
                    .__dict__,401
            return Response(status=200,
                message="User found.",
                value=user.dict_repr(public=False)).__dict__,200
            
        #ensure user specifys date of birth
        if args.dob_year==None or args.dob_month==None or args.dob_day==None:
            return Response(status=400, message="Must specify DOB.").__dict__,400
            
        if args.longitude!=None and args.latitude!=None\
            and (not (-180 <= args.longitude <= 180)\
                 or not (-90 <= args.latitude <= 90)):
            return Response(status=400, message="Coordinates invalid.")\
                .__dict__,400

        #add user to db
        try:
            new_user = User(
                fb_id=args.fb_id,
                fb_secret=args.fb_secret,
                longitude=args.longitude,
                latitude=args.latitude,
                about_me=args.about_me,
                dob=date(args.dob_year,args.dob_month,args.dob_day),
                available=args.available,
                name=args.name,
                gender=args.gender
            )
            db.session.add(new_user)
            db.session.commit()
        except:
            db.session.rollback()
            return Response(status=500,
                message="Internal error. Changes not committed.").__dict__,500

        #return json for new user
        return Response(status=201,
            message="User created.",
            value=new_user.dict_repr(public=False)).__dict__,201

@api.resource('/users/<int:user_id>')
class UserAPI(Resource):
    def get(self, user_id):
        """
        Get a user object by user_id

        :param int user_id: User to delete.

        :query str-list attributes: list of user attribute names to receive;
            if left empty, all attributes will be returned

        :status 200: User found.
        :status 404: User not found.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("attributes",
            type=str, location='args', required=False, action="append")
        args = parser.parse_args()
        
        #Get user from db
        user = User.query.get(user_id)
        if not user:
            return Response(status=404,message="User not found.").__dict__,404
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
        
        :reqheader Authorization: facebook secret

        :param int user_id: User to delete.

        :form float longitude: Update user's longitude.
            Latitude must also be specified.
        :form float latitude: Update user's latitude.
            Longitude must also be specified.
        :form str primary_picture: Update user's primary_picture
        :form str about_me: Update user's about_me
        :form bool available: Update user's availability
        :form int dob: Update user's DOB; THIS WILL LIKELY CHANGE

        :status 401: Not Authorized.
        :status 404: User not found.
        :status 500: Internal error. Changes not committed.
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
        parser.add_argument("dob_year",
            type=int, location='form', required=False)
        parser.add_argument("dob_month",
            type=int, location='form', required=False)
        parser.add_argument("dob_day",
            type=int, location='form', required=False)
        args = parser.parse_args()

        #get user to update from db
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=404,message="User not found.").__dict__,404

        #ensure user is valid by checking if fb_id is correct
        if user.fb_secret != args.Authorization:
            return Response(status=401,message="Not Authorized.").__dict__,401

        #update fields specified by client
        if args.longitude and args.latitude:
            user.location =\
                WKTElement("POINT(%f %f)"%(args.longitude,args.latitude))
        if args.primary_picture: user.primary_picture = args.primary_picture
        if args.about_me: user.about_me = args.about_me
        if args.available: user.available = args.available
        if args.dob_year!=None and args.dob_month!=None and args.dob_day!=None:
            user.dob = date(args.dob_year,args.dob_month,args.dob_day)
        if args.secondary_pictures:
            for pic in args.secondary_pictures:
                self.secondary_pictures.append(Picture(user,pic))

        #Update database and return whether or not the update was a success
        try: db.session.commit()
        except:
            db.session.rollback()
            return Response(status=500,
                message="Internal error. Changes not committed.").__dict__, 500
        
        #reflect update in user's other clients
        socketio.emit("user_update", user.dict_repr(), room=str(user.id))

        return Response(status=202,message="User updated",
                        value=user.dict_repr()).__dict__,202

    def delete(self, user_id):
        """
        Delete a user
        
        :reqheader Authorization: facebook secret

        :param int user_id: User to delete.

        :status 401: Not Authorized.
        :status 404: User not found.
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
            return Response(status=404,
                message="User not found.").__dict__,404

        #ensure user is authorized to delete
        if user.fb_secret != args.Authorization:
            return Response(status=401,
                message="Not Authorized.").__dict__,401
            
        try:
            db.session.delete(user)
            db.session.commit()
        except: 
            db.session.rollback()
            return Response(status=500,
                message="Internal error. Changes not committed.").__dict__, 500

        return Response(status=200, message="User deleted.").__dict__,200
