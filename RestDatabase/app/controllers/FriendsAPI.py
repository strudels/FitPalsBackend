from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from sqlalchemy import func,or_, and_, not_
from datetime import date
from sqlalchemy import and_

from app import db, api, app, exception_is_validation_error
from app.models import *
from app.utils.Response import Response

@api.resource("/friends")
class FriendsAPI(Resource):
    def get(self):
        """
        Get friends for a user specified by Authorization.
        
        :reqheader Authorization: facebook secret
        
        :status 200: Friends found.
        :status 401: Not Authorized.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()
        
        try:
            #Ensure user is authorized
            user = User.query.filter(User.fitpals_secret==args.Authorization).first()
            if not user:
                return Response(status=401, message="Not Authorized.").__dict__,401

            return Response(status=200, message="Friends found.",
                            value=[f.friend_user.dict_repr(show_online_status=True)\
                                for f in user.friends]).__dict__,200
        except Exception as e:
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500
        
    def post(self):
        """
        Add friend to friends list.

        :reqheader Authorization: facebook secret
        
        :form int id: Id of user to be added to friends list.
        
        :status 400: Friend data invalid.
        :status 401: Not Authorized.
        :status 404: User not found.
        :status 201: Friend added.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        parser.add_argument("id",
            type=int, location="form", required=True)
        args = parser.parse_args()

        try:
            #ensure user is authorized
            user = User.query.filter(User.fitpals_secret==args.Authorization).first()
            if not user:
                return Response(status=401, message="Not Authorized.").__dict__,401

            #get friend user from db
            friend_user = User.query.get(args.id)
            if not friend_user:
                return Response(status=404, message="User not found.").__dict__,404

            #add friend to user.friends
            new_friend = Friend(user,friend_user)
            user.friends.append(new_friend)
            db.session.commit()

            return Response(status=201, message="Friend added.",
                            value=new_friend.friend_user\
                            .dict_repr(show_online_status=True)).__dict__, 201
        except Exception as e:
            if exception_is_validation_error(e):
                return Response(status=400,
                    message="Friend data invalid.").__dict__,400
            db.session.rollback()
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500
        
@api.resource("/friends/<int:friend_id>")
class FriendAPI(Resource):
    def delete(self, friend_id):
        """
        Delete a friend.

        :reqheader Authorization: facebook secret
        
        :param int friend_id: User Id of friend to delete.
        
        :status 401: Not Authorized.
        :status 404: Friend not found.
        :status 500: Internal error. Changes not committed.
        :status 200: Friend deleted.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()
        
        try:
            #Get user from Authorization
            user = User.query.filter(User.fitpals_secret==args.Authorization).first()
            if not user:
                return Response(status=401, message="Not Authorized.").__dict__,401

            #get friend user from db
            #friend = Friend.query.get(friend_id)
            friend_user = User.query.get(friend_id)
            if not friend_user:
                return Response(status=404, message="Friend not found.").__dict__,404

            friend = Friend.query.filter(and_(Friend.user==user,
                                            Friend.friend_user==friend_user))\
                                .first()
            if not friend:
                return Response(status=404, message="Friend not found.").__dict__,404

            #delete friend from db
            user.friends.remove(friend)
            db.session.delete(friend)
            db.session.commit()

            return Response(status=200, message="Friend deleted.").__dict__,200
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500
