import database

from flask import Flask
from flask import request
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
        user_id = database.insert_user(args.fb_id)
        return str(user_id)

@api.resource('/users/<user_id>')
class UserAPI(Resource):
    def get(self):
        print 'ohai' + user_id
        parser = reqparse.RequestParser()
        parser.add_argument("attributes",
            type=str, location='args', required=True, action="append")
        args = parser.parse_args()

        #Get user from db
        user = database.get_user(user_id, args.attributes)

        #Only allow certain attributes to be requested by clients
        allowed_attrs = set(["location","activity","picture_links"])
        return json.dumps(
            {attr:user[attr] for attr in allowed_attrs.intersection(attr_list)}
        )
    
    def put(self):
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
        user = database.get_user(user_id)

        #ensure user is valid by checking if fb_id is correct
        if user["fb_id"] != args.fb_id: return "Invalid facebook id"

        #update fields specified by client
        if args.location_x and args.location_y:
            user["location"] = [args.location_x,args.location_y]
        if args.pictures: user["picture_links"] = args.pictures

        return database.update_user(user_id,user)

@api.resource('/users/<user_id>/activity')
class ActivityAPI(Resource):
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument("fb_id",
            type=str, location='form', required=True)
        parser.add_argument("name",
            type=str,location='form', required=False)
        parser.add_argument("distance",
            type=str,location='form', required=False)
        parser.add_argument("time",
            type=str,location='form', required=False)
        args = parser.parse_args()

        #get user to update from db
        user = database.get_user(user_id)

        #ensure user is valid by checking if fb_id is correct
        if user["fb_id"] != args.fb_id: return "Invalid facebook id"

        #update activity fields specified by client
        if args.name: user['activity']["name"] = args.name
        if args.distance: user['activity']["distance"] = args.distance
        if args.time: user["activity"]["time"] = args.time
        
        return databasatabasatabasatabasatabasatabasatabasatabasatabase.update_user(user_id,user)
    


@api.resource('/users/<user_id>/matches')
class UserMatchAPI(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("radius",
            type=float, location='args', required=True)
        args = parser.parse_args()
        return json.dumps(database.get_nearby_users(user_id,args.radius))
        
if __name__=='__main__':
    app.run(host='0.0.0.0')
