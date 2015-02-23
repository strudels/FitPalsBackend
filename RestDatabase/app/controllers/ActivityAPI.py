from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from app import db, api
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

@api.resource('/users/<int:user_id>/activity_settings')
class UserActivitySettingsAPI(Resource):
    #get's all activities for a specific user
    def get(self, user_id):
        """
        Get all activity settings for a user

        :param int user_id: User to get activity settings for

        :status 400: User not found.
        :status 200: Activity settings found.
        """

        #get user via user_id
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400,message="User not found.").__dict__,400

        return Response(status=200, message="Activity settings found.",
            value=[a.dict_repr() for a in user.activity_settings]).__dict__,200

    #add activity to user's activity list
    def post(self, user_id):
        """
        Post new activity setting for user

        :reqheader Authorization: fb_id token needed here
        :param int user_id: Id of user.

        :form int activity_id: Id of activity.
        :form int-list question_ids: List of question_ids, must zip with answers
        :form float-list answers: List of answers, must zip with question_ids

        :status 401: Not Authorized.
        :status 400: "Inequal numbers of questions and answers" or
            "Activity not found" or "Activity question not found".
        :status 202: Activity setting created.
        """

        parser = reqparse.RequestParser()
        parser.add_argument("fb_id",
            type=str, location='form', required=True)
        parser.add_argument("activity_id",
            type=int,location="form", required=True)
        parser.add_argument("question_ids",
            type=int,location="form", required=True, action="append")
        parser.add_argument("answers",
            type=float, location="form", required=True, action="append")
        args = parser.parse_args()

        #get user via user_id
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400,message="User not found.").__dict__,400

        #ensure user is valid by checking if fb_id is correct
        if user.fb_id != args.fb_id:
            return Response(status=401,message="Not Authorized.").__dict__,401

        #ensure questions and answers can be zipped
        if not len(args.question_ids)==len(args.answers):
            return Response(status=400,
                message="Inequal numbers of questions and answers.")\
                .__dict__,400

        #get activity via activity_id
        activity = Activity.query.filter(Activity.id==args.activity_id).first()
        if not activity:
            return Response(status=400,
                message="Activity not found.").__dict__,400

        #add activity_setting for each question-answer pair
        for q_id,answer in zip(args.question_ids, args.answers):
            try:
                question =\
                    activity.questions.filter(Question.id==q_id)[0]
            except:
                return Response(status=400,
                    message="Activity question not found.").__dict__, 400

            activity_setting =\
                ActivitySetting(user,activity,question,answer)
            user.activity_settings.append(activity_setting)
        db.session.commit()
        
        return Response(status=201,message="Activity setting created.").__dict__,201

    #delete all user's activities
    def delete(self, user_id):
        """
        Delete activity settings for user

        :reqheader Authorization: fb_id token needed here
        :param int user_id: Id of user.

        :status 401: Not Authorized.
        :status 400: User not found.
        :status 202: Activity settings created.
        """

        parser = reqparse.RequestParser()
        parser.add_argument("fb_id",
            type=str, location='form', required=True)
        args = parser.parse_args()

        #get user via user_id
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400,message="User not found.").__dict__,400

        #ensure user is valid by checking if fb_id is correct
        if user.fb_id != args.fb_id:
            return Response(status=401,message="Incorrect fb_id.").__dict__,401

        user.activity_settings.delete()
        db.session.commit()

        return Response(status=200,
            message="Activity settings deleted.").__dict__,200

#activity_id maps to an ActivitySetting id
@api.resource("/users/<int:user_id>/activity_settings/<int:activity_id>")
class UserActivitySettingAPI(Resource):
    #get settings for user's specific activity
    def get(self, user_id, activity_id):
        """
        Get user's activity settings for a specific activity

        :param int user_id: Id of user.
        :param int activity_id: Id of acitivity.

        :query int question_id: Id of question.

        :status 400: User not found.
        :status 202: Activity found.
        """

        parser = reqparse.RequestParser()
        parser.add_argument("question_id",
            type=int, location="args", required=False)
        args = parser.parse_args()

        #get user via user_id
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400,message="User not found.").__dict__,400

        #get user's activity_settings for specific activity_id
        query =\
            user.activity_settings\
                .filter(ActivitySetting.activity_id==activity_id)
        if args.question_id:
            query = query.filter(ActivitySetting.question_id==args.question_id)
        activity_settings = query.all()
        if not activity_settings: activity_settings = []

        return Response(status=200, message="Activity found.",
            value=[a.dict_repr() for a in activity_settings]).__dict__, 200

    #update user's specific activity
    def put(self, user_id, activity_id):
        """
        Update user's activity settings for a specific activity

        :reqheader Authorization: fb_id token needed here

        :param int user_id: Id of user.
        :param int activity_id: Id of acitivity.

        :form int-list question_ids: Ids of questions. Must zip with answers
        :form int-list answers: Answer to question. Must zip with question_ids

        :status 400: "User not found" or
            "Inequal amounts of questions and answers".
        :status 202: Activity setting updated.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("fb_id",
            type=str, location='form', required=True)
        parser.add_argument("question_ids",
            type=int,location="form",required=True,action="append",default=[])
        parser.add_argument("answers",
            type=float,location="form",required=True,action="append",default=[])
        args = parser.parse_args()

        #get user via user_id
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400,message="User not found.").__dict__,400

        #ensure questions and answers can be zipped together
        if not len(args.question_ids) == len(args.answers):
            return Response(status=400,
                message="Inequal amounts of questions and answers").__dict__,400

        for q_id, answer in zip(args.question_ids,args.answers):
            activity_setting = user.activity_settings\
                .filter(ActivitySetting.activity_id==activity_id)\
                .filter(ActivitySetting.question_id==q_id).first()
            if activity_setting != None:
                activity_setting.answer = answer
            else:
                activity = Activity.query.get(activity_id)
                question = activity.questions\
                .filter(Question.id==q_id).first()
                setting = ActivitySetting(user, activity, question)
                setting.answer = answer
                user.activity_settings.append(setting)
        db.session.commit()

        return Response(status=202,
            message="Activity setting updated.").__dict__,202

    #delete user's specific activity
    def delete(self, user_id, activity_id):
        """
        Delete user's activity settings for a specific activity

        :reqheader Authorization: fb_id token needed here

        :param int user_id: Id of user.
        :param int activity_id: Id of acitivity.

        :form int-list question_ids: Ids of questions.

        :status 400: User not found.
        :status 202: Activity setting deleted.
        """

        parser = reqparse.RequestParser()
        parser.add_argument("fb_id",
            type=str, location='form', required=True)
        parser.add_argument("question_ids",
            type=int,location="form",required=False,action="append",default=[])
        args = parser.parse_args()

        #get user via user_id
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400,message="User not found.").__dict__,400

        #delete specific questions if specified
        query = user.activity_settings\
            .filter(ActivitySetting.activity_id==activity_id)
        for q_id in args.question_ids:
            query = query.filter(ActivitySetting.question_id==q_id)
        for setting in query.all(): user.activity_settings.remove(setting)
        db.session.commit()
        return Response(status=200,
            message="Activity setting deleted.").__dict__, 200
