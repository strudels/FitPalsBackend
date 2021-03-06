from __future__ import print_function
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, DataError
from flask.ext.restful import Api
from flask.ext.socketio import SocketIO, send, emit, join_room, leave_room
from ConfigParser import ConfigParser
from os.path import basename, dirname
import os
import sys
import logging
from logging import Formatter
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

#setup log handler
log_handler = RotatingFileHandler("fitpals_api.log",maxBytes=10000,backupCount=1)
log_handler.setLevel(logging.INFO)
log_handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(log_handler)

config = ConfigParser()
config.read([dirname(__file__) + "/fitpals_api.cfg"])

#determines if an exception is from entering invalid data into database
def exception_is_validation_error(e):
    return type(e) == IntegrityError or\
        type(e) == AssertionError or\
        type(e) == DataError

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

    conn_str += config.get("postgres","username")
    conn_str += ":" + config.get("postgres","password")
    conn_str += "@" + config.get("postgres","hostname")
    conn_str += ":" + config.get("postgres","port")
    conn_str += "/" + config.get("postgres","dbname")
app.config["SQLALCHEMY_DATABASE_URI"] = conn_str

app.config["SECRET_KEY"] = "091afb3da7dfc6ef76b6d384b1a21e7790c89e79f2558ee04e7d6ed69f33f2b1"

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
from controllers.UserBlockAPI import *

#import websocket events
from websockets import *

#init login manager for admin panel
from admin import init_login
init_login()

#reset app and database to fresh install
def reset_app():
    from app import db
    from admin import AdminUser
    db.drop_all()
    db.create_all()

    from app.models import Activity, Question

    #add default activities
    activity_info_list = {
        "Walking" : [
            "IcnWalking.png", 
            "IcnWalkingInactive.png", [
                [ "Time", "minutes", 15, 60 ]]
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
        
    #add admin user, so that admin access panel can be accessed
    admin_user = AdminUser("admin","password")
    db.session.add(admin_user)
    
    db.session.commit()
