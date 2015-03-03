from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api
from flask.ext.socketio import SocketIO, send, emit, join_room, leave_room
from ConfigParser import ConfigParser
import MySQLdb as mysql
from os.path import dirname
from pyapns import configure, provision, notify

config = ConfigParser()
config.read([dirname(__file__) + "/fitpals_api.cfg"])

app = Flask(__name__)

conn_str = "postgresql://"
conn_str += config.get("postgres","username")
conn_str += ":" + config.get("postgres","password")
conn_str += "@" + config.get("postgres","hostname")
conn_str += ":" + config.get("postgres","port")
conn_str += "/" + config.get("postgres","dbname")
app.config["SQLALCHEMY_DATABASE_URI"] = conn_str

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

#import websocket events
from websockets import *
