import pymongo
import time
from datetime import datetime
from bson import ObjectId
import MySQLdb as mysql
from ConfigParser import ConfigParser

#open config file
config = ConfigParser()
config.read(["fitpals_api.cfg"])

#make connections according to config
client = pymongo.MongoClient(config.get("mongo","hostname"),
    config.getint("mongo","port"))
db = client[config.get("mongo","dbname")]
jabber_db = mysql.connect(
    host=config.get("tigase","hostname"),
    user=config.get("tigase","username"),
    passwd=config.get("tigase","password"),
    db=config.get("tigase","dbname"),
    port=config.getint("tigase","port")
)

#user attributes
private_attrs = ["fb_id","apn_tokens","approved_users","denied_users"]
public_attrs = [
    "about_me",
    "location",
    "activity",
    "primary_picture",
    "secondary_pictures",
    "last_updated",
    "dob",
    "available",
    "jabber_id"
]

#get number of seconds since utc epoch
def _now():
    return int(datetime.utcnow().strftime("%s"))

def _today():
    return int(time.mktime(datetime.now().date().timetuple()))

def _generate_jabber_id(user_id):
    return user_id + "@" + config.get("jabber","hostname")

def get_messages(owner_id, other_id):
    #map id's to jabber id's
    owner_id = _generate_jabber_id(owner_id)
    other_id = _generate_jabber_id(other_id)

    #get messages from jabber database
    cursor = jabber_db.cursor()
    results = cursor.callproc("get_messages",[owner_id,other_id])
    results = [r[0] for r in cursor.fetchall()]
    cursor.close()
    jabber_db.commit()
    return results

def delete_messages(owner_id, other_id):
    #map id's to jabber id's
    owner_id = _generate_jabber_id(owner_id)
    other_id = _generate_jabber_id(other_id)

    #delete message from jabber database
    cursor = jabber_db.cursor()
    cursor.callproc("delete_messages",[owner_id,other_id])
    cursor.close()
    jabber_db.commit()

#initialize database
def init_db():
    if not "posts" in db.collection_names():
        db.users.create_index([("loc", pymongo.GEO2D)])

#lookup user_id for a given fb_id
def find_user_by_fb_id(fb_id):
    user = db.users.find_one({"fb_id":fb_id})
    user["user_id"] = user["_id"]
    del user["_id"]
    return user

#generate skeleton user with user_id, jabber_id, and password
def insert_user(fb_id):
    #create user in users database
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
        "available":False,
        "jabber_id":"",
        "approved_users":[],
        "denied_users":[]
    }
    user_id = str(db.users.insert(user))
    user = db.users.find_one({"_id":ObjectId(user_id)})

    #create jabber account to be paired with user account
    jabber_id = _generate_jabber_id(user_id)
    cursor = jabber_db.cursor()
    #CATCH THIS EXCEPTION!!!!!!!!!!!
    # if this fails, the user that was created must be deleted from the db
    cursor.callproc("TigAddUserPlainPw", [jabber_id,fb_id])
    cursor.close()
    jabber_db.commit()

    #update user's jabber_id
    #CATCH THIS EXCEPTION AS WELL
    # WILL NEED TO DELETE BOTH ACCOUNTS IF THIS FAILS
    user["jabber_id"] = jabber_id
    update_user(user_id,user)

    return {
        "user_id":user_id,
        "jabber_id":jabber_id,
        "password":fb_id
    }
    

#Updates a user's info, specified by user_dict
# If a user_id is not provided, then a new user will be created
# with the attributes specified in user_dict
def update_user(user_id,user_dict):
    user_dict["last_updated"] = _now()
    #MAKE SURE THIS HACK IS ALRIGHT
    if "user_id" in user_dict.keys(): del user_dict["user_id"]
    if "_id" in user_dict.keys(): del user_dict["_id"]
    #capture and log error if invalid "user_id"
    return db.users.update({"_id":ObjectId(user_id)},
        {"$set":user_dict},upsert=False)

def get_user(user_id):
    user = db.users.find_one({"_id":ObjectId(user_id)})
    if not user: return {}
    user["user_id"] = user["_id"]
    del user["_id"]
    return user

def get_users():
    users = db.users.find()
    for user in users:
        for attr in private_attrs:
            del user[attr]
            user["user_id"] = user["_id"]
            del user["_id"]
    return users

#radius specified in miles
def get_nearby_users(longitude, latitude, radius):
    nearby_users = list(db.users.find({
        "location":{
            "$geoWithin":{
                #3959 == approximate radius of the earth in miles
                # This number is used so that the radius can
                # be specified in miles
                "$centerSphere":[[longitude,latitude], radius / 3959]}}}))
    for user in nearby_users:
        user["user_id"] = user["_id"]
        del user["_id"]
    return filter(lambda x:x["available"]==True, nearby_users)
