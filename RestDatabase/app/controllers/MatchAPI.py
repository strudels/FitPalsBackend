from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from app import db, api
from app.models import *
from app.utils.Response import Response

@api.resource('/users/<int:user_id>/matches')
class UserMatchAPI(Resource):
    """
    #sends apple push notification
    def _send_apn(self, device_token, data_dict):
        notify("uhsome.Fitpals", device_token, {"aps":data_dict})
    """

    def get(self, user_id):
        """
        :param int user_id: User id for owner of matches.

        :query bool liked: If specified,
            returns matches that correspond with liked.

        :status 400: User not found.
        :status 200: Matches retrieved.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("liked",
            type=bool, location="args", required=False)
        args = parser.parse_args()

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
        """
        :reqheader Authorization: fb_id token needed here
        :param int user_id: User id for owner of matches.

        :form int match_id: User id for match.
        :form bool liked: If specified,
            returns matches that correspond with liked.

        :status 400: "User not found" or "Match not found".
        :status 200: Match posted.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("match_id",
            type=int, location="form", required=True)
        parser.add_argument("liked",
            type=bool, location="form", required=True)
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()

        #get users from database
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400, message="User not found.").__dict__,400
        match_user = User.query.filter(User.id==args.match_id).first()
        if not match_user:
            return Response(status=400, message="Match not found.").__dict__,400

        #ensure user is authorized
        if user.fb_id != args.Authorization:
            return Response(status=401,
                message="Not Authorized.").__dict__, 401

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

        return Response(status=201,message="User updated").__dict__,201

    def delete(self, user_id):
        """
        :reqheader Authorization: fb_id token needed here
        :param int user_id: User id for owner of matches.

        :form int match_id: User id for match.

        :status 400: User not found.
        :status 200: User match decisions deleted.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("match_id",
            type=int, location="form", required=False)
        parser.add_argument("fb_id",
            type=str, location="form", required=True)
        args = parser.parse_args()

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
