from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from app import db, api, socketio
from app.models import *
from app.utils.Response import Response

@api.resource("/activities")
class ActivitiesAPI(Resource):
    #get's all possible activities
    def get(self):
        """
        Get all possible activities.

        :status 200: Activities found.
        """
        return Response(status=200,message="Activites found.",
            value=[a.dict_repr() for a in Activity.query.all()]).__dict__, 200

@api.resource('/activity_settings')
class UserActivitySettingsAPI(Resource):
    #get's all activities for a specific user
    def get(self):
        """
        Get all activity settings for a user, specified by Authorization

        :reqheader Authorization: facebook token

        :status 401: Not Authorized.
        :status 200: Activity settings found.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()

        #get user via user_id
        user = User.query.filter(User.fb_id == args.Authorization).first()
        if not user:
            return Response(status=401,message="Not Authorized.").__dict__,401

        return Response(status=200, message="Activity settings found.",
            value=[a.dict_repr() for a in user.activity_settings]).__dict__,200

    #add activity setting to user's activity setting list
    def post(self):
        """
        Post new activity setting for user

        :reqheader Authorization: facebook token

        :form int user_id: Id of user.
        :form int question_id: Id of question.
        :form float lower_value: Lower value answer for question.
        :form float upper_value: Upper value answer for question.

        :status 401: Not Authorized.
        :status 404: Question not found.
        :status 404: User not found.
        :status 500: Could not create activity setting.
        :status 201: Activity setting created.
        """

        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location='headers', required=True)
        parser.add_argument("user_id",
            type=int,location="form", required=True)
        parser.add_argument("question_id",
            type=int,location="form", required=True)
        parser.add_argument("lower_value",
            type=float, location="form", required=True)
        parser.add_argument("upper_value",
            type=float, location="form", required=True)
        args = parser.parse_args()

        #get question
        question = Question.query.get(args.question_id)
        if not question:
            return Response(status=404,message="Question not found.")\
                .__dict__, 404

        #get user
        user = User.query.get(args.user_id)
        if not user:
            return Response(status=404,message="User not found.").__dict__,404

        #ensure user is authorized by checking if fb_id is correct
        if user.fb_id != args.Authorization:
            return Response(status=401,message="Not Authorized.").__dict__,401

        # add setting to user's activity settings
        try: 
            activity_setting =\
                ActivitySetting(user,question,args.lower_value,args.upper_value)
            user.activity_settings.append(activity_setting)
            db.session.commit()
        except: 
            db.session.rollback()
            return Response(status=400,
                message="Could not create activity setting.").__dict__,400
            
        socketio.emit("activity_setting_added",activity_setting.dict_repr(),
                      room=str(activity_setting.user.id))
        
        return Response(status=201,message="Activity setting created.",
                        value=activity_setting.dict_repr()).__dict__,201

#activity_id maps to an ActivitySetting id
@api.resource("/activity_settings/<int:setting_id>")
class ActivitySettingAPI(Resource):
    #get settings for user's specific activity
    def get(self, setting_id):
        """
        Get specific activity setting
        
        :reqheader Authorization: fb_id token needed here

        :status 401: Not Authorized.
        :status 404: Activity setting not found.
        :status 202: Activity setting found.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()
        
        #get setting
        setting = ActivitySetting.query.get(setting_id)
        if not setting:
            return Response(status=404,message="Activity setting not found.")\
                .__dict__, 404
            
        #Ensure that user is authorized
        if setting.user.fb_id != args.Authorization:
            return Response(status=401,message="Not Authorized.").__dict__,401

        return Response(status=200, message="Activity setting found.",
                        value=setting.dict_repr()).__dict__, 200

    def put(self, setting_id):
        """
        Update specific activity setting

        :reqheader Authorization: fb_id token needed here

        :form float lower_value: Lower value answer to question.
        :form float upper_value: Upper value answer to question.

        :status 400: Could not update activity setting.
        :status 401: Not Authorized.
        :status 404: Activity setting not found.
        :status 202: Activity setting updated.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location='headers', required=True)
        parser.add_argument("lower_value",
            type=float,location="form",required=True)
        parser.add_argument("upper_value",
            type=float,location="form",required=True)
        args = parser.parse_args()
        
        #get setting
        setting = ActivitySetting.query.get(setting_id)
        if not setting:
            return Response(status=404,message="Activity setting not found.")\
                .__dict__, 404

        #ensure user is valid by checking if fb_id is correct
        if setting.user.fb_id != args.Authorization:
            return Response(status=401,message="Not Authorized.").__dict__,401
            
        try:
            setting.lower_value = args.lower_value
            setting.upper_value = args.upper_value
            db.session.commit()
        except:
            db.session.rollback()
            return Response(status=400,
                message="Could not update activity setting.").__dict__,400
            
        socketio.emit("activity_setting_updated",setting.dict_repr(),
                      room=str(setting.user.id))

        return Response(status=202,
                        message="Activity setting updated.",
                        value=setting.dict_repr()).__dict__,202

    #delete user's specific activity
    def delete(self, setting_id):
        """
        Delete user's activity settings for a specific activity

        :reqheader Authorization: fb_id token needed here

        :param int setting_id: Id of activity setting.

        :status 400: User not found.
        :status 202: Activity setting deleted.
        """

        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location='headers', required=True)
        args = parser.parse_args()

        #get setting
        setting = ActivitySetting.query.get(setting_id)
        if not setting:
            return Response(status=404,message="Activity setting not found.")\
                .__dict__, 404
        user = setting.user

        #ensure user is valid by checking if fb_id is correct
        if setting.user.fb_id != args.Authorization:
            return Response(status=401,message="Not Authorized.").__dict__,401
            
        setting.user.activity_settings.remove(setting)
        db.session.commit()

        socketio.emit("activity_setting_deleted",setting_id,
                      room=str(user.id))

        return Response(status=200,
            message="Activity setting deleted.").__dict__, 200
