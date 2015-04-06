from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api
from flask.ext.socketio import SocketIO, send, emit, join_room, leave_room
from ConfigParser import ConfigParser
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
from controllers.DevicesAPI import *
from controllers.MatchAPI import *
from controllers.MessagesAPI import *
from controllers.PicturesAPI import *
from controllers.SearchSettingsAPI import *
from controllers.FriendsAPI import *
from controllers.UserReportsAPI import *

#import websocket events
from websockets import *

#reset app and database to fresh install
def reset_app():
    from app import db
    db.drop_all()
    db.create_all()

    from app.models import *
    running = Activity("running")
    running_q1 = Question(running, "How far do you want to run?", "kilometer")
    running_q2 = Question(running, "How much time do you want to spend running?", "minute")
    running.questions.append(running_q1)
    running.questions.append(running_q2)
    db.session.add(running)
    db.session.commit()
