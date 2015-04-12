from __future__ import print_function
from flask import Flask
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, DataError
from flask.ext.restful import Api
from flask.ext.socketio import SocketIO, send, emit, join_room, leave_room
from ConfigParser import ConfigParser
from os.path import basename, dirname
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

#setup log handler
log_handler = RotatingFileHandler("fitpals_api.log",maxBytes=10000,backupCount=1)
log_handler.setLevel(logging.INFO)
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

#class for overriding ModelView methods to make ModelView Work
class ActivityView(ModelView):
    def create_model(self,form):
        try:
            activity = Activity(name=form.data['name'])
            self.session.add(activity)
            self.session.commit()
        except:
            self.session.rollback()
            return False
        return True
        
    def update_model(self, form, model):
        try:
            model.name = form.data['name']
            self.session.commit()
        except:
            self.session.rollback()
            return False
        return True
        
    def delete_model(self,model):
        try:
            self.on_model_delete(model)
            self.session.flush()
            self.session.delete(model)
            self.session.commit()
        except:
            self.session.rollback()
            return False
        return True
        
class QuestionView(ModelView):
    def create_model(self, form):
        try:
            question = Question(form.data["activity"],
                                form.data["question"],
                                form.data["unit_type"],
                                form.data["min_value"],
                                form.data["max_value"])
            self.session.add(question)
            self.session.commit()
        except:
            self.session.rollback()
            return False
        return True
        
    def update_model(self,form,model):
        try:
            model.question = form.data["question"]
            model.unit_type = form.data["unit_type"]
            self.session.commit()
        except:
            self.session.rollback()
            return Flase
        return True
        
    def delete_model(self,model):
        try:
            self.on_model_delete(model)
            self.session.flush()
            self.session.delete(model)
            self.session.commit()
        except:
            self.session.rollback()
            return False
        return True

admin = Admin(app)
admin.add_view(ActivityView(Activity, db.session))
admin.add_view(QuestionView(Question, db.session))

#import websocket events
from websockets import *

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
