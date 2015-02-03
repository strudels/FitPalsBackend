import requests
import simplejson as json
from datetime import datetime
import sys
import time
import random
import string

if len(sys.argv)==2 and sys.argv[1]=="remote":
    host_url = "https://strudelcakes.sytes.net:31337"
else: host_url = "http://localhost:5000"
print "Testing on " + host_url

test_token = "91e0eee8f8ae9e4f5334bd5f2a07df5fc6fcb0a0b2fce99219918abe2ccd430f"

def get_random_fb_id():
    return ''.join(random.choice(string.digits) for _ in range(32))

def get_dob_stamp(dob_str):
    dob = datetime.strptime(dob_str,"%m/%d/%Y")
    return int(time.mktime(dob.timetuple()))

ben_fb_id = get_random_fb_id()
print ben_fb_id
ben_update = {
    "fb_id":ben_fb_id,
    "latitude":27.924475,
    "longitude":-82.319645,
    "available":True,
    "about_me":"I go fast.",
    "dob":get_dob_stamp("01/30/1992"),
    "apn_tokens":[test_token]
}
ben_activity = {
    "fb_id":ben_fb_id,
    "name":"running",
    "distance":2,
    "time":30
}

ricky_fb_id = get_random_fb_id()
ricky_update = {
    "fb_id":ricky_fb_id,
    "latitude":28.065674,
    "longitude":-82.381193,
    "available":True,
    "about_me":"I go fast.",
    "dob":get_dob_stamp("12/12/1991"),
    "apn_tokens":[test_token]
}
ricky_activity = {
    "fb_id":ricky_fb_id,
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
resp = requests.post(host_url + "/users",
    data={"fb_id":ben_fb_id},verify=False)
print resp.text
print

print "Test 2: Read Ben's User Data"
ben_user_id = json.loads(resp.text)["value"]["user_id"]
resp = requests.get(host_url + "/users/" + ben_user_id,
    params={'attributes':attributes},verify=False)
print resp.text
print

print "Test 3: Update Ben's User Data"
resp = requests.put(host_url + "/users/" + ben_user_id,
    data=ben_update,verify=False)
print resp.text
print

print "Test 4: Update Ben's Activity"
resp = requests.put(host_url + "/users/%s/activity" % ben_user_id,
    data=ben_activity,verify=False)
print resp.text
print

print "Test 5: Read Ben's User Data Again"
resp = requests.get(host_url + "/users/%s" % ben_user_id,
    params={'attributes':['activity','location']},verify=False)
print resp.text
print

print "Test 6: Create Ricky"
resp = requests.post(host_url + "/users",
    data={"fb_id":ricky_fb_id},verify=False)
print resp.text
print

print "Test 7: Read Ricky's User Data"
ricky_user_id = json.loads(resp.text)["value"]["user_id"]
resp = requests.get(host_url + "/users/" + ricky_user_id,
    verify=False)
print resp.text
print

print "Test 8: Update Ricky's User Data"
resp = requests.put(host_url + "/users/" + ricky_user_id,
    data=ricky_update,verify=False)
print resp.text
print

print "Test 9: Update Ricky's Activity"
resp = requests.put(host_url + "/users/%s/activity" % ricky_user_id,
    data=ricky_activity,verify=False)
print resp.text
print

print "Test 10: Read Ricky's User Data Again"
resp = requests.get(host_url + "/users/%s" % ricky_user_id,
    params={'attributes':attributes},verify=False)
print resp.text
print

last_updated = json.loads(resp.text)["value"]["last_updated"]

print "Test 11: Find Ricky's Matches"
resp = requests.get(host_url + "/users",
    params={
        "radius":11,
        "longitude":-82.381193,
        "latitude":28.065674
    },verify=False)
print resp.text
print

print "Test 12: Find Ricky's First 25 Matches"
resp = requests.get(host_url + "/users",
    params={
        "radius":11,
        "longitude":-82.381193,
        "latitude":28.065674,
        "index":0,
        "limit":20
    },verify=False)
print resp.text
print

print "Test 13: Find Ricky's First 25 Matches Before certain time"
resp = requests.get(host_url + "/users",
    params={
        "radius":11,
        "longitude":-82.381193,
        "latitude":28.065674,
        "index":0,
        "limit":20,
        "last_updated":last_updated
    },verify=False)
print resp.text
print

print "Test 14: Find Ricky's First 25 Matches Before certain time, ages 23-25"
resp = requests.get(host_url + "/users",
    params={
        "radius":11,
        "longitude":-82.381193,
        "latitude":28.065674,
        "index":0,
        "limit":20,
        "last_updated":last_updated,
        "min_age":23,
        "max_age":25
    },verify=False)
print resp.text
print

print "Test 15: Find Ricky's First 25 Matches Before certain time, ages 22-25"
resp = requests.get(host_url + "/users",
    params={
        "radius":11,
        "longitude":-82.381193,
        "latitude":28.065674,
        "index":0,"limit":20,
        "last_updated":last_updated,
        "min_age":22,
        "max_age":25
    },verify=False)
print resp.text
print

print "Test 16: Find Ricky's Matches in small radius"
resp = requests.get(host_url + "/users",
    params={
        "radius":10,
        "longitude":-82.381193,
        "latitude":28.065674,
        "index":0,
        "limit":20,
        "last_updated":last_updated,
        "min_age":22,"max_age":25
    },verify=False)
print resp.text
print

print "Test 17: Get Messages For Ben User"
resp = requests.get(host_url + "/users/%s/messages/%s" %\
    (ben_user_id,ricky_user_id), verify=False)
print resp.text
print

print "Test 18: Delete Messages For Ben User"
resp = requests.delete(host_url + "/users/%s/messages/%s" %\
    (ben_user_id,ricky_user_id), verify=False)
print resp.text
print

print "Test 19: Get Messages For Ben User After Deletion"
resp = requests.get(host_url + "/users/%s/messages/%s" %\
    (ben_user_id,ricky_user_id), verify=False)
print resp.text
print

print "Test 20: POST Match For Ben"
resp = requests.post(host_url + "/users/%s/matches" % ben_user_id,
    data={"match_id":ricky_user_id,"fb_id":ben_fb_id,"approved":True}, verify=False)
print resp.text
print

print "Test 21: POST Match For Ricky"
resp = requests.post(host_url + "/users/%s/matches" % ricky_user_id,
    data={"match_id":ben_user_id,"fb_id":ricky_fb_id,"approved":True}, verify=False)
print resp.text
print

print "Test 22: Delete Ben"
resp = requests.delete(host_url + "/users/%s" % ben_user_id,
    data={"fb_id":ben_fb_id})
print resp.text
print

print "Test 23: Delete Ricky"
resp = requests.delete(host_url + "/users/%s" % ricky_user_id,
    data={"fb_id":ricky_fb_id})
print resp.text
print
