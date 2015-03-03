from flask.ext.socketio import emit, join_room
from app.models import *
from app import socketio

#listen for client's to connect to chat websocket
@socketio.on("connect", namespace="/chat")
def connect():
    emit("connected_chat")
    
@socketio.on("join", namespace="/chat")
def on_join(json):
    user = User.query.get(json["id"])
    if user.fb_id != json["fb_id"]:
        emit("unauthorized", user.dict_repr())
    room = str(user.id) + "-chat"
    join_room(room)
    emit("joined_room",{"room":room})

#listen for client's to connect to sync websocket
@socketio.on("connect", namespace="/sync")
def connect():
    emit("connected_sync")
    pass
    
@socketio.on("join", namespace="/sync")
def on_join(json):
    user = User.query.get(json["id"])
    if user.fb_id != json["fb_id"]:
        emit("unauthorized", user.dict_repr())
    room = str(user.id) + "-sync"
    join_room(room)
    emit("joined_room", {"room":room})
