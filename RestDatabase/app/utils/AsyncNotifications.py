from app import socketio
import simplejson as json
from pyapns import configure, provision, notify
import base64
from apns import APNs, Payload

apns = APNs(use_sandbox=True,
            cert_file='/home/strudels/Desktop/sand.pem',
            key_file='/home/strudels/Desktop/sand.pem')

def send_message(user,path,http_method,value=None):
    info = {
        "path":path,
        "http_method":http_method,
        "value":value
    }
    if user.online:
        #send websocket notification
        socketio.emit("update",info,room=str(user.id))
    elif path=="/matches" and http_method=="POST":
        #send APNS notification
        for d in user.devices.all():
            token_hex = base64.b64decode(d.token).encode('hex')
            payload = Payload(alert="Match found!", custom=info)
            apns.gateway_server.send_notification(token_hex,payload)
    elif path=="/messages" and http_method=="POST":
        #send APNS notification
        for d in user.devices.all():
            token_hex = base64.b64decode(d.token).encode('hex')
            payload = Payload(alert="Message Received!", custom=info)
            apns.gateway_server.send_notification(token_hex,payload)
