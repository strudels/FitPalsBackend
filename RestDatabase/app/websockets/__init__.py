from flask.ext.socketio import emit, join_room
from app.models import *
from app import socketio

#listen for client's to connect to chat websocket
@socketio.on("connect")
def connect():
    emit("connected")
    
#need to add support for authorizing a device, as well as a user
@socketio.on("join")
def on_join(json):
    user = User.query.get(json["id"])
    if user.fitpals_secret != json["fitpals_secret"]:
        emit("unauthorized", user.dict_repr())
    room = str(user.id)
    join_room(room)
    emit("joined_room",{"room":room})
