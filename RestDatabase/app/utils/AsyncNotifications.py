from app import socketio
import simplejson as json
import base64
from apns import APNs, Payload
from ConfigParser import ConfigParser
from threading import Thread
from Queue import Queue
import os.path
from os.path import basename,dirname

config = ConfigParser()
config.read([dirname(__file__) + "/../fitpals_api.cfg"])

if not os.path.isfile(config.get("certs","apns_cert")):
    raise Exception("Certificate file not found.")
apns = APNs(use_sandbox=True,
            cert_file=config.get("certs","apns_cert"),
            key_file=config.get("certs","apns_cert"),
            enhanced=True)

thread_q = Queue()
def async_notification_thread_manager():
    global thread_q
    while True:
        thread = thread_q.get()
        thread.start()
        thread.join()
manager_thread = Thread(target=async_notification_thread_manager)
manager_thread.start()

def emit_wrapper(name,value,room):
    socketio.emit(name,value,room=room)

def send_message(user,path,http_method,value=None,apn_send=False):
    info = {
        "path":path,
        "http_method":http_method,
        "value":value
    }
    if apn_send and user.online == False:
        for d in user.devices.all():
            token_hex = base64.b64decode(d.token).encode('hex')
            if path=="/matches":
                payload = Payload(alert="New Match!", custom=info)
            else: #path=="/messages"
                payload = Payload(alert="New Message!", custom=info)
            apns.gateway_server.send_notification(token_hex,payload)
    else:
        global thread_q
        thread = Thread(target=emit_wrapper,
                        args=("update",info,str(user.id)))
        thread_q.put(thread)
            
    #keeping this code commented out for now
    """
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
    """
