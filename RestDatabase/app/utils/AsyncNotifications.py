from app import socketio
import simplejson as json
import base64
from apns import APNs, Payload
from threading import Thread
from Queue import Queue
from ConfigParser import ConfigParser
import os.path
from os.path import basename,dirname

config = ConfigParser()
config.read([dirname(__file__) + "/../fitpals_api.cfg"])

if not os.path.isfile(config.get("certs","apns_cert")):
    raise Exception("Certificate file not found.")
apns = APNs(use_sandbox=True,
            cert_file=config.get("certs","apns_cert"),
            key_file=config.get("certs","apns_cert"))

thread_q = Queue()
manager_thread_should_be_alive = True
def async_notification_thread_manager():
    global manager_thread_should_be_alive
    global thread_q
    while manager_thread_should_be_alive:
        thread = thread_q.get()
        thread.start()
        thread.join()
manager_thread = Thread(target=async_notification_thread_manager)
manager_thread.start()

def get_thread_q():
    return thread_q

def send_message_thread_function(user,tokens,path,http_method,value):
    info = {
        "path":path,
        "http_method":http_method,
        "value":value
    }
    if user["online"]:
        #send websocket notification
        socketio.emit("update",info,room=str(user["id"]))
    elif path=="/matches" and http_method=="POST":
        #send APNS notification
        for t in tokens:
            token_hex = base64.b64decode(t).encode('hex')
            payload = Payload(alert="Match found!", custom=info)
            apns.gateway_server.send_notification(token_hex,payload)
    elif path=="/messages" and http_method=="POST":
        #send APNS notification
        for t in tokens:
            token_hex = base64.b64decode(d.token).encode('hex')
            payload = Payload(alert="Message Received!", custom=info)
            apns.gateway_server.send_notification(token_hex,payload)

def send_message(user,tokens,path,http_method,value=None):
    global thread_q
    thread = Thread(target=send_message_thread_function,
                      args=(user,tokens,path,http_method,value,))
    thread_q.put(thread)
