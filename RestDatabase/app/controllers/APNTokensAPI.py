from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from app import db, api
from app.models import *
from app.utils.Response import Response

@api.resource("/users/<user_id>/apn_tokens")
class APNTokensAPI(Resource):
    #add a device token for a user
    def post(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("token",
            type=str, location="form", required=True)
        args = parser.parse_args()

        #cast user_id to int type
        try: user_id = int(user_id)
        except: 
            return Response(status=400,message="Invalid user id.").__dict__,400

        #get user from database
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400,
                message="Could not find user.").__dict__,400

        token = APNToken(user, args.token)
        user.apn_tokens.append(token)
        db.session.commit()
        return Response(status=201, message="APN token stored.").__dict__,201

    #delete either a specific or all device tokens for a user
    def delete(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("token",
            type=str, location="form", required=False)
        args = parser.parse_args()

        #cast user_id to int type
        try: user_id = int(user_id)
        except: 
            return Response(status=400,message="Invalid user id.").__dict__,400

        #get user from database
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400,
                message="Could not find user.").__dict__,400

        #delete all tokens if no specific one is specified
        if not args.token:
            user.apn_tokens = []
            return Response(status=200,
                message="APN tokens deleted.").__dict__,200

        #get specific token to delete
        token = user.apn_tokens.filter(APNToken.token==args.token).first()
        if not token:
            return Response(status=400,
                message="APN token not found.").dict__,400

        #remove specific token
        user.apn_tokens.remove(token)
        db.session.commit()
