from flask import Flask, request
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from sqlalchemy import and_

from app import db, api, app, exception_is_validation_error
from app.models import *
from app.utils.Response import Response
from app.utils.AsyncNotifications import send_message

@api.resource('/matches')
class MatchesAPI(Resource):
    """
    #sends apple push notification
    def _send_apn(self, device_token, data_dict):
        notify("uhsome.Fitpals", device_token, {"aps":data_dict})
    """

    def get(self):
        """
        Get matches for a user

        :reqheader Authorization: facebook secret

        :query int mutual: If specified, returns matches where other user has also
            matched with the querying user. Set to 0 for False, 1 for True.

        :status 401: Not Authorized.
        :status 200: Matches found.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("mutual",
            type=int, location="args", required=False)
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()

        try:
            #get user from the database
            user = User.query.filter(User.fitpals_secret==args.Authorization).first()
            if not user:
                return Response(status=401,
                    message="Not Authorized.").__dict__, 401

            query = user.matches
            #if args.mutual, get all user's matches where the matched_user
            #liked back
            if args.mutual == 1:
                mutual_match_users = Match.query.filter(and_(
                    Match.matched_user_id==user.id,
                    Match.liked==True)).with_entities(Match.user_id)
                query = query.filter(and_(Match.liked==True,
                    Match.matched_user_id.in_(mutual_match_users)))

            return Response(status=200, message="Matches found.",
                value=[m.dict_repr() for m in query.all()]).__dict__,200
        except Exception as e:
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500

    def post(self):
        """
        Create new match

        :reqheader Authorization: facebook secret

        :form int user_id: User id for owner of matches.
        :form int matched_user_id: User id for matched user.
        :form bool liked: If specified,
            sets new match liked. Set to 0 for False, 1 for True.

        :status 400: Match data invalid.
        :status 401: Not Authorized.
        :status 404: User not found.
        :status 404: Match user not found.
        :status 201: Match created.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("user_id",
            type=int, location="form", required=True)
        parser.add_argument("match_user_id",
            type=int, location="form", required=True)
        parser.add_argument("liked",
            type=int, location="form", required=True)
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()

        try:
            #get users from database
            user = User.query.get(args.user_id)
            if not user:
                return Response(status=404, message="User not found.").__dict__,404
            match_user = User.query.get(args.match_user_id)
            if not match_user:
                return Response(status=404, message="Match user not found.")\
                    .__dict__,404

            #ensure user is authorized
            if user.fitpals_secret != args.Authorization:
                return Response(status=401,
                    message="Not Authorized.").__dict__, 401

            #add match to user's matches
            match = Match(user, match_user, bool(args.liked))
            user.matches.append(match)
            db.session.commit()

            #send match to user's other devices
            send_message(user,request.path,request.method,
                         value=match.dict_repr())

            #if the person being matched with has also matched with the user, let the user know
            mutual_match = match_user.matches.filter(Match.matched_user_id==user.id).first()
            if mutual_match and match.liked and mutual_match.liked:
                send_message(user,request.path,request.method,
                             value=mutual_match.dict_repr(),apn_send=True)
                send_message(match_user,request.path,request.method,
                             value=match.dict_repr(),apn_send=True)

            return Response(status=201,message="Match created.",
                            value=match.dict_repr()).__dict__,201
        except Exception as e:
            if exception_is_validation_error(e):
                return Response(status=400,
                    message="Match data invalid.").__dict__,400
            db.session.rollback()
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500

@api.resource("/matches/<int:match_id>")
class MatchAPI(Resource):
    def delete(self, match_id):
        """
        Delete match

        :reqheader Authorization: facebook secret

        :param int match_id: Id for specific match.

        :status 401: Not Authorized.
        :status 404: Match not found.
        :status 200: Match deleted.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()
        
        try:
            match = Match.query.get(match_id)
            if not match:
                return Response(status=404, message="Match not found.").__dict__,404
            user = match.user

            #ensure user is authorized
            if user.fitpals_secret != args.Authorization:
                return Response(status=401,
                    message="Not Authorized.").__dict__, 401

            #delete all match decisions
            user.matches.remove(match)
            db.session.commit()

            #send websocket update
            send_message(user,request.path,request.method)

            return Response(status=200,message="Match deleted.").__dict__, 200
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500
