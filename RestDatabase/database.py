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
    return results

def delete_messages(owner_id, other_id):
    #map id's to jabber id's
    owner_id = _generate_jabber_id(owner_id)
    other_id = _generate_jabber_id(other_id)

    #delete message from jabber database
    cursor = jabber_db.cursor()
    try:cursor.callproc("delete_messages",[owner_id,other_id])
    except Exception as e: print "Exception: ", e
    cursor.close()
    jabber_db.commit()

#initialize database
def init_db():
    if not "posts" in db.collection_names():
        db.users.create_index([("loc", pymongo.GEO2D)])

#lookup user_id for a given fb_id
def find_user_by_fb_id(fb_id):
    return db.users.find_one({"fb_id":fb_id})

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
        "jabber_id":""
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
    del user_dict["_id"]
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
