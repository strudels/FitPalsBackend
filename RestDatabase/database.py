import pymongo

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
    return db.users.update({"_id":ObjectId(user_id)},{"$set":user_dict},upsert=False)

def get_nearby_users(user_id, radius):
    user = db.users.find_one({"_id":ObjectId(user_id)})
    if not user: return []
    nearby_users = db.users.find({
        "location":{
            "$within":{
                "$center":[user['location'], radius]}}})
    return [str(u['_id']) for u in nearby_users
        if u['activity']['name'] == user['activity']['name']]

def get_user(user_id):
    user = db.users.find_one({"_id":ObjectId(user_id)})
    if not user: return {}
    return user
