from flask.ext.restful import Resource, reqparse, Api
from flask import request

from app import db, api, app, exception_is_validation_error
from app.models import *
from app.utils.Response import Response
from app.utils.AsyncNotifications import send_message
from sqlalchemy import or_, and_

@api.resource("/user_blocks")
class NewUserBlocksAPI(Resource):
    def get(self):
        """
        Get a user's UserBlocks.
        
        :reqheader Authorization: fitpals_secret

        :query int message_thread_id: Id of specific thread to get messages from(Optional).
        :query int since: Optional time to get messages 'since' then(epoch).

        :status 401: Not Authorized.
        :status 200: User blocks found.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()
        
        try:
            user = User.query.filter(User.fitpals_secret==args.Authorization).first()
            if not user:
                return Response(status=401,message="Not Authorized.").__dict__,401

            blocks = user.blocks.all()
            return Response(status=200,message="User blocks found.",
                            value=[b.dict_repr() for b in blocks])
        except Exception as e:
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500
        
    def post(self):
        """
        Post a new UserBlock.
        
        :reqheader Authorization: fitpals_secret

        :form int blocked_user_id: ID of user to be blocked.

        :status 401: Not Authorized.
        :status 404: User not found.
        :status 201: User block created.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        parser.add_argument("blocked_user_id",
            type=int, location="headers", required=True)
        args = parser.parse_args()

        try:
            user = User.query.filter(User.fitpals_secret==args.Authorization).first()
            if not user:
                return Response(status=401,message="Not Authorized.").__dict__,401

            blocked_user = User.query.get(args.blocked_user_id)
            if not blocked_user:
                return Response(status=404,message="User not found.").__dict__,404

            block = UserBlock(user,blocked_user)
            db.session.add(block)
            db.session.commit()

            return Response(status=201,message="User block created.").__dict__,201
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500

@api.resource("/user_blocks/<int:block_id>")
class NewUserBlocksAPI(Resource):
    def delete(self,block_id):
        """
        Remove a UserBlock.
        
        :reqheader Authorization: fitpals_secret

        :param int block_id: ID of UserBlock.

        :status 401: Not Authorized.
        :status 404: User block not found.
        :status 200: User block removed.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()

        try:
            user = User.query.filter(User.fitpals_secret==args.Authorization).first()
            if not user:
                return Response(status=401,message="Not Authorized.").__dict__,401
                
            block = UserBlock.query.get(block_id)
            if not block:
                return Response(status=404,message="User block not found.")\
                    .__dict__,404
                
            if block.user_id != user.id:
                return Response(status=401,message="Not Authorized.").__dict__,401
                
            block.unblock_time = db.func.now()
            db.session.commit()
            
            return Response(status=200,message="User block removed.",
                            value=block.dict_repr()).__dict__,200
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500
