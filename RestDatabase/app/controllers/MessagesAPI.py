from flask.ext.restful import Resource, reqparse, Api

from app import db, api
from app.models import *
from app.utils.Response import Response
from sqlalchemy import or_

@api.resource("/messages")
class NewMessagesAPI(Resource):
    def get(self):
        """
        Get owner's messages with other user
        
        :reqheader Authorization: fb_id token needed here

        :param int message_thread_id: Id of specific thread to get messages from.
        :param int since: Optional time to get messages 'since' then.

        :status 400: Message thread <message_thread_id> not found.
        :status 401: Not Authorized.
        :status 200: Messages found.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        parser.add_argument("message_thread_id",
            type=int, location="args", required=True)
        parser.add_argument("since",
            type=int, location="args", required=False)
        args = parser.parse_args()

        #get user from Authorization
        user = User.query.filter(User.fb_id==args.Authorization).first()
        if not user:
            return Response(status=400, message="Invalid Authorization Token.")\
                .__dict__, 400
        
        #get thread from database
        thread = MessageThread.query.get(message_thread_id)
        if not thread or\
           (thread.user1==user and thread.user1.deleted==true) or\
           (thread.user2==user and thread.user2.deleted==true):
            return Response(status=400,
                message="Message thread %d not found." % args.thread_id)\
                .__dict__, 400

        #ensure user is authorized to read thread
        if thread.user1 != user and thread.user2 != user:
            return Response(status=401,message="Not Authorized.").__dict__,401
            
        if args.since != None:
            messages = thread.messages.filter(Message.time>=args.since).all()
        else: messages = thread.messages.all()
            
        #return thread
        return Response(status=200, message="Messages found.",
                        value=[m.dict_repr() for m in messages]), 200

    #create new message
    def post(self):
        """
        Post new message to thread
        
        :reqheader Authorization: fb_id token needed here

        :form int message_thread_id: Id of specific thread to get messages from.
        :form str body: Message body
        :form bool direction: direction that message goes between users 1 and 
                              2 in a thread. False:1->2, True:2->1

        :status 400: Invalid Authorization Token.
        :status 400: Message thread <message_thread_id> not found.
        :status 400: Message thread has been closed.
        :status 401: Not Authorized.
        :status 201: Message created.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        parser.add_argument("direction",
            type=bool, location="form", required=True)
        parser.add_argument("body",
            type=str, location="form", required=True)
        parser.add_argument("message_thread_id",
            type=int, location="form", required=True)
        args = parser.parse_args()

        #get user from Authorization
        user = User.query.filter(User.fb_id==args.Authorization).first()
        if not user:
            return Response(status=400, message="Invalid Authorization Token.")\
                .__dict__, 400
        
        #get thread from message_thread_id
        thread = MessageThread.query.get(args.message_thread_id)
        if not thread:
            return Response(status=400,
                message="Message thread %d not found." % args.thread_id)\
                .__dict__, 400

        #ensure that user is authorized to add the message to the thread
        if not ((user == thread.user1 and args.direction==0) or\
           (user == thread.user2 and args.direction==1)):
            return Response(status=401,message="Not Authorized.").__dict__,401
            
        #Don't allow a user to send messages to a thread deleted by another user
        if thread.user1_deleted or thread.user2_delete:
            return Response(status=400,
                message="Message thread has been closed.").__dict__, 400

        #add message to thread
        new_message = Message(thread, args.direction, args.body)
        thread.messages.append(new_message)
        db.session.commit()
        
        #send update over websocket
        socketio.emit("message_received", new_message.dict_repr(),
                      room=str(thread.user1.id) + "-chat")
        socketio.emit("message_received", new_message.dict_repr(),
                      room=str(thread.user2.id) + "-chat")
        
        #return success
        return Response(status=201,
            message="Message created.").__dict__, 201
        
@api.resource("/message_threads")
class MessageThreadsAPI(Resource):
    #return all message threads for a user
    def get(self):
        """
        Get all message threads for a specific user
        
        :reqheader Authorization: fb_id token needed here

        :status 200: Message threads found.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parse.parse_args()
        
        #get user from Authorization
        user = User.query.filter(User.fb_id==args.Authorization).first()
        if not user:
            return Response(status=400, message="Invalid Authorization Token.")\
                .__dict__, 400
        
        #This query will likely need a rewrite
        threads = MessageThread.query\
            .filter(
                or_expr(
                    and_expr(MessageThread.user1.fb_id==args.Authorization,
                             MessageThread.user1_deleted==False),
                    and_expr(MessageThread.user2.fb_id==args.Authorization,
                             MessageThread.user2_deleted==False))).all()
        
        return Response(status=200, message="Message threads found.",
                        value=[t.dict_repr() for t in threads]).__dict__,200
        
@api.resource("/message_threads/<int:thread_id>")
class MessageThreadAPI(Resource):
    #delete whole thread
    def delete(self, thread_id):
        """
        Delete a message thread
        
        :reqheader Authorization: fb_id token needed here

        :status 400: Invalid Authorization Token.
        :status 400: Message thread <message_thread_id> not found.
        :status 401: Not Authorized.
        :status 200: Message thread deleted.
        """

        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()

        #get user from Authorization
        user = User.query.filter(User.fb_id==args.Authorization).first()
        if not user:
            return Response(status=400, message="Invalid Authorization Token.")\
                .__dict__, 400

        #get thread from database
        thread = MessageThread.query.get(thread_id)
        if not thread:
            return Response(status=400,
                message="Message thread %d not found." % thread_id)\
                .__dict__, 400
            
        #delete thread for user if user is authorized
        if user == thread.user1:
            thread.user1_deleted = True
        elif user == thread.user2:
            thread.user2_deleted = True
        else:
            return Response(status=401,message="Not Authorized.").__dict__,401
            
        #if both user's have opt'ed to delete the thread, delete from db
        if thread.user1_deleted and thread.user2_deleted:
            thread.delete()
            
        #commit changes to the db
        db.session.commit()
        
        #push delete to user's other devices
        socketio.emit("message_thread_deleted",
                      room=str(thread.user.id) + "-chat")
        
        #return deletion success!
        return Response(status=200, message="Message thread deleted.")\
            .__dict__,200
