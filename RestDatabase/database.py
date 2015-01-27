import pymongo
from bson import ObjectId

client = pymongo.MongoClient('localhost', 27017)
db = client['fitpals_matchmaker']

#initialize database
def init_db():
    if not "posts" in db.collection_names():
        db.users.create_index([("loc", pymongo.GEO2D)])

#generate new user id
def insert_user(fb_id):
    user = {
        "fb_id":fb_id,
        "apn_tokens":[],
        "about_me":"",
        "location":[],
        "activity":{},
        "primary_picture":"",
        "secondary_pictures":[]
    }
    return db.users.insert(user)

#Updates a user's info, specified by user_dict
# If a user_id is not provided, then a new user will be created
# with the attributes specified in user_dict
def update_user(user_id,user_dict):
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
    #map distance and time to show distance between user values
    for u in nearby_users:
        u['activity']['distance'] =\
            abs(u['activity']['distance'] - user['activity']['distance'])
        u['activity']['time'] =\
            abs(u['activity']['time'] - user['activity']['time'])
    nearby_users.sort(key=lambda x:x['activity']['distance'])
    nearby_users.sort(key=lambda x:x['activity']['time'])
    return [str(u['_id']) for u in nearby_users
        if u['activity']['name'] == user['activity']['name']
            and u['_id'] != user['_id']]

def get_user(user_id):
    user = db.users.find_one({"_id":ObjectId(user_id)})
    if not user: return {}
    return user
