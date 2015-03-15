import requests
import simplejson as json

def get_user_friends(user_fb_id):
    app_id = "645422265578276"
    app_secret = "122ec7f041995912ec9c7cff44666bd5"
    
    #get access token
    access_token_url = ("https://graph.facebook.com/v2.2/oauth/access_token?" +\
                       "client_id=%s&client_secret=%s" +\
                       "&grant_type=client_credentials") % (app_id,app_secret)
    resp = requests.get(access_token_url)
    
    #get friends list
    access_token = resp.text
    friends_url = ("https://graph.facebook.com/v2.2/%s/friends?"+\
                  "%s&format=json&method=get&pretty=0&suppress_http_code=1")\
                  % (user_fb_id,access_token)
    resp = requests.get(friends_url)
    friends = json.loads(resp.text)["data"]
    return [f["id"] for f in friends]
