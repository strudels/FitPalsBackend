from sqlalchemy import ForeignKey, DateTime
import geoalchemy2
from geoalchemy2.types import Geography
from geoalchemy2.elements import WKTElement
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property

from app import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    fb_id = db.Column(db.String(2048), unique=True, nullable=False)
    password = db.Column(db.String(2048), unique=True, nullable=False)
    location = db.Column(Geography(geometry_type="POINT",srid=4326))
    about_me = db.Column(db.String(2048))
    primary_picture = db.Column(db.String(2048))
    name = db.Column(db.String(256))
    gender = db.Column(db.String(32))
    secondary_pictures = relationship("SecondaryPicture")
    last_updated =\
        db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    dob = db.Column(db.Integer)
    available = db.Column(db.Boolean, default=False)
    match_decisions = relationship("MatchDecision",
        primaryjoin="User.id==MatchDecision.user_id")
    apn_tokens = relationship("APNToken")
    activity_settings = relationship("ActivitySetting")

    @hybrid_property
    def jabber_id(self):
        return str(id) + "@strudelcakes.sytes.net"

    def register_jabber(self):
        cursor = jabber_db.cursor()
        cursor.callproc("TigAddUserPlainPw", [self.jabber_id,self.fb_id])
        cursor.close()
        jabber_db.commit()

    def unregister_jabber(self):
        cursor = jabber_db.cursor()
        cursor.callproc("TigRemoveUser",[jabber_id])
        cursor.close()
        jabber_db.commit()

    def __init__(self,fb_id,longitude=None,latitude=None,about_me=None,
        primary_picture=None,secondary_pictures=[], dob=None, available=False,
        apn_tokens=[], name=None, gender=None):

        self.fb_id = fb_id
        self.password = fb_id

        if longitude and latitude:
            self.location = WKTElement("POINT(%f %f)"%(longitude,latitude))
        if about_me: self.about_me = about_me
        if primary_picture: self.primary_picture = primary_picture
        self.secondary_pictures = secondary_pictures
        if dob: self.dob = dob
        self.available = available
        self.apn_tokens = apn_tokens
        self.name=name
        self.gender=gender

class SecondaryPicture(db.Model):
    __tablename__ = "secondary_pictures"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship("User",foreign_keys=[user_id])
    picture = db.Column(db.String(2048), nullable=False)

    def __init__(self, user_id, picture):
        self.user_id = user_id
        self.picture = picture

class MatchDecision(db.Model):
    __tablename__ = "match_decisions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship("User",foreign_keys=[user_id])
    decision_user_id = db.Column(db.Integer, ForeignKey("users.id"))
    decision_user = relationship("User",foreign_keys=[decision_user_id])
    liked = db.Column(db.Boolean, index=True, nullable=False)

    def __init__(self, user, liked):
        self.user = user

class APNToken(db.Model):
    __tablename__ = "apn_tokens"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship("User",foreign_keys=[user_id])
    token = db.Column(db.String(2048), nullable=False)

    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token

class Activity(db.Model):
    __tablename__ = "activities"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    questions = relationship("Question")

    def __init__(self, name, questions=[]):
        self.name = name
        self.questions = questions

class ActivitySetting(db.Model):
    __tablename__ = "activity_settings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship("User",foreign_keys=[user_id])
    activity_id = db.Column(db.Integer, ForeignKey("activities.id"))
    activity = relationship("Activity", foreign_keys=[activity_id])
    question_id = db.Column(db.Integer, ForeignKey("activity_questions.id"))
    question = relationship("Question", foreign_keys=[question_id])
    answer = db.Column(db.Float)

    def __init__(self, user, activity ,question, answer=None):
        self.user = user
        self.activity = activity
        self.question = question
        if self.answer: self.answer = answer

class Question(db.Model):
    __tablename__ = "activity_questions"
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, ForeignKey("activities.id"))
    activity = relationship("Activity", foreign_keys=[activity_id])
    question = db.Column(db.String(2048), nullable=False)

    def __init__(self, activity, question_string):
        self.question = question_string
        self.activity = activity
