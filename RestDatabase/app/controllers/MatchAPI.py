from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from app import db, api, socketio
from app.models import *
from app.utils.Response import Response

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

        :reqheader Authorization: fb_id token needed here

        :query int user_id: User id for owner of matches.
        :query bool liked: If specified,
            returns matches that correspond with liked.

        :status 404: User not found.
        :status 200: Matches found.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("user_id",
            type=int, location="args", required=True)
        parser.add_argument("liked",
            type=bool, location="args", required=False)
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()

        #get user from the database
        user = User.query.get(args.user_id)
        if not user:
            return Response(status=404, message="User not found.").__dict__,404
            
        #ensure user is authorized
        if user.fb_id != args.Authorization:
            return Response(status=401,
                message="Not Authorized.").__dict__, 401

        #apply liked filter if specified
        query = user.matches
        if args.liked != None:
            query = query.filter(Match.liked==args.liked)

        return Response(status=200, message="Matches found.",
            value=[m.dict_repr() for m in query.all()]).__dict__,200

    def post(self):
        """
        :reqheader Authorization: fb_id token needed here

        :form int user_id: User id for owner of matches.
        :form int matched_user_id: User id for matched user.
        :form bool liked: If specified,
            returns matches that correspond with liked.

        :status 400: Could not create match.
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
            type=bool, location="form", required=True)
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()

        #get users from database
        user = User.query.get(args.user_id)
        if not user:
            return Response(status=404, message="User not found.").__dict__,404
        match_user = User.query.get(args.match_user_id)
        if not match_user:
            return Response(status=404, message="Matched user not found.")\
                .__dict__,404

        #ensure user is authorized
        if user.fb_id != args.Authorization:
            return Response(status=401,
                message="Not Authorized.").__dict__, 401

        #add match to user's matches
        try:
            match = Match(user, match_user, args.liked)
            user.matches.append(match)
            db.session.commit()
        except:
            db.session.rollback()
            return Response(status=400, message="Could not create match.")\
                .__dict__, 400
            
        
        #send websocket update if match_user has also liked user
        mutual_match = match_user.matches.filter(Match.matched_user_id==user.id).first()
        if mutual_match:
            socketio.emit("mutual_match_added",mutual_match.dict_repr(),
                        room=str(user.id))
            socketio.emit("mutual_match_added",mutual_match.dict_repr(),
                        room=str(match_user.id))
        else:
            #send websocket update
            socketio.emit("match_added",match.dict_repr(),
                        room=str(user.id))

        return Response(status=201,message="Match created.",
                        value=match.dict_repr()).__dict__,201

@api.resource("/matches/<int:match_id>")
class MatchAPI(Resource):
    def delete(self, match_id):
        """
        :reqheader Authorization: fb_id token needed here

        :param int match_id: Id for specific match.

        :status 400: Match could not be deleted.
        :status 401: Not Authorized.
        :status 404: Match not found.
        :status 200: Match deleted.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()
        
        match = Match.query.get(match_id)
        if not match:
            return Response(status=404, message="Match not found.").__dict__,404
        user = match.user

        #ensure user is authorized
        if user.fb_id != args.Authorization:
            return Response(status=401,
                message="Not Authorized.").__dict__, 401

        #delete all match decisions
        try:
            user.matches.remove(match)
            db.session.commit()
        except:
            db.session.rollback()
            return Response(status=400,message="Match could not be deleted.")\
                .__dict__,400

        #send websocket update
        socketio.emit("match_deleted",match_id,
                      room=str(user.id))

        return Response(status=200,message="Match deleted.").__dict__, 200
