import pymongo
from bson.objectid import ObjectId

#Creates database for storing user information.
# Since the database is only kept in RAM, this function should be called after
# the service is first started.
def get_matchmaker_db():
    client = pymongo.MongoClient('localhost', 27017)
    db = client['fitpals_matchmaker']

    #if database doesn't exist, setup indexes
    if not "posts" in db.collection_names():
        db.users.create_index([("loc", pymongo.GEO2D)])
    return db

#generate new user id
def new_user(db):
    user = {
        "facebook_token":"",
        "apn_token":"",
        "location":[],
        "activity":{},
        "picture_links":[]
    }
    return db.users.insert(user)

#Updates a user's info, specified by user_dict
# If a user_id is not provided, then a new user will be created
# with the attributes specified in user_dict
def update_user(user_dict, db, user_id=None):
    #validate that user_dict is of the correct format
    # possibly do this with a class

    # insert new user_id into db
    if not user_id: user_id = str(new_user(db))

    #capture and log error if invalid "user_id"
    db.users.update({"_id":ObjectId(user_id)},{"$set":user_dict},upsert=False)
    return user_id

def get_nearby_users(user_id, radius, db):
    user = db.users.find_one({"_id":ObjectId(user_id)})
    if not user: return []
    nearby_users = db.users.find({
        "location":{
            "$within":{
                "$center":[user['location'], radius]}}})
    return [str(u['_id']) for u in nearby_users
        if u['activity']['name'] == user['activity']['name']]

def get_user_data(user_id, attr_list, db):
    allowed_attrs = set([
        "location",
        "activity",
        "picture_links"
    ])
    user = db.users.find_one({"_id":ObjectId(user_id)})
    if not user: return {}
    return {attr:user[attr] for attr in allowed_attrs.intersection(attr_list)}
        
def main():
    pass

#This function replaces main() for testing.
def test():
    db = get_matchmaker_db()
    ben_user = {
        "facebook_token":"fb_ben",
        "apn_token":"some apn_ben",
        "location":[1,1],
        "activity":{"name":"walking","time":"30","distance":"3"},
        "picture_links":[]
    }
    ricky_user = {
        "facebook_token":"fb_ricky",
        "apn_token":"apn_ricky",
        "location":[2,2],
        "activity":{"name":"walking","time":"30","distance":"3"},
        "picture_links":[]
    }
    dan_user = {
        "facebook_token":"fb_dan",
        "apn_token":"apn_dan",
        "location":[20,20],
        "activity":{"name":"running","time":"30","distance":"3"},
        "picture_links":[]
    }

    ben_user_id = update_user(ben_user, db)
    ricky_user_id = update_user(ricky_user, db)
    dan_user_id = update_user(dan_user, db)

    print "Testing get_user_data()"
    print get_user_data(ben_user_id,
        ["location","activity","picture_links","facebook_token"], db)
    print

    print "Testing get_nearby_users()"
    for user in get_nearby_users(ricky_user_id,1000,db): print user
    print

if __name__ == "__main__": test()
