import sys
from BeautifulSoup import BeautifulSoup
from pyapns import configure, provision, notify
import simplejson as json

configure({"HOST": "http://localhost:7077/"})
provision("uhsome.Fitpals", open("certs/apns_cert.pem").read(), "sandbox")

def send_apn(device_token, data_dict):
    notify("uhsome.Fitpals", device_token, {"aps":data_dict})

def get_device_tokens(msg):
    jabber_id = BeautifulSoup(msg).find("message")["to"].split('/')[0];
    api_host = "https://strudelcakes.sytes.net:31337"

    client = pymongo.MongoClient(config.get("mongo","hostname"),
        config.getint("mongo","port"))
    db = client[config.get("mongo","dbname")]

    return db.users.find({"jabber_id":jabber_id})["apn_tokens"]

if __name__ == "__main__": 
    apn_tokens = get_device_tokens(sys.stdin.read())
    for token in apn_tokens: send_apn(token, {"aps":{"message":msg}})
