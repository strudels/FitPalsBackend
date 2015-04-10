from __future__ import print_function
from flask import Flask
from flask.ext.admin import Admin
from flask_admin import LoginManager
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api
from flask.ext.socketio import SocketIO, send, emit, join_room, leave_room
from ConfigParser import ConfigParser
from os.path import basename, dirname
import os
import sys

app = Flask(__name__)

conn_str = "postgresql://"
if basename(os.environ.get("_", "")) == "foreman":
    if os.environ.get("DATABASE_URL", None) is not None:
        conn_str = os.environ["DATABASE_URL"]
    else:
        pguser = os.environ.get("FITPALS_PGUSER", "")
        conn_str += pguser
        conn_str += (":" + \
                os.environ.get("FITPALS_PGPASS", "")) if pguser != "" else ""
        conn_str += "@" if pguser != "" else ""
        conn_str += os.environ.get("FITPALS_PGHOST", "localhost")
        conn_str += ":" + os.environ.get("FITPALS_PGPORT", "5432")
        conn_str += "/" + os.environ.get("FITPALS_PGDBNAME", "fitpals")
elif os.environ.get("DATABASE_URL", None) is not None:
    conn_str = os.environ["DATABASE_URL"]
else:
    config = ConfigParser()
    config.read([dirname(__file__) + "/fitpals_api.cfg"])

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
from controllers.FacebookFriendsAPI import *
from controllers.UserReportsAPI import *

#import websocket events
from websockets import *

#import admin panel
from admin import *

login_manager = LoginManager()
login_manager.init_app(app)

#reset app and database to fresh install
def reset_app():
    from app import db
    db.drop_all()
    db.create_all()

    from app.models import *

    activity_info_list = {
        "Walking" : [
            "IcnWalking.png", 
            "IcnWalkingInactive.png", [
                [ "Pace", "minutes", 15, 60 ]]
        ],
        "Running" : [
            "IcnRunning.png", 
            "IcnRunningInactive.png", [
                [ "Distance", "miles", 2, 20 ],
                [ "Pace", "minutes/mile", 6, 10 ]]
        ],
        "Biking" : [
            "IcnBiking.png", 
            "IcnBikingInactive.png", [
                [ "Distance", "miles", 5, 30 ],
                [ "Pace", "miles/hour", 10, 30 ]]
        ]
    }
    for a_name, a_value in activity_info_list.iteritems():
        activity = Activity(a_name, a_value[0], a_value[1])
        for q_value in a_value[2]:
            question = Question(activity, q_value[0], q_value[1], q_value[2], q_value[3])
            activity.questions.append(question)
        db.session.add(activity)
    
    db.session.commit()
