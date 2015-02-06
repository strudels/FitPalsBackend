from response import Response

from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from app import db, api
from app.models import *

@api.resource("/users/<owner_id>/messages/<other_id>")
class UserMessagesAPI(Resource):
    def get(self, owner_id, other_id):
        #get messages from database.py
        try: messages = database.get_messages(owner_id,other_id)
        except: return Response(status=500,
            message="Message lookup failed.").__dict__, 500
        return Response(status=200,message="Messages found.",
            value={"messages":messages}).__dict__, 200
        
    def delete(self, owner_id, other_id):
        #delete messages via database.py
        try: database.delete_messages(owner_id, other_id)
        except: return Response(status=500,
            message="Messages not deleted.").__dict__, 500
        return Response(status=200,message="Messages deleted.").__dict__, 200

if __name__=='__main__':
    app.run(host=config.get("api_server","bind_addr"),
        port=config.getint("api_server","port"))
