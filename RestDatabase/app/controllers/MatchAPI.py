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
    #sends apple push notification
    def _send_apn(self, device_token, data_dict):
        notify("uhsome.Fitpals", device_token, {"aps":data_dict})

    def post(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("match_id",
            type=str, location="form", required=True)
        parser.add_argument("approved",
            type=bool, location="form", required=False)
        parser.add_argument("fb_id",
            type=str, location="form", required=True)
        args = parser.parse_args()

        #get users from database
        user = database.get_user(user_id)
        match = database.get_user(args.match_id)

        #ensure user is authorized
        if user["fb_id"] != args.fb_id:
            return Response(status=401,
                message="Invalid fb_id").__dict__, 401

        #add match to user's matches
        if args.approved:
            user["approved_users"].append(args.match_id)
        else: user["denied_users"].append(args.match_id)
        try: update_status = database.update_user(user_id,user)
        except: return Response(status=400,
            message="Matches update failed.").__dict__, 400

        #ensure no error's from db
        if update_status["ok"]!=1:
            return Response(status=400,
            message="User update failed.").__dict__, 400

        #send push notification to both users that match was found
        if args.approved and user_id in match["approved_users"]:
            for token in user["apn_tokens"]: self._send_apn(token, {"alert":"Match!"})
            for token in match["apn_tokens"]: self._send_apn(token, {"alert":"Match!"})

        return Response(status=202,message="User updated").__dict__,202
