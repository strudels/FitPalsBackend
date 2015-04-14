from flask.ext.restful import Resource, reqparse, Api
from flask import request

from app import db, api, app, exception_is_validation_error
from app.models import *
from app.utils.Response import Response
from app.utils.AsyncNotifications import send_message
from sqlalchemy import or_, and_
from datetime import datetime

@api.resource("/messages")
class NewMessagesAPI(Resource):
    def get(self):
        """
        Get owner's messages from a thread
        
        :reqheader Authorization: facebook secret

        :query int message_thread_id: Id of specific thread to get messages from(Optional).
        :query int since: Optional time to get messages 'since' then(epoch).

        :status 401: Not Authorized.
        :status 404: Message thread not found.
        :status 200: Messages found.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        parser.add_argument("message_thread_id",
            type=int, location="args", required=False)
        parser.add_argument("since",
            type=int, location="args", required=False)
        args = parser.parse_args()

        try:
            #get user from Authorization
            user = User.query.filter(User.fitpals_secret==args.Authorization).first()
            if not user:
                return Response(status=401, message="Not Authorized.")\
                    .__dict__, 401

            #get thread from database
            if args.message_thread_id:
                thread = MessageThread.query.get(args.message_thread_id)
                if not thread:
                    return Response(status=404,
                        message="Message thread not found.")\
                        .__dict__, 404

                #ensure user is authorized to read thread
                if thread.user1 != user and thread.user2 != user:
                    return Response(status=401,message="Not Authorized.").__dict__,401
                messages_query = thread.messages.join(Message.message_thread)
            else:
                messages_query = Message.query.join(Message.message_thread)\
                                 .filter(or_(MessageThread.user1_id==user.id,
                                             MessageThread.user2_id==user.id))

            if args.since != None:
                messages_query = messages_query.filter(Message.time>=\
                    datetime.utcfromtimestamp(args.since))
                
            #filter out messages that were deleted via DELETE /message_threads/<id>
            messages_query = messages_query.filter(
                or_(
                    and_(MessageThread.user1==user,
                            or_(MessageThread.user1_delete_time==None,
                                MessageThread.user1_delete_time<=Message.time
                            )
                    ),
                    and_(MessageThread.user2==user,
                            or_(MessageThread.user2_delete_time==None,
                                MessageThread.user2_delete_time<=Message.time
                            )
                    )
                )
            )
                
            #filter out messages received from a user while they were blocked
            sub_query = UserBlock.query.filter(
                and_(
                    UserBlock.user_id==user.id,
                    UserBlock.block_time<=db.func.now(),
                    or_(
                        UserBlock.unblock_time==None,
                        UserBlock.unblock_time>=db.func.now()
                    )
                )
            ).with_entities(UserBlock.blocked_user_id)
            messages_query = messages_query.filter(
                or_(
                    and_(
                        MessageThread.user1_id==user.id,
                        ~MessageThread.user2_id.in_(sub_query),
                        Message.direction==True,
                    ), and_(
                        MessageThread.user2_id==user.id,
                        ~MessageThread.user1_id.in_(sub_query),
                        Message.direction==False
                    ), and_(MessageThread.user1_id==user.id,
                            Message.direction==False
                    ), and_(MessageThread.user2_id==user.id,
                            Message.direction==True
                    )
                )
            )

            messages = messages_query.all()

            #return thread
            return Response(status=200, message="Messages found.",
                            value=[m.dict_repr() for m in messages]).__dict__, 200
        except Exception as e:
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500

    #create new message
    def post(self):
        """
        Post new message to thread
        
        :reqheader Authorization: facebook secret

        :form int message_thread_id: Id of specific thread to get messages from.
        :form str body: Message body
        :form int direction: direction that message goes between users 1 and 
                              2 in a thread. Set to 0 for user1->user2; Set
                              to 1 for user2->user1. Note: direction's type 
                              in the model is actually boolean, where 0->False
                              and 1->True.

        :status 400: Message data invalid.
        :status 401: Not Authorized.
        :status 403: Message thread has been closed.
        :status 404: Message thread not found.
        :status 201: Message created.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        parser.add_argument("direction",
            type=int, location="form", required=True)
        parser.add_argument("body",
            type=str, location="form", required=True)
        parser.add_argument("message_thread_id",
            type=int, location="form", required=True)
        args = parser.parse_args()

        try:
            #get user from Authorization
            user = User.query.filter(User.fitpals_secret==args.Authorization).first()
            if not user:
                return Response(status=401, message="Not Authorized.")\
                    .__dict__, 401

            #get thread from message_thread_id
            thread = MessageThread.query.get(args.message_thread_id)
            if not thread:
                return Response(status=404,
                    message="Message thread not found.").__dict__, 404

            #ensure that user is authorized to add the message to the thread
            if not ((user == thread.user1 and args.direction==0) or\
            (user == thread.user2 and args.direction==1)):
                return Response(status=401,message="Not Authorized.").__dict__,401

            #add message to thread
            new_message = Message(thread, bool(args.direction), args.body)
            thread.messages.append(new_message)

            #commit changes to the db
            db.session.commit()

            #determine if user sending message has been blocked by receiver
            if user == thread.user1:
                is_blocked = thread.user2.blocks\
                              .filter(and_(UserBlock.blocked_user_id==user.id,
                                           UserBlock.unblock_time==None)).first()
            elif user == thread.user2:
                is_blocked = thread.user1.blocks\
                              .filter(and_(UserBlock.blocked_user_id==user.id,
                                           UserBlock.unblock_time==None)).first()
                
            #send sync update
            send_message(thread.user1 if user==thread.user1 else thread.user2,
                        request.path,request.method,
                        value=new_message.dict_repr())

            #ensure that if user has been blocked, the new message won't be sent
            #to the intended user
            if not is_blocked:
                send_message(thread.user2 if user==thread.user1 else thread.user1,
                            request.path,request.method,
                            value=new_message.dict_repr(),apn_send=True)

            #return success
            return Response(status=201,message="Message created.",
                            value=new_message.dict_repr()).__dict__, 201
        except Exception as e:
            if exception_is_validation_error(e):
                return Response(status=400,
                    message="Message data invalid.").__dict__,400
            db.session.rollback()
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500
        
