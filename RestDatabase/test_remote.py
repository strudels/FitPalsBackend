import requests
import simplejson as json
from datetime import datetime
import time

def get_dob_stamp(dob_str):
    dob = datetime.strptime(dob_str,"%m/%d/%Y")
    return int(time.mktime(dob.timetuple()))

ben_fb_id = "fb9001"
ben_update = {
    "fb_id":"fb9001",
    "latitude":27.924475,
    "longitude":-82.319645,
    "available":True,
    "about_me":"I go fast.",
    "dob":get_dob_stamp("01/30/1992")
}
ben_activity = {
    "fb_id":"fb9001",
    "name":"running",
    "distance":2,
    "time":30
}

ricky_fb_id = "fb9002"
ricky_update = {
    "fb_id":"fb9002",
    "latitude":28.065674,
    "longitude":-82.381193,
    "available":True,
    "about_me":"I go fast.",
    "dob":get_dob_stamp("12/12/1991")
}
ricky_activity = {
    "fb_id":"fb9002",
    "name":"running",
    "distance":2,
    "time":30
}

attributes = [
    "location",
    "about_me",
    "dob",
    "last_updated",
    "activity",
    "primary_picture",
    "secondary_pictures",
    "available",
]

print "Test 1: Create Ben"
resp = requests.post("https://strudelcakes.sytes.net:31337/users",
    data={"fb_id":ben_fb_id},verify=False)
print resp.text
print

print "Test 2: Read Ben's User Data"
user_id = json.loads(resp.text)["value"]["user_id"]
resp = requests.get("https://strudelcakes.sytes.net:31337/users/" + user_id,
    params={'attributes':attributes},verify=False)
print resp.text
print

print "Test 3: Update Ben's User Data"
resp = requests.put("https://strudelcakes.sytes.net:31337/users/" + user_id,
    data=ben_update,verify=False)
print resp.text
print

print "Test 4: Update Ben's Activity"
resp = requests.put("https://strudelcakes.sytes.net:31337/users/%s/activity" % user_id,
    data=ben_activity,verify=False)
print resp.text
print

print "Test 5: Read Ben's User Data Again"
resp = requests.get("https://strudelcakes.sytes.net:31337/users/%s" % user_id,
    params={'attributes':['activity','location']},verify=False)
print resp.text
print

print "Test 6: Create Ricky"
resp = requests.post("https://strudelcakes.sytes.net:31337/users",
    data={"fb_id":ricky_fb_id},verify=False)
print resp.text
print

print "Test 7: Read Ricky's User Data"
user_id = json.loads(resp.text)["value"]["user_id"]
resp = requests.get("https://strudelcakes.sytes.net:31337/users/" + user_id,
    verify=False)
print resp.text
print

print "Test 8: Update Ricky's User Data"
resp = requests.put("https://strudelcakes.sytes.net:31337/users/" + user_id,
    data=ricky_update,verify=False)
print resp.text
print

print "Test 9: Update Ricky's Activity"
resp = requests.put("https://strudelcakes.sytes.net:31337/users/%s/activity" % user_id,
    data=ricky_activity,verify=False)
print resp.text
print

print "Test 10: Read Ricky's User Data Again"
resp = requests.get("https://strudelcakes.sytes.net:31337/users/%s" % user_id,
    params={'attributes':attributes},verify=False)
print resp.text
print

last_updated = json.loads(resp.text)["value"]["last_updated"]

print "Test 11: Find Ricky's Matches"
resp = requests.get("https://strudelcakes.sytes.net:31337/users/%s/matches" % user_id,
    params={"radius":11},verify=False)
print resp.text
print

print "Test 12: Find Ricky's First 25 Matches"
resp = requests.get("https://strudelcakes.sytes.net:31337/users/%s/matches" % user_id,
    params={"radius":11,"index":0,"limit":20},verify=False)
print resp.text
print

print "Test 13: Find Ricky's First 25 Matches Before certain time"
resp = requests.get("https://strudelcakes.sytes.net:31337/users/%s/matches" % user_id,
    params={"radius":11,"index":0,"limit":20,"last_updated":last_updated},verify=False)
print resp.text
print

print "Test 14: Find Ricky's First 25 Matches Before certain time, ages 23-25"
resp = requests.get("https://strudelcakes.sytes.net:31337/users/%s/matches" % user_id,
    params={"radius":11,"index":0,"limit":20,"last_updated":last_updated, "min_age":23, "max_age":25},verify=False)
print resp.text
print

print "Test 15: Find Ricky's First 25 Matches Before certain time, ages 22-25"
resp = requests.get("https://strudelcakes.sytes.net:31337/users/%s/matches" % user_id,
    params={"radius":11,"index":0,"limit":20,"last_updated":last_updated, "min_age":22, "max_age":25},verify=False)
print resp.text
print

print "Test 16: Find Ricky's Matches in small radius"
resp = requests.get("https://strudelcakes.sytes.net:31337/users/%s/matches" % user_id,
    params={"radius":10,"index":0,"limit":20,"last_updated":last_updated, "min_age":22, "max_age":25},verify=False)
print resp.text
print