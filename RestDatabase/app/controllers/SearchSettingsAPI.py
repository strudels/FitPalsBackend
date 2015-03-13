from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
from flask.ext.socketio import emit
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from sqlalchemy import func,or_, and_

from app import db, api, socketio
from app.models import *
from app.utils.Response import Response

@api.resource("/search_settings/<int:settings_id>")
class SearchSettingsAPI(Resource):
    def get(self, settings_id):
        """
        Get search settings.

        :reqheader Authorization: facebook secret

        :param int settings_id: Id of search settings.
        
        :status 401: Not Authorized.
        :status 404: Search settings not found.
        :status 200: Search settings found.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()

        #get search_settings
        settings = SearchSettings.query.get(settings_id)
        if not settings:
            return Response(status=404, message="Search settings not found.")\
                .__dict__,404
        
        #Ensure user is authorized to make change to settings
        user = settings.user
        if user.fb_secret != args.Authorization:
            return Response(status=401, message="Not Authorized.").__dict__,401
            
        return Response(status=200, message="Search settings found.",
                        value=settings.dict_repr()).__dict__, 200

    def put(self, settings_id):
        """
        Create new search setting.
        
        NOTE bool fields friends_only, men_only, and women_only are encoded as int
        because reqparse is dumb and I should've used something else.

        :reqheader Authorization: facebook secret
        
        :param int settings_id: Id of search settings.
        
        :form int activity_id: Activity id.
        :form int friends_only: Set to 1 if user wants friends only; Default is 0
        :form int men_only: Set to 1 if user wants men only; Default is 0
        :form int women_only: Set to 1 if user wants women only; Default is 0
        :form int age_lower_limit: Set if user want lower age limit. Default is 18.
        :form int age_upper_limit: Set if user want upper age limit. Default is 130.
        http://en.wikipedia.org/wiki/Oldest_people
        
        :status 400: Search settings could not be updated.
        :status 401: Not Authorized.
        :status 404: Search settings not found.
        :status 202: Search settings updated.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        parser.add_argument("activity_id",
            type=int, location="form", required=False)
        parser.add_argument("friends_only",
            type=int, location="form", required=False)
        parser.add_argument("men_only",
            type=int, location="form", required=False)
        parser.add_argument("women_only",
            type=int, location="form", required=False)
        parser.add_argument("age_lower_limit",
            type=int, location="form", required=False)
        parser.add_argument("age_upper_limit",
            type=int, location="form", required=False)
        args = parser.parse_args()
        if type(args.friends_only)==type(int()):
            args.friends_only = bool(args.friends_only)
        if type(args.men_only)==type(int()):
            args.men_only = bool(args.men_only)
        if type(args.women_only)==type(int()):
            args.women_only = bool(args.women_only)
        
        #get search_settings
        settings = SearchSettings.query.get(settings_id)
        if not settings:
            return Response(status=404, message="Search settings not found.")\
                .__dict__,404
            
        #Ensure user is authorized to make change to settings
        user = settings.user
        if user.fb_secret != args.Authorization:
            return Response(status=401, message="Not Authorized.").__dict__,401
            
        #update search_settings
        try:
            for arg in args.keys():
                if args[arg] != None: setattr(settings,arg,args[arg])
            db.session.commit()
        except:
            return Response(status=400,
                message="Search settings could not be updated.")\
                .__dict__,400
            db.session.rollback()
            
        #send update to user's other devices
        socketio.emit("search_settings_update", settings.dict_repr(),
                      room=str(user.id))

        return Response(status=202,message="Search settings updated.",
                        value=settings.dict_repr()).__dict__,202
