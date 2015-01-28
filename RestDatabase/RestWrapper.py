import database
from response import Response

from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json

app=Flask(__name__)
api=Api(app)

@api.resource('/users')
class UserListAPI(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('fb_id',
            type=str, location='form', required=True)
        args = parser.parse_args()
        try:
            user_id = database.insert_user(args.fb_id)
            return Response(status=201, value={"user_id":str(user_id)}).__dict__
        except:
            return Response(status=400, 
                message="Could not create user").__dict__

@api.resource('/users/<user_id>')
class UserAPI(Resource):
    def get(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("attributes",
            type=str, location='args', required=True, action="append")
        args = parser.parse_args()

        #Get user from db
        try: user = database.get_user(user_id)
        except:
            return Response(status=400,message="Invalid user id.").__dict__

        #Only allow certain attributes to be requested by clients
        allowed_attrs = set(["location","activity","picture_links"])
        value = {attr:user[attr]\
            for attr in allowed_attrs.intersection(args.attributes)
        }
        return Response(status=200,value=value).__dict__
    
    def put(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("fb_id",
            type=str, location='form', required=True)
        parser.add_argument("apn_tokens",
            type=str, location='form', required=False, action="append")
        parser.add_argument("location_x",
            type=int, location='form', required=False)
        parser.add_argument("location_y",
            type=int, location='form', required=False)
        parser.add_argument("pictures",
            type=str, location='form', required=False, action="append")
        parser.add_argument("about_me",
            type=str, location='form', required=False, action="append")
        args = parser.parse_args()

        #get user to update from db
        try: user = database.get_user(user_id)
        except:
            return Response(status=400,message="Invalid user id.").__dict__

        #ensure user is valid by checking if fb_id is correct
        if user["fb_id"] != args.fb_id: return Response(status=401).__dict__

        #update fields specified by client
        if args.location_x and args.location_y:
            user["location"] = [args.location_x,args.location_y]
        if args.pictures: user["picture_links"] = args.pictures

        #Update database and return whether or not the update was a success
        try:
            update_status = database.update_user(user_id,user)
            if update_status["ok"]==1: return Response(status=202).__dict__
            else: return Response(status=400,
                message="User update failed.").__dict__
        except:
            return Response(status=400,message="Invalid user data.").__dict__

@api.resource('/users/<user_id>/activity')
class ActivityAPI(Resource):
    def put(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("fb_id",
            type=str, location='form', required=True)
        parser.add_argument("name",
            type=str,location='form', required=False)
        parser.add_argument("distance",
            type=int,location='form', required=False)
        parser.add_argument("time",
            type=int,location='form', required=False)
        args = parser.parse_args()

        #get user to update from db
        try: user = database.get_user(user_id)
        except:
            return Response(status=400,message="Invalid user id.").__dict__

        #ensure user is valid by checking if fb_id is correct
        if user["fb_id"] != args.fb_id: return Response(status=401).__dict__

        #update activity fields specified by client
        if args.name: user['activity']["name"] = args.name
        if args.distance: user['activity']["distance"] = args.distance
        if args.time: user["activity"]["time"] = args.time
        
        #Update database and return whether or not the update was a success
        try:
            update_status = database.update_user(user_id,user)
            if update_status["ok"]==1: return Response(status=202).__dict__
            else: return Response(status=400,
                message="User update failed.").__dict
        except:
            return Response(status=400,message="Invalid user data.").__dict__

@api.resource('/users/<user_id>/matches')
class UserMatchAPI(Resource):
    def get(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("radius",
            type=float, location='args', required=True)
        args = parser.parse_args()

        #ensure radius is greater than 0
        if args.radius <= 0:
            return Response(status=400,message="Invalid radius")

        #return user_id's for nearby users
        try: matches = database.get_nearby_users(user_id,args.radius)
        except: return Response(status=400,message="Invalid user id.").__dict__
        return Response(status=200,value=matches).__dict__
        
if __name__=='__main__':
    app.run(host='0.0.0.0')
