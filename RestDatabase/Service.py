import pymongo
from bson.objectid import ObjectId

#Creates database for storing user information.
# Since the database is only kept in RAM, this function should be called after
# the service is first started.
def get_matchmaker_db():
    client = pymongo.MongoClient('localhost', 27017)
    db = client['fitpals_matchmaker']
    return db

#generate new user id
def new_user(db):
    user = {
        "facebook_token":"",
        "apn_token":"",
        "coords":[],
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
    pass

    # insert new user_id into db
    if not user_id: user_id = str(new_user(db))

    #capture and log error if invalid "user_id"
    db.users.update({"_id":ObjectId(user_id)},{"$set":user_dict},upsert=False)
    return user_id

def get_user_data(user_id, attr_list, db):
    allowed_attrs = set([
        "coords",
        "activity",
        "picture_links"
    ])
    user = db.users.find_one({"_id":ObjectId(user_id)})
    if not user: return {}
    return {attr:user[attr] for attr in allowed_attrs.intersection(attr_list)}
        
def main():
    pass

#This function should not be run unless testing, which would require
# a separate driver program
def test():
    db = get_matchmaker_db()
    test_user = {
        "facebook_token":"some facebook token",
        "apn_token":"some apn_token",
        "coords":[1,1],
        "activity":{"name":"walking","time":"30","distance":"3"},
        "picture_links":[]
    }

    test_user_id = update_user(test_user, db)
    print get_user_data(test_user_id,
        ["coords","activity","picture_links","facebook_token"], db)

if __name__ == "__main__": test()
