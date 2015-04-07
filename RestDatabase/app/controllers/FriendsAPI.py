from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
from flask.ext.socketio import emit
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from sqlalchemy import func,or_, and_, not_
from datetime import date

from app import db, api, socketio
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
        
        #Ensure user is authorized
        user = User.query.filter(User.fitpals_secret==args.Authorization).first()
        if not user:
            return Response(status=401, message="Not Authorized.").__dict__,401
            
        return Response(status=200, message="Friends found.",
                        value=[f.dict_repr() for f in user.friends]).__dict__,200
        
    def post(self):
        """
        Add friend to friends list.

        :reqheader Authorization: facebook secret
        
        :form int user_id: Id of user creating friend.
        :form int friend_user_id: Id of user to be friend.
        
        :status 401: Not Authorized.
        :status 404: User not found.
        :status 500: Internal error. Changes not committed.
        :status 201: Friends added.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        parser.add_argument("user_id",
            type=int, location="form", required=True)
        parser.add_argument("friend_user_id",
            type=int, location="form", required=True)
        args = parser.parse_args()
        
        #get user from db
        user = User.query.get(args.user_id)
        if not user:
            return Response(status=404, message="User not found.").__dict__,404
            
        #ensure user is authorized
        if not user.fitpals_secret == args.Authorization:
            return Response(status=401, message="Not Authorized.").__dict__,401
            
        #get friend user from db
        friend_user = User.query.get(args.friend_user_id)
        if not friend_user:
            return Response(status=404, message="User not found.").__dict__,404
            
        #add friend to user.friends
        try:
            new_friend = Friend(user,friend_user)
            user.friends.append(new_friend)
            db.session.commit()
        except:
            db.session.rollback()
            return Response(status=500,
                message="Internal error. Changes not committed").__dict__,500
            
        return Response(status=201, message="Friend added.",
                        value=new_friend.dict_repr()).__dict__, 201
        
@api.resource("/friends/<int:friend_id>")
class FriendAPI(Resource):
    def delete(self, friend_id):
        """
        Delete a friend.

        :reqheader Authorization: facebook secret
        
        :param int friend_id: Id of friend to delete.
        
        :status 401: Not Authorized.
        :status 404: Friend not found.
        :status 500: Internal error. Changes not committed.
        :status 200: Friend deleted.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()
        
        #Get user from Authorization
        user = User.query.filter(User.fitpals_secret==args.Authorization).first()
        if not user:
            return Response(status=401, message="Not Authorized.").__dict__,401

        #get friend user from db
        friend = Friend.query.get(friend_id)
        if not friend:
            return Response(status=404, message="Friend not found.").__dict__,404
            
        #delete friend from db
        try:
            user.friends.remove(friend)
            db.session.delete(friend)
            db.session.commit()
        except:
            db.session.rollback()
            return Response(status=500,
                message="Internal error. Changes not committed").__dict__,500
            
        return Response(status=200, message="Friend deleted.").__dict__,200
