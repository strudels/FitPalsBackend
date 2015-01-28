import pymongo
import time
from datetime import datetime
from bson import ObjectId

client = pymongo.MongoClient('localhost', 27017)
db = client['fitpals_matchmaker']

#get number of seconds since utc epoch
def _now():
    return int(datetime.utcnow().strftime("%s"))

def _today():
    return int(time.mktime(datetime.now().date().timetuple()))

#initialize database
def init_db():
    if not "posts" in db.collection_names():
        db.users.create_index([("loc", pymongo.GEO2D)])

#lookup user_id for a given fb_id
def find_user_id(fb_id):
    return db.users.find_one({"fb_id":fb_id})["_id"]

#generate new user id
def insert_user(fb_id):
    user = {
        "fb_id":fb_id,
        "apn_tokens":[],
        "about_me":"",
        "location":[],
        "activity":{},
        "primary_picture":"",
        "secondary_pictures":[],
        "last_updated":_now(),
        "dob":_today(),
        "available":False
    }
    return db.users.insert(user)

#Updates a user's info, specified by user_dict
# If a user_id is not provided, then a new user will be created
# with the attributes specified in user_dict
def update_user(user_id,user_dict):
    user_dict["last_updated"] = _now()
    #capture and log error if invalid "user_id"
    return db.users.update({"_id":ObjectId(user_id)},
        {"$set":user_dict},upsert=False)

#radius specified in miles
def get_nearby_users(user_id, radius):
    user = db.users.find_one({"_id":ObjectId(user_id)})
    if not user: return []
    nearby_users = list(db.users.find({
        "location":{
            "$geoWithin":{
                #3959 == approximate radius of the earth in miles
                # This number is used so that the radius can
                # be specified in miles
                "$centerSphere":[user['location'], radius / 3959]}}}))
    for u in nearby_users:
        u['activity']['distance'] =\
            abs(u['activity']['distance'] - user['activity']['distance'])
        u['activity']['time'] =\
            abs(u['activity']['time'] - user['activity']['time'])
    nearby_users.sort(key=lambda x:x['activity']['distance'])
    nearby_users.sort(key=lambda x:x['activity']['time'])
    nearby_users = filter(lambda x:x["available"]==True, nearby_users)

    return [u for u in nearby_users
        if u['activity']['name'] == user['activity']['name']
            and u['_id'] != user['_id']]

def get_user(user_id):
    user = db.users.find_one({"_id":ObjectId(user_id)})
    if not user: return {}
    return user
