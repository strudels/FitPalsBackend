from app import socketio
import simplejson as json
from pyapns import configure, provision, notify
import base64

configure({'HOST': 'http://localhost:7077/'})
provision('uhsome.Fitpals', open('/home/strudels/Desktop/aps_sandbox.pem').read(),
          'sandbox')

def errback(e):
    import pdb; pdb.set_trace()
    print e

def send_message(user,event_name,event_value=None):
    if user.online:
        #send websocket notification
        socketio.emit(event_name,event_value,room=str(user.id))
    else:
        #send APNS notification
        value = {"name":event_name,"value":event_value}
        for d in user.devices.all():
            token_hex = base64.b64decode(d.token).encode('hex')
            stuff = notify('uhsome.Fitpals',
                           token_hex,
                           {'aps':{'alert': value}},
                           errback=errback)