@api.resource("/message_threads")
class MessageThreadsAPI(Resource):
    #return all message threads for a user
    def get(self):
        """
        Get all message threads for a user, specified by Authorization
        
        :reqheader Authorization: facebook secret

        :status 401: Not Authorized.
        :status 200: Message threads found.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()
        
        try:
            #get user from Authorization
            user = User.query.filter(User.fitpals_secret==args.Authorization).first()
            if not user:
                return Response(status=401, message="Not Authorized.")\
                    .__dict__, 401

            #get threads for user that are either empty, or have any messages
            # that have not been deleted
            threads = MessageThread.query
                .filter(
                    or_(
                        and_(MessageThread.user1==user,
                             or_(MessageThread.user1_delete_time==None,
                                 MessageThread.messages.join(Message.message_thread).filter(
                                     MessageThread.user1_delete_time<=Message.time
                                 ).any()
                             )
                        ),
                        and_(MessageThread.user2==user,
                             or_(MessageThread.user2_delete_time==None,
                                 MessageThread.messages.join(Message.message_thread).filter(
                                     MessageThread.user2_delete_time<=Message.time
                                 ).any()
                             )
                        )
                    )
                ).all()

            return Response(status=200, message="Message threads found.",
                            value=[t.dict_repr() for t in threads]).__dict__,200
        except Exception as e:
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500
    
    #create new message thread
    def post(self):
        """
        Create new message thread between 2 users.
        
        :reqheader Authorization: fitpals_secret
        
        :form int user2_id: Id of user2 for new message thread.
        
        :status 400: Message thread data invalid.
        :status 401: Not Authorized.
        :status 403: Blocked from creating message thread.
        :status 404: user2_id not found.
        :status 201: Message thread created.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        parser.add_argument("user2_id",
            type=int, location="form", required=True)
        args = parser.parse_args()
        
        try:
            #get user from Authorization
            user1 = User.query.filter(User.fitpals_secret==args.Authorization).first()
            if not user1:
                return Response(status=401, message="Not Authorized.")\
                    .__dict__, 401

            #get user 2
            user2 = User.query.get(args.user2_id)
            if not user2:
                return Response(status=404,
                                message="user2_id not found.").__dict__,404

            #determine if another thread already exists between the 2 users
            thread = MessageThread.query.filter(
                or_(
                    and_(MessageThread.user1==user2,
                         MessageThread.user2==user1),
                    and_(MessageThread.user2==user2,
                         MessageThread.user1==user1)
                )
            ).first()

            if not thread:
                thread = MessageThread(user1, user2)
                db.session.add(new_thread)
                db.session.commit()
                send_message(thread.user1,request.path,request.method,
                            value=thread.dict_repr())
                send_message(thread.user2,request.path,request.method,
                            value=thread.dict_repr())
                
            else: #only send_message to user making request
                send_message(user,request.path,request.method,
                             value=thread.dict_repr()

            #return create success!
            return Response(status=201, message="Message thread created.",
                            value=new_thread.dict_repr()).__dict__,201
        except Exception as e:
            if exception_is_validation_error(e):
                return Response(status=400,
                    message="Message thread data invalid.").__dict__,400
            db.session.rollback()
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500
        
@api.resource("/message_threads/<int:thread_id>")
class MessageThreadAPI(Resource):
    #delete whole thread
    def delete(self, thread_id):
        """
        Delete a message thread
        
        :reqheader Authorization: facebook secret

        :status 401: Not Authorized.
        :status 404: Message thread not found.
        :status 500: Internal Error. Changes not committed.
        :status 200: Message thread deleted.
        """

        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()

        try:
            #get user from Authorization
            user = User.query.filter(User.fitpals_secret==args.Authorization).first()
            if not user:
                return Response(status=401, message="Not Authorized.")\
                    .__dict__, 401

            #get thread from database
            thread = MessageThread.query.get(thread_id)
            if not thread:
                return Response(status=404,
                    message="Message thread not found.")\
                    .__dict__, 404

            #delete thread for user if user is authorized
            if user == thread.user1:
                thread.user1_delete_time = datetime.utcnow()
            elif user == thread.user2:
                thread.user2_delete_time = datetime.utcnow()
            else:
                return Response(status=401,message="Not Authorized.").__dict__,401

            #commit changes to the db
            db.session.commit()

            #push delete to user's other devices
            send_message(thread.user1 if user==thread.user1 else thread.user2,
                         request.path,request.method)

            #return deletion success!
            return Response(status=200, message="Message thread deleted.")\
                .__dict__,200
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500
