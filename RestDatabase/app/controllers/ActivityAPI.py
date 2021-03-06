from flask import Flask, request
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from app import db, api, app, exception_is_validation_error
from app.models import *
from app.utils.Response import Response
from app.utils.AsyncNotifications import send_message

@api.resource("/activities")
class ActivitiesAPI(Resource):
    #get's all possible activities
    def get(self):
        """
        Get all possible activities.

        :status 200: Activities found.
        """
        try:
            return Response(status=200,message="Activites found.",
                value=[a.dict_repr() for a in Activity.query.all()]).__dict__, 200
        except Exception as e:
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500
        
@api.resource("/activities/<int:activity_id>/questions")
class ActivityQuestionsAPI(Resource):
    def get(self, activity_id):
        """
        Get all questions for an activity.
        
        :status 404: Activity not found.
        :status 200: Questions found.
        """
        activity = Activity.query.get(activity_id)
        if not activity:
            return Response(status=404, message="Activity not found.").__dict__,\
                404

        try:
            return Response(status=200, message="Questions found.",
                            value=[q.dict_repr() for q in activity.questions.all()])\
                            .__dict__, 200
        except Exception as e:
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500
        
@api.resource("/questions")
class QuestionsAPI(Resource):
    def get(self):
        """
        Get all questions for all activities.
        
        :status 200: Questions found.
        """
        try:
            return Response(status=200,message="Questions found.",
                value=[q.dict_repr() for q in Question.query.all()]).__dict__,200
        except Exception as e:
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500

@api.resource('/activity_settings')
class UserActivitySettingsAPI(Resource):
    #get's all activities for a specific user
    def get(self):
        """
        Get all activity settings for a user, specified by Authorization

        :reqheader Authorization: facebook secret

        :status 401: Not Authorized.
        :status 200: Activity settings found.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()

        #get user via user_id
        try:
            user = User.query.filter(User.fitpals_secret == args.Authorization).first()
        except Exception as e:
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500
        if not user:
            return Response(status=401,message="Not Authorized.").__dict__,401

        return Response(status=200, message="Activity settings found.",
            value=[a.dict_repr() for a in user.activity_settings]).__dict__,200

    #add activity setting to user's activity setting list
    def post(self):
        """
        Post new activity setting for user

        :reqheader Authorization: facebook secret

        :form int user_id: Id of user.
        :form int question_id: Id of question.
        :form float lower_value: Lower value answer for question.
        :form float upper_value: Upper value answer for question.
        :form str unit_type: Name of type of unit; i.e. meter

        :status 400: Activity setting data invalid.
        :status 401: Not Authorized.
        :status 404: Question not found.
        :status 404: User not found.
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
        parser.add_argument("unit_type",
            type=str, location='form', required=True)
        args = parser.parse_args()

        #get question
        try:
            question = Question.query.get(args.question_id)
            if not question:
                return Response(status=404,message="Question not found.")\
                    .__dict__, 404

        #get user
            user = User.query.get(args.user_id)
            if not user:
                return Response(status=404,message="User not found.").__dict__,404

            #ensure user is authorized by checking if fb_id is correct
            if user.fitpals_secret != args.Authorization:
                return Response(status=401,message="Not Authorized.").__dict__,401

            # add setting to user's activity settings
            activity_setting = ActivitySetting(user,question,args.unit_type,
                                            args.lower_value,args.upper_value)
            user.activity_settings.append(activity_setting)
            db.session.commit()

            send_message(activity_setting.user,request.path,request.method,
                         value=activity_setting.dict_repr())

            return Response(status=201,message="Activity setting created.",
                            value=activity_setting.dict_repr()).__dict__,201
        except Exception as e:
            if exception_is_validation_error(e):
                return Response(status=400,
                    message="Activity setting data invalid.").__dict__,400
            db.session.rollback()
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500

#activity_id maps to an ActivitySetting id
@api.resource("/activity_settings/<int:setting_id>")
class ActivitySettingAPI(Resource):
    #get settings for user's specific activity
    def get(self, setting_id):
        """
        Get specific activity setting
        
        :reqheader Authorization: facebook secret

        :status 401: Not Authorized.
        :status 404: Activity setting not found.
        :status 202: Activity setting found.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()
        
        #get setting
        try:
            setting = ActivitySetting.query.get(setting_id)
            if not setting:
                return Response(status=404,message="Activity setting not found.")\
                    .__dict__, 404
        except Exception as e:
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500
            
        #Ensure that user is authorized
        if setting.user.fitpals_secret != args.Authorization:
            return Response(status=401,message="Not Authorized.").__dict__,401

        return Response(status=200, message="Activity setting found.",
                        value=setting.dict_repr()).__dict__, 200

    def put(self, setting_id):
        """
        Update specific activity setting

        :reqheader Authorization: facebook secret

        :form float lower_value: Lower value answer to question.
        :form float upper_value: Upper value answer to question.
        :form str unit_type: Name of type of unit; i.e. meter

        :status 400: Activity settings data invalid.
        :status 401: Not Authorized.
        :status 404: Activity setting not found.
        :status 202: Activity setting updated.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location='headers', required=True)
        parser.add_argument("lower_value",
            type=float,location="form",required=False)
        parser.add_argument("upper_value",
            type=float,location="form",required=False)
        parser.add_argument("unit_type",
            type=str,location="form",required=False)
        args = parser.parse_args()
        
        try:
            #get setting
            setting = ActivitySetting.query.get(setting_id)
            if not setting:
                return Response(status=404,message="Activity setting not found.")\
                    .__dict__, 404

            #ensure user is valid by checking if fb_id is correct
            if setting.user.fitpals_secret != args.Authorization:
                return Response(status=401,message="Not Authorized.").__dict__,401

            if args.unit_type != None: setting.unit_type = args.unit_type
            if args.lower_value != None: setting.lower_value = args.lower_value
            if args.upper_value != None: setting.upper_value = args.upper_value
            db.session.commit()

            send_message(setting.user,request.path,request.method,
                         value=setting.dict_repr())

            return Response(status=202,
                            message="Activity setting updated.",
                            value=setting.dict_repr()).__dict__,202
        except Exception as e:
            if exception_is_validation_error(e):
                return Response(status=400,
                    message="Activity setting data invalid.").__dict__,400
            db.session.rollback()
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500

    #delete user's specific activity
    def delete(self, setting_id):
        """
        Delete Activity Setting

        :reqheader Authorization: facebook secret

        :param int setting_id: Id of activity setting.

        :status 401: Not Authorized.
        :status 404: Activity setting not found.
        :status 500: Internal error. Changes not committed.
        :status 202: Activity setting deleted.
        """

        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location='headers', required=True)
        args = parser.parse_args()

        try:
            #get setting
            setting = ActivitySetting.query.get(setting_id)
            if not setting:
                return Response(status=404,message="Activity setting not found.")\
                    .__dict__, 404
            user = setting.user

            #ensure user is valid by checking if fb_id is correct
            if setting.user.fitpals_secret != args.Authorization:
                return Response(status=401,message="Not Authorized.").__dict__,401

            setting.user.activity_settings.remove(setting)
            db.session.delete(setting)
            db.session.commit()

            send_message(user,request.path,request.method)

            return Response(status=200,
                message="Activity setting deleted.").__dict__, 200
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500
