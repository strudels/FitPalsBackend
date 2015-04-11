from flask import Flask, request
from flask.ext.restful import Resource, reqparse, Api
from flask.ext.socketio import emit
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from sqlalchemy import func,or_, and_, not_
from datetime import date

from app import db, api, app, exception_is_validation_error
from app.models import *
from app.utils.Response import Response
from app.utils import Facebook
from app.utils.AsyncNotifications import send_message

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

        :query int limit: Limit the number of results.

        :status 401: Not Authorized.
        :status 500: Internal Error.
        :status 200: Users found.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        parser.add_argument("limit",
            type=int, location="args", required=False)
        args = parser.parse_args()
        
        try:
            #get user by fb_id; if no user then 401
            user = User.query.filter(User.fitpals_secret==args.Authorization).first()
            if not user:
                return Response(status=401,message="Not Authorized.").__dict__,401

            #return no users if user running query has not specified any
            # activity settings
            settings = user.activity_settings.all()
            if not settings:
                return Response(status=200,message="Users found.",value=[])\
                    .__dict__,200

            #begin creating query
            query = User.query.filter(User.id!=user.id)
            query = query.join(User.search_settings)
            query = query.join(User.activity_settings)

            #filter out users that the querying user has already made a decision on
            query = query.filter(~User.id.in_(
                user.matches.with_entities(Match.matched_user_id)))

            #filter out users not marked as available
            query = query.filter(SearchSettings.available==True)

            #filter by activity preferences
            if settings:
                s = settings[0]
                or_expr = and_(ActivitySetting.question_id==s.question_id,
                                        not_(or_(ActivitySetting.upper_value_converted <
                                                        s.lower_value_converted,
                                                ActivitySetting.lower_value_converted >
                                                        s.upper_value_converted)))
                for s in settings[1:]:
                    and_expr = and_(ActivitySetting.question_id==s.question_id,
                                    not_(or_(ActivitySetting.upper_value_converted <
                                                    s.lower_value_converted,
                                            ActivitySetting.lower_value_converted >
                                                    s.upper_value_converted)))
                    or_expr = or_(or_expr,and_expr)
                #also match users that don't have any activity settings
                query = query.filter(or_expr)

            #apply filters in user's search settings
            if user.search_settings.friends_only:
                #wrap in try except, incase Facebook doesn't respond
                try: friend_fb_ids = Facebook.get_user_friends(user.fb_id)
                except :
                    return Response(status=500,message="Internal Error."),500
                users = query.filter(User.fb_id in friend_fb_ids).all()
                users += [f.friend_user for f in user.friends.all()]
                users = list(set([u.dict_repr() for u in users]))
                return Response(status=200,message="Users found.",
                                value=users).__dict__,200
            else:
                gender_or = or_()
                if user.search_settings.men and user.search_settings.women:
                    query = query.filter(or_(User.gender=="female", User.gender=="male"))
                elif user.search_settings.women:
                    query = query.filter(User.gender=="female")
                else: #user.search_settings.men == True
                    query = query.filter(User.gender=="male")
                query = query.filter(User.dob<=self._age_to_day(
                    user.search_settings.age_lower_limit))
                query = query.filter(User.dob>=self._age_to_day(
                    user.search_settings.age_upper_limit))

            #apply filters from other user's search settings
            if user.gender == "male":
                query = query.filter(SearchSettings.men==True)
            else: #user.gender == "female"
                query = query.filter(SearchSettings.women==True)

            #apply gps filter
            other_in_user_range = func.ST_DWithin(user.location, User.location,
                user.search_settings.radius_converted, True)
            user_in_other_range = func.ST_DWithin(user.location, User.location,
                SearchSettings.radius_converted, True)
            query = query.filter(and_(other_in_user_range, user_in_other_range))

            #ensure no repeat users as a result from an earlier join
            query = query.distinct(User.id)

            if args.limit != None: users = query.limit(args.limit)
            users = [u.dict_repr() for u in query.all()]
            #return matches' ids
            return Response(status=200,message="Users found.",
                            value=users).__dict__,200
        except Exception as e:
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500

    def post(self):
        """
        Create new user if not already exists; return user

        :form str access_token: Specify fb access token for user from login dialogue.
        :form float longitude: Specify a longitude to search by.
        :form float latitude: Specify a latitude to search by.
        :form str about_me: "About me" description of the user.
        :form str primary_picture: Picture ID string for primary picture.
        :form int dob_year: Integer number to represent DOB year.
        :form int dob_month: Integer number to represent DOB month.
        :form int dob_day: Integer number to represent DOB day.
        :form str name: Specify user name
        :form str gender: Specify user gender; I DON'T THINK THIS WORKS

        :status 400: Invalid user data.
        :status 401: Not Authorized.
        :status 200: User found.
        :status 201: User created.
        """

        parser = reqparse.RequestParser()
        #skip these args for now
        parser.add_argument("access_token",
            type=str, location="form",required=True)
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
        parser.add_argument("name",
            type=str, location='form', required=False)
        parser.add_argument("gender",
            type=str, location='form', required=True)
        args = parser.parse_args()
        
        try:
            #if no fb_id is found for the given access token, the user is not auth'd
            fb_id = Facebook.get_fb_id_via_access_token(args.access_token)
            if not fb_id:
                return Response(status=401, message="Not Authorized.")\
                    .__dict__,401

            #return user if already exists
            user = User.query.filter(User.fb_id==fb_id).first()
            if user:
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
            new_user = User(
                fb_id=fb_id,
                fitpals_secret=Facebook.create_fitpals_secret(),
                longitude=args.longitude,
                latitude=args.latitude,
                about_me=args.about_me,
                dob=date(args.dob_year,args.dob_month,args.dob_day),
                name=args.name,
                gender=args.gender
            )
            db.session.add(new_user)
            db.session.commit()

            #return json for new user
            return Response(status=201,
                message="User created.",
                value=new_user.dict_repr(public=False)).__dict__,201
        except Exception as e:
            if exception_is_validation_error(e):
                return Response(status=400,
                    message="Invalid user data.").__dict__,400
            db.session.rollback()
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500

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
        
        try:
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
        except Exception as e:
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500
    
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
        parser.add_argument("dob_year",
            type=int, location='form', required=False)
        parser.add_argument("dob_month",
            type=int, location='form', required=False)
        parser.add_argument("dob_day",
            type=int, location='form', required=False)
        args = parser.parse_args()
        
        try:
            #get user to update from db
            user = User.query.filter(User.id==user_id).first()
            if not user:
                return Response(status=404,message="User not found.").__dict__,404

            #ensure user is valid by checking if fb_id is correct
            if user.fitpals_secret != args.Authorization:
                return Response(status=401,message="Not Authorized.").__dict__,401

            #update fields specified by client
            if args.longitude and args.latitude:
                user.location =\
                    WKTElement("POINT(%f %f)"%(args.longitude,args.latitude))
            if args.primary_picture: user.primary_picture = args.primary_picture
            if args.about_me: user.about_me = args.about_me
            if args.dob_year!=None and args.dob_month!=None and args.dob_day!=None:
                user.dob = date(args.dob_year,args.dob_month,args.dob_day)
            if args.secondary_pictures:
                for pic in args.secondary_pictures:
                    self.secondary_pictures.append(Picture(user,pic))

            #Update database
            db.session.commit()

            #reflect update in user's other clients
            send_message(user.dict_repr(show_online_status=True),
                        [d.token for d in user.devices.all()],
                        request.path,request.method,user.dict_repr())

            return Response(status=202,message="User updated",
                            value=user.dict_repr()).__dict__,202
        except Exception as e:
            if exception_is_validation_error(e):
                return Response(status=400,
                    message="Invalid user data.").__dict__,400
            db.session.rollback()
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500

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

        try:
            #get user from database
            user = User.query.filter(User.id==user_id).first()
            if not user:
                return Response(status=404,
                    message="User not found.").__dict__,404

            #ensure user is authorized to delete
            if user.fitpals_secret != args.Authorization:
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
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500
