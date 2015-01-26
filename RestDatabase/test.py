import requests
import simplejson as json

user = {
    "facebook_token":"fb_ben",
    "apn_token":"some apn_ben",
    "location":[1,1],
    "activity":{"name":"walking","time":"30","distance":"3"},
    "picture_links":[]
}

print "Test 1:"
resp = requests.post("http://localhost:5000/update-user",
    data={'user_info':json.dumps(user)})
print resp.text
print

print "Test 2:"
user_id = resp.text
resp = requests.get("http://localhost:5000/search",
    params={'user_id':user_id, 'radius':100})
print resp.text
print

print "Test 3:"
resp = requests.get("http://localhost:5000/users",
    params={"user_id":user_id, "attributes":["location","activity"]})
print resp.text
print
