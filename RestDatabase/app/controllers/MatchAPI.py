from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from app import db, api
from app.models import *
from app.utils.Response import Response

@api.resource('/users/<user_id>/matches')
class UserMatchAPI(Resource):
    """
    #sends apple push notification
    def _send_apn(self, device_token, data_dict):
        notify("uhsome.Fitpals", device_token, {"aps":data_dict})
    """

    def get(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("liked",
            type=bool, location="args", required=False)
        args = parser.parse_args()

        #cast user_id to int
        try: user_id = int(user_id)
        except:
            return Response(status=400,message="Invalid user id.").__dict__,400

        #get user from the database
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400, message="User not found.").__dict__,400

        query = user.match_decisions
        if args.liked != None:
            query = query.filter(MatchDecision.liked==args.liked)

        return Response(status=200, message="Matches retrieved.",
            value=[m.dict_repr() for m in query.all()]).__dict__,200

    def post(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("match_id",
            type=int, location="form", required=True)
        parser.add_argument("liked",
            type=bool, location="form", required=True)
        parser.add_argument("fb_id",
            type=str, location="form", required=True)
        args = parser.parse_args()

        #cast user_id to int
        try: user_id = int(user_id)
        except:
            return Response(status=400,message="Invalid user id.").__dict__,400

        #get users from database
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400, message="User not found.").__dict__,400
        match_user = User.query.filter(User.id==args.match_id).first()
        if not match_user:
            return Response(status=400, message="Match not found.").__dict__,400

        #ensure user is authorized
        if user.fb_id != args.fb_id:
            return Response(status=401,
                message="Incorrect fb_id.").__dict__, 401

        #add match to user's matches
        match = MatchDecision(user, match_user, args.liked)
        user.match_decisions.append(match)
        db.session.commit()

        """
        #send push notification to both users that match was found
        matches_other_user = match_user.match_decisions\
            .filter(MatchDecision.decision_user_id==user_id)
            .filter(MatchDecision.liked==True).first()
        if args.approved and matches_other_user:
            for token in user["apn_tokens"]: self._send_apn(token, {"alert":"Match!"})
            for token in match["apn_tokens"]: self._send_apn(token, {"alert":"Match!"})
        """

        return Response(status=202,message="User updated").__dict__,202

    def delete(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("match_id",
            type=int, location="form", required=False)
        parser.add_argument("fb_id",
            type=str, location="form", required=True)
        args = parser.parse_args()

        #cast user_id to int
        try: user_id = int(user_id)
        except:
            return Response(status=400,message="Invalid user id.").__dict__,400

        #get users from database
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400, message="User not found.").__dict__,400

        #ensure user is authorized
        if user.fb_id != args.fb_id:
            return Response(status=401,
                message="Incorrect fb_id.").__dict__, 401

        #delete all match decisions
        user.match_decisions = []
        db.session.commit()
        return Response(status=200,message="User match decisions deleted.")\
            .__dict__, 200
