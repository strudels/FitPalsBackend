from sqlalchemy import ForeignKey, DateTime
import geoalchemy2
from geoalchemy2.types import Geography
from geoalchemy2.elements import WKTElement
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property

from app import db, jabber_db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    fb_id = db.Column(db.String(2048), unique=True, nullable=False)
    location = db.Column(Geography(geometry_type="POINT",srid=4326))
    about_me = db.Column(db.String(2048))
    primary_picture = db.Column(db.String(2048))
    name = db.Column(db.String(256))
    gender = db.Column(db.String(32))
    secondary_pictures = relationship("Picture", lazy="dynamic")
    last_updated =\
        db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    dob = db.Column(db.Integer)
    available = db.Column(db.Boolean, default=False)
    match_decisions = relationship("MatchDecision",
        primaryjoin="User.id==MatchDecision.user_id", lazy="dynamic")
    apn_tokens = relationship("APNToken", lazy="dynamic")
    activity_settings = relationship("ActivitySetting", lazy="dynamic")

    @hybrid_property
    def jabber_id(self):
        return str(self.id) + "@strudelcakes.sytes.net"

    @hybrid_property
    def password(self):
        return self.fb_id

    def register_jabber(self):
        cursor = jabber_db.cursor()
        cursor.callproc("TigAddUserPlainPw", [self.jabber_id,self.fb_id])
        cursor.close()
        jabber_db.commit()

    def unregister_jabber(self):
        cursor = jabber_db.cursor()
        cursor.callproc("TigRemoveUser",[self.jabber_id])
        cursor.close()
        jabber_db.commit()

    def get_messages(self, other_user):
        cursor = jabber_db.cursor()
        results = cursor.callproc("get_messages",
            [self.jabber_id,other_user.jabber_id])
        results = [r[0] for r in cursor.fetchall()]
        cursor.close()
        return results

    def del_messages(self, other_user):
        cursor = jabber_db.cursor()
        cursor.callproc("delete_messages",
            [self.jabber_id,other_user.jabber_id])
        cursor.close()
        jabber_db.commit()

    def __init__(self,fb_id,longitude=None,latitude=None,about_me=None,
        primary_picture=None,secondary_pictures=[], dob=None, available=False,
        apn_tokens=[], name=None, gender=None):

        self.fb_id = fb_id
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

    def dict_repr(self,public=True):
        dict_repr = {
            "id":self.id,
            "jabber_id":self.jabber_id,
            "about_me":self.about_me,
            "primary_picture":self.primary_picture,
            "secondary_pictures":\
                [p.dict_repr() for p in self.secondary_pictures],
            "dob":self.dob,
            "available":self.available,
            "name":self.name,
            "gender":self.gender
        }
        if not public:
            dict_repr["fb_id"] = self.fb_id
            dict_repr["password"] = self.password
            dict_repr["apn_tokens"] = [t.dict_repr() for t in self.apn_tokens]
        return dict_repr


class Picture(db.Model):
    __tablename__ = "secondary_pictures"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship("User",foreign_keys=[user_id])
    picture = db.Column(db.String(2048), nullable=False)

    def __init__(self, user, picture):
        self.user = user
        self.picture = picture

    def dict_repr(self):
        return {
            "id":self.id,
            "user_id":self.user_id,
            "picture":self.picture
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

class APNToken(db.Model):
    __tablename__ = "apn_tokens"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship("User",foreign_keys=[user_id])
    token = db.Column(db.String(2048), nullable=False)

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
    questions = relationship("Question", lazy="dynamic")

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
    activity_id = db.Column(db.Integer, ForeignKey("activities.id"))
    activity = relationship("Activity", foreign_keys=[activity_id])
    question_id = db.Column(db.Integer, ForeignKey("activity_questions.id"))
    question = relationship("Question", foreign_keys=[question_id])
    answer = db.Column(db.Float)

    def __init__(self, user, activity ,question, answer=None):
        self.user = user
        self.activity = activity
        self.question = question
        self.answer = answer

    def dict_repr(self):
        return {
            "id":self.id,
            "user_id":self.user_id,
            "activity_id":self.activity_id,
            "question_id":self.question_id,
            "question":self.question.question,
            "answer":self.answer
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
