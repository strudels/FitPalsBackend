from app import socketio
import simplejson as json
import base64
from apns import APNs, Payload
from threading import Thread
from Queue import Queue

apns = APNs(use_sandbox=True,
            cert_file='/home/strudels/Desktop/sand.pem',
            key_file='/home/strudels/Desktop/sand.pem')


thread_q = Queue()
def async_notification_thread_manager():
    while True:
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
    thread = Thread(target=send_message_thread_function,
                      args=(user,tokens,path,http_method,value,))
    thread_q.put(thread)
