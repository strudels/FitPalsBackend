import requests
import base64
import os
import simplejson as json

app_id = "645422265578276"
app_secret = "122ec7f041995912ec9c7cff44666bd5"

def get_user_friends(user_fb_id):
    #get access token
    access_token_url = ("https://graph.facebook.com/v2.3/oauth/access_token?" +\
                       "client_id=%s&client_secret=%s" +\
                       "&grant_type=client_credentials") % (app_id,app_secret)
    resp = requests.get(access_token_url, timeout=3)
    
    #get friends list
    access_token = json.loads(resp.text)["access_token"]
    friends_url = ("https://graph.facebook.com/v2.3/%s/friends?"+\
                  "access_token=%s&format=json&method=get&pretty=0&suppress_http_code=1")\
                  % (user_fb_id,access_token)
    resp = requests.get(friends_url, timeout=3)
    friends = json.loads(resp.text)["data"]
    return [f["id"] for f in friends]
    
def get_test_users():
    #get access token
    access_token_url = ("https://graph.facebook.com/v2.3/oauth/access_token?" +\
                       "client_id=%s&client_secret=%s" +\
                       "&grant_type=client_credentials") % (app_id,app_secret)
    resp = requests.get(access_token_url, timeout=3)
    
    #get friends list
    access_token = json.loads(resp.text)["access_token"]
    url = "https://graph.facebook.com/v2.3/645422265578276/accounts/" +\
          "test-users?access_token=%s" % access_token
    resp = requests.get(url, timeout=3)
    test_users = json.loads(resp.text)["data"]
    return test_users
    
def get_fb_id_via_access_token(access_token):
    get_user_url = "https://graph.facebook.com/v2.3/me?access_token=%s"\
                   % access_token
    resp = json.loads(requests.get(get_user_url, timeout=3).text)
    if "error" in resp: return None
    return resp["id"]

def create_fitpals_secret():
    return base64.b64encode(os.urandom(64))
