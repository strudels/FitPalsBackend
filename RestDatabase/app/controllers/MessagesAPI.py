from flask.ext.restful import Resource, reqparse, Api

from app import db, api
from app.models import *
from app.utils.Response import Response

@api.resource("/users/<int:owner_id>/messages/<int:other_id>")
class MessagesAPI(Resource):
    def get(self, owner_id, other_id):
        """
        Get owner's messages with other user

        :param int owner_id: User id for owner.
        :param int other_id: User id for other user.

        :status 400: User not found.
        :status 500: Message lookup failed.
        :status 200: Messages found.
        """

        #get owner user
        owner = User.query.filter(User.id==owner_id).first()
        if not owner:
            return Response(status=400,
                message="User %d not found" % owner_id).__dict__, 400

        #get other user
        other_user = User.query.filter(User.id==other_id).first()
        if not other_user:
            return Response(status=400,
                message="User %d not found" % other_id).__dict__, 400

        #get owner's messages from other user
        try: messages = owner.get_messages(other_user)
        except:
            return Response(status=500,
                message="Message lookup failed.").__dict__, 500

        #return the messages
        return Response(status=200,message="Messages found.",
            value={"messages":messages}).__dict__, 200
        
    def delete(self, owner_id, other_id):
        """
        Delete owner's messages with other user

        :param int owner_id: User id for owner.
        :param int other_id: User id for other user.

        :status 400: User not found.
        :status 500: Messages not deleted.
        :status 200: Messages deleted.
        """

        #get owner user
        owner = User.query.filter(User.id==owner_id).first()
        if not owner:
            return Response(status=400,
                message="User %d not found" % owner_id).__dict__, 400

        #get other user
        other_user = User.query.filter(User.id==other_id).first()
        if not other_user:
            return Response(status=400,
                message="User %d not found" % other_id).__dict__, 400

        #delete user's messages to and from other user
        try: owner.del_messages(other_user)
        except: return Response(status=500,
            message="Messages not deleted.").__dict__, 500

        #return success
        return Response(status=200,message="Messages deleted.").__dict__, 200
