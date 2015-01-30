import database
from response import Response

from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from ConfigParser import ConfigParser

config = ConfigParser()
config.read(["fitpals_api.cfg"])

app=Flask(__name__)
api=Api(app)

def _age_to_day(age):
    day = datetime.now().date() - relativedelta(years=age)
    return int(time.mktime(day.timetuple()))

@api.resource('/users')
class UserListAPI(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("longitude",
            type=float, location='args', required=False)
        parser.add_argument("latitude",
            type=float, location='args', required=False)
        parser.add_argument("radius",
            type=float, location='args', required=False)
        parser.add_argument("limit",
            type=int, location="args", required=False)
        parser.add_argument("index",
            type=int, location="args", required=False)
        parser.add_argument("last_updated",
            type=int, location="args", required=False)
        parser.add_argument("min_age",
            type=int, location="args", required=False)
        parser.add_argument("max_age",
            type=int, location="args", required=False)
        parser.add_argument("activity_name",
            type=str, location="args", required=False)
        parser.add_argument("activity_distance",
            type=int, location="args", required=False)
        parser.add_argument("activity_time",
            type=int, location="args", required=False)
        args = parser.parse_args()

        #apply filters specified by user to matches
        if not (args.radius and args.longitude and args.latitude):
            matches = database.get_users()
        else: 
            #ensure GPS parameters are valid
            if (args.radius <= 0) or not (-180 <= args.longitude <= 180)\
                or not (-90 <= args.latitude <= 90):
                return Response(status=400,message="Invalid GPS parameters"),400
            matches = database.get_nearby_users(args.longitude,
                args.latitude, args.radius)

        if args.last_updated:
            matches = [m for m in matches\
                if m["last_updated"] <= args.last_updated]

        if args.min_age:
            matches = [m for m in matches\
                if m["dob"] <= _age_to_day(args.min_age)]

        if args.max_age:
            matches = [m for m in matches\
                if m["dob"] >= _age_to_day(args.max_age)]

        if args.activity_name:
            matches = [m for m in matches
                if m['activity']['name'] == args.activity_name]

        if args.activity_distance:
            for m in matches:
                m['activity']['distance'] =\
                    abs(m['activity']['distance'] - args.activity_distance)
            matches.sort(key=lambda x:x['activity']['distance'])

        if args.activity_time:
            for m in matches:
                m['activity']['time'] =\
                    abs(m['activity']['time'] - user['activity']['time'])
            matches.sort(key=lambda x:x['activity']['time'])

        if args.limit!=None and args.index!=None:
            matches = matches[args.index:args.index+args.limit]

        #return matches' user_ids
        return Response(status=200,message="Matches found.",
            value={"matches":[str(m["_id"]) for m in matches]}).__dict__,200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('fb_id',
            type=str, location='form', required=True)
        args = parser.parse_args()

        #return user_id, jabber_id, and password if user already exists
        try:
            user = database.find_user_by_fb_id(args.fb_id)
            value = {
                "user_id":str(user["_id"]),
                "jabber_id":user["jabber_id"],
                "password":user["fb_id"]
            }
            return Response(status=200,message="User found.",
                value=value).__dict__,200
        except: pass

        #create new user and return it's new user_id, jabber_id, and password
        try:
            new_user = database.insert_user(args.fb_id)
            return Response(status=201,message="User created.",
                value=new_user).__dict__,201
        except:
            return Response(status=400, 
                message="Could not create user").__dict__,400

@api.resource('/users/<user_id>')
class UserAPI(Resource):
    def get(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("attributes",
            type=str, location='args', required=False, action="append")
        args = parser.parse_args()

        #Get user from db
        try: user = database.get_user(user_id)
        except:
            return Response(status=400,message="Invalid user id.").__dict__,400

        #cast id from ObjectId() to str()
        user["_id"] = str(user["_id"])

        #don't allow user to get secrets of other users
        del user["fb_id"]
        del user["apn_tokens"]

        #if attributes were specified, only return specified attributes
        if args.attributes:
            user = {attr:user[attr]\
                for attr in args.attributes if attr in user.keys()
            }
        return Response(status=200,
            message="User found.",value=user).__dict__,200
    
    def put(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("fb_id",
            type=str, location='form', required=True)
        parser.add_argument("apn_tokens",
            type=str, location='form', required=False, action="append")
        parser.add_argument("longitude",
            type=float, location='form', required=False)
        parser.add_argument("latitude",
            type=float, location='form', required=False)
        parser.add_argument("primary_picture",
            type=str, location='form', required=False, action="append")
        parser.add_argument("secondary_pictures",
            type=str, location='form', required=False, action="append")
        parser.add_argument("about_me",
            type=str, location='form', required=False, action="append")
        parser.add_argument("available",
            type=bool, location='form', required=False)
        parser.add_argument("dob",
            type=int, location='form', required=False)
        args = parser.parse_args()

        #get user to update from db
        try: user = database.get_user(user_id)
        except:
            return Response(status=400,message="Invalid user id.").__dict__,400

        #ensure user is valid by checking if fb_id is correct
        if user["fb_id"] != args.fb_id:
            return Response(status=401,message="Incorrect fb_id.").__dict__,401

        #update fields specified by client
        if args.longitude and args.latitude:
            user["location"] = [args.longitude,args.latitude]
        if args.primary_picture: user["primary_picture"] = args.primary_picture
        if args.secondary_pictures:
            user["secondary_pictures"] = args.secondary_pictures
        if args.about_me: user["about_me"] = args.about_me
        if args.available: user["available"] = args.available
        if args.dob: user["dob"] = args.dob

        #Update database and return whether or not the update was a success
        try:
            update_status = database.update_user(user_id,user)
            if update_status["ok"]==1:
                return Response(status=202,message="User updated").__dict__,202
            else:
                return Response(status=400,
                    message="User update failed.").__dict__,400
        except:
            return Response(status=400,
                message="Invalid user data.").__dict__,400

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
            return Response(status=400,message="Invalid user id.").__dict__,400

        #ensure user is valid by checking if fb_id is correct
        if user["fb_id"] != args.fb_id:
            return Response(status=401,message="Incorrect fb_id.").__dict__,401

        #update activity fields specified by client
        if args.name: user['activity']["name"] = args.name
        if args.distance: user['activity']["distance"] = args.distance
        if args.time: user["activity"]["time"] = args.time
        
        #Update database and return whether or not the update was a success
        try:
            update_status = database.update_user(user_id,user)
            if update_status["ok"]==1:
                return Response(status=202,message="User updated").__dict__,202
            else: return Response(status=400,
                message="User update failed.").__dict__, 400
        except:
            return Response(status=400,
                message="Invalid user data.").__dict__,400

@api.resource('/users/<user_id>/matches')
class UserMatchAPI(Resource):
    def put(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument("match_id",
            type=str, location="form", required=True)
        args = parser.parse_args()

        #get users from database
        user = database.get_user(user_id)
        match = database.get_user(args.match_id)

        #add match to user's matches
        user[""] = user[""].append(match_id)
        database.update_user(user_id,user)

        #add user to match's remote matches
        match[""] = match[""].append(user_id)
        database.update_user(match_id,match)



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
