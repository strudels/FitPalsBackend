from sqlalchemy import ForeignKey, DateTime, UniqueConstraint, CheckConstraint
import geoalchemy2
from geoalchemy2.types import Geography
from geoalchemy2.elements import WKTElement
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref, validates
from sqlalchemy.ext.hybrid import hybrid_property

from app import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    fb_id = db.Column(db.String(2048), unique=True, nullable=False)
    location = db.Column(Geography(geometry_type="POINT",srid=4326))
    about_me = db.Column(db.String(2048))
    name = db.Column(db.String(256))
    gender = db.Column(db.String(32))
    pictures = relationship("Picture", lazy="dynamic",
                            cascade="save-update, merge, delete")
    last_updated =\
        db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    dob = db.Column(db.Integer)
    available = db.Column(db.Boolean, default=False)
    match_decisions = relationship("MatchDecision",
        primaryjoin="User.id==MatchDecision.user_id", lazy="dynamic",
        cascade="save-update, merge, delete")
    devices = relationship("Device", lazy="dynamic",
        cascade="save-update, merge, delete")
    activity_settings = relationship("ActivitySetting", lazy="dynamic",
        cascade="save-update, merge, delete")

    @hybrid_property
    def password(self):
        return self.fb_id

    def __init__(self,fb_id,longitude=None,latitude=None,about_me=None,
        dob=None, available=False, name=None, gender=None):
        self.fb_id = fb_id
        if longitude and latitude:
            self.location = WKTElement("POINT(%f %f)"%(longitude,latitude))
        if about_me: self.about_me = about_me
        if dob: self.dob = dob
        self.available = available
        self.name=name
        self.gender=gender

    def dict_repr(self,public=True):
        dict_repr = {
            "id":self.id,
            "about_me":self.about_me,
            "dob":self.dob,
            "available":self.available,
            "name":self.name,
            "gender":self.gender
        }
        if not public:
            dict_repr["fb_id"] = self.fb_id
            dict_repr["password"] = self.password
        return dict_repr


class Picture(db.Model):
    __tablename__ = "pictures"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship("User",foreign_keys=[user_id])
    uri = db.Column(db.String(2048), nullable=False)
    ui_index = db.Column(db.Integer)
    top = db.Column(db.Float, nullable=False)
    bottom = db.Column(db.Float, nullable=False)
    left = db.Column(db.Float, nullable=False)
    right = db.Column(db.Float, nullable=False)
    
    __table_args__ = (UniqueConstraint("user_id","ui_index"),
                      UniqueConstraint("user_id","uri"))

    #ensure that top bottom left and right are all between 0.0 and 1.0
    @validates("top","bottom","left","right")
    def validate_top(self, key, value):
        assert 0.0 <= value <= 1.0
        return value
        
    @validates("ui_index")
    def validate_ui_index(self, key, ui_index):
        assert 0 <= ui_index <= 6
        return ui_index
        
    def __init__(self, user, uri, ui_index, top, bottom, left, right):
        self.user = user
        self.uri = uri
        self.ui_index = ui_index
        self.top = top
        self.bottom = bottom
        self.left = left 
        self.right = right 

    def dict_repr(self):
        return {
            "id":self.id,
            "user_id":self.user_id,
            "uri":self.uri,
            "ui_index":self.ui_index,
            "top":self.top,
            "bottom":self.bottom,
            "left":self.left,
            "right":self.right,
        }

class MatchDecision(db.Model):
    __tablename__ = "match_decisions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship("User",foreign_keys=[user_id])
    decision_user_id = db.Column(db.Integer, ForeignKey("users.id"))
    decision_user = relationship("User",foreign_keys=[decision_user_id])
    liked = db.Column(db.Boolean, index=True, nullable=False)

    def __init__(self, user, decision_user,liked=False):
        self.user = user
        self.decision_user = decision_user
        self.liked = liked

    def dict_repr(self):
        return {
            "id":self.id,
            "user_id":self.user_id,
            "decision_user_id":self.decision_user_id,
            "liked":self.liked
        }

class Device(db.Model):
    __tablename__ = "devices"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship("User",foreign_keys=[user_id])
    token = db.Column(db.String(2048), nullable=False)

    UniqueConstraint('user_id','token')

    def __init__(self, user, token):
        self.user = user
        self.token = token

    def dict_repr(self):
        return {
            "id":self.id,
            "user_id":self.user_id,
            "token":self.token
        }

class Activity(db.Model):
    __tablename__ = "activities"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    questions = relationship("Question", lazy="dynamic",
        cascade="save-update, merge, delete")

    def __init__(self, name):
        self.name = name

    def dict_repr(self):
        return {
            "id":self.id,
            "name":self.name,
            "questions":[q.dict_repr() for q in self.questions]
        }

class ActivitySetting(db.Model):
    __tablename__ = "activity_settings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship("User",foreign_keys=[user_id])
    question_id = db.Column(db.Integer, ForeignKey("activity_questions.id"))
    question = relationship("Question", foreign_keys=[question_id])
    lower_value = db.Column(db.Float)
    upper_value = db.Column(db.Float)
    
    __table_args__ = (CheckConstraint("lower_value <= upper_value"),)

    def __init__(self, user, question, lower_value=None, upper_value=None):
        self.user = user
        self.question = question
        self.lower_value = lower_value
        self.upper_value = upper_value

    def dict_repr(self):
        return {
            "id":self.id,
            "user_id":self.user_id,
            "question_id":self.question_id,
            "lower_value":self.lower_value,
            "upper_value":self.upper_value
        }

class Question(db.Model):
    __tablename__ = "activity_questions"
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, ForeignKey("activities.id"))
    activity = relationship("Activity", foreign_keys=[activity_id])
    question = db.Column(db.String(2048), nullable=False)

    def __init__(self, activity, question_string):
        self.question = question_string
        self.activity = activity

    def dict_repr(self):
        return {
            "id":self.id,
            "activity_id":self.activity_id,
            "question":self.question
        }

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    # 0 for user1->user2, 1 for user2->user1
    direction = db.Column(db.Boolean, nullable=False)
    body = db.Column(db.String(9900), index=True, nullable=False)
    time =\
        db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    message_thread_id = db.Column(db.Integer, ForeignKey("message_threads.id"))
    message_thread =\
        relationship("MessageThread",foreign_keys=[message_thread_id])

    def __init__(self, message_thread, direction, body):
        self.message_thread = message_thread
        self.direction = direction
        self.body = body

    def dict_repr(self):
        return {
            "id":self.id,
            "direction":self.direction,
            "body":self.body,
            "time":self.time,
            "message_thread_id":self.message_thread_id
        }

class MessageThread(db.Model):
    __tablename__ = "message_threads"
    id = db.Column(db.Integer, primary_key=True)
    messages = relationship("Message", lazy="dynamic",
        cascade="save-update, merge, delete")
    user1_id = db.Column(db.Integer, ForeignKey("users.id"))
    user1 = relationship("User",foreign_keys=[user1_id])
    user1_deleted = db.Column(db.Boolean, default=False)
    user2_id = db.Column(db.Integer, ForeignKey("users.id"))
    user2 = relationship("User",foreign_keys=[user2_id])
    user2_deleted = db.Column(db.Boolean, default=False)
    
    def __init__(self, user1, user2):
        self.user1 = user1
        self.user2 = user2
        
    def dict_repr(self):
        return {
            "id":self.id,
            "user1_id":self.user1_id,
            "user2_id":self.user2_id,
        }
