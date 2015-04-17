from flask import Flask, request
from flask.ext.restful import Resource, reqparse, Api
from flask.ext.socketio import emit
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from sqlalchemy import func,or_, and_, not_
from datetime import date

from app import db, api, app, exception_is_validation_error
from app.models import *
from app.utils.Response import Response
from app.utils import Facebook
from app.utils.AsyncNotifications import send_message

@api.resource("/facebook_friends")
class FacebookFriendsAPI(Resource):
    def get(self):
        """
        Gets a user's(specified by Authorization) facebook friends(As User objects).
        
        :reqheader Authorization: fitpals secret
        
        :status 401: Not Authorized.
        :status 200: Friends found.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()

        try:
            user = User.query.filter(User.fitpals_secret==args.Authorization).first()
            if not user:
                return Response(status=401,message="Not Authorized.").__dict__,401

            friend_fb_ids = Facebook.get_user_friends(user.fb_id)

            if not friend_fb_ids:
                return Response(status=200,message="Friends found.",
                                value=[]).__dict__,200
            or_expr = or_(User.fb_id==friend_fb_ids[0])
            for f in friend_fb_ids[1:]: or_expr = or_(or_expr,User.fb_id==f)
            users = User.query.filter(or_expr).all()
            users = [u.dict_repr(show_online_status=True) for u in users]
            return Response(status=200,message="Friends found.",
                            value=users).__dict__,200
        except Exception as e:
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500

