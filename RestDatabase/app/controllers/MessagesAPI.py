from flask.ext.restful import Resource, reqparse, Api

from app import db, api
from app.models import *
from app.utils.Response import Response

@api.resource("/users/<owner_id>/messages/<other_id>")
class MessagesAPI(Resource):
    def get(self, owner_id, other_id):
        #ensure user_id's are both ints
        try:
            owner_id = int(owner_id)
            other_id = int(other_id)
        except: return Response(status=400,
            message="Invalid user ids.").__dict__, 400

        #get owner user
        user = User.query.filter(User.id==owner_id).first()
        if not user:
            return Response(status=400,
                message="User %d not found" % owner_id).__dict__, 400

        #get owner's messages from other user
        try: messages = user.get_messages(other_id)
        except: return Response(status=500,
            message="Message lookup failed.").__dict__, 500

        #return the messages
        return Response(status=200,message="Messages found.",
            value={"messages":messages}).__dict__, 200
        
    def delete(self, owner_id, other_id):
        #ensure user_id's are both ints
        try:
            owner_id = int(owner_id)
            other_id = int(other_id)
        except: return Response(status=400,
            message="Invalid user ids.").__dict__, 400

        #get owner user
        user = User.query.filter(User.id==owner_id).first()
        if not user:
            return Response(status=400,
                message="User %d not found" % owner_id).__dict__, 400

        #delete user's messages to and from other user
        try: user.del_messages(other_id)
        except: return Response(status=500,
            message="Messages not deleted.").__dict__, 500

        #return success
        return Response(status=200,message="Messages deleted.").__dict__, 200
