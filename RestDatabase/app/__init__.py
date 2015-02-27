from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api
from flask.ext.socketio import SocketIO
from ConfigParser import ConfigParser
import MySQLdb as mysql
from os.path import dirname
from pyapns import configure, provision, notify

config = ConfigParser()
config.read([dirname(__file__) + "/fitpals_api.cfg"])

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] =\
    "postgresql://fitpals:Bb0ffline!@192.168.1.12/fitpals_db"
socketio = SocketIO(app)

api = Api(app)

db = SQLAlchemy(app)

jabber_db = mysql.connect(
    host=config.get("tigase","hostname"),
    user=config.get("tigase","username"),
    passwd=config.get("tigase","password"),
    db=config.get("tigase","dbname"),
    port=config.getint("tigase","port")
)

"""
#setup apple push notifications
configure({"HOST": "http://localhost:7077/"})
provision("uhsome.Fitpals", open("certs/apns_cert.pem").read(), "sandbox")
"""

#import all models
from models import *

#import all controllers
from controllers.UserAPI import *
from controllers.ActivityAPI import *
from controllers.APNTokensAPI import *
from controllers.MatchAPI import *
from controllers.MessagesAPI import *
from controllers.PicturesAPI import *

#listen for client's to connect to chat websocket
@socketio.on("connect", namespace="/chat")
def connect(json):
    pass
    
@socketio.on("join", namespace="/chat")
def on_join(json):
    user = User.query.get(json["id"])
    if user.fb_id != json["fb_id"]:
        emit("unauthorized", user.dict_repr())
    join_room(str(user.id) + "-chat")

#listen for client's to connect to sync websocket
@socketio.on("connect", namespace="/sync")
def connect(json):
    pass
    
@socketio.on("join", namespace="/sync")
def on_join(json):
    user = User.query.get(json["id"])
    if user.fb_id != json["fb_id"]:
        emit("unauthorized", user.dict_repr())
    join_room(str(user.id) + "-sync")
