import requests
import simplejson as json

user = {
    "facebook_token":"fb_ben",
    "apn_token":"some apn_ben",
    "location":[1,1],
    "activity":{"name":"walking","time":"30","distance":"3"},
    "picture_links":[]
}

print "Test 1: Create User"
resp = requests.post("http://localhost:5000/users",
    data={"fb_id":"fb9001"})
print resp.text
print

print "Test 2: Read User Data"
user_id = json.loads(resp.text)["value"]["user_id"]
resp = requests.get("http://localhost:5000/users/" + user_id,
    params={'attributes':'location'})
print resp.text
print

print "Test 3: Update User Data"
resp = requests.put("http://localhost:5000/users/" + user_id,
    data={'fb_id':'fb9001','location_x':4, 'location_y':5})
print resp.text
print

print "Test 4: Update User Activity"
resp = requests.put("http://localhost:5000/users/%s/activity" % user_id,
    data={"fb_id":"fb9001","name":"running","distance":9000,"time":5})
print resp.text
print

print "Test 5: Read User Data Again"
resp = requests.get("http://localhost:5000/users/%s" % user_id,
    params={'attributes':['activity','location']})
print resp.text
print

print "Test 6: Find Matches"
resp = requests.get("http://localhost:5000/users/%s/matches" % user_id,
    params={"radius":9000})
print resp.text
print

print "Test 7: Find First 25 Matches"
resp = requests.get("http://localhost:5000/users/%s/matches" % user_id,
    params={"radius":9000,"index":0,"limit":20})
print resp.text
print
