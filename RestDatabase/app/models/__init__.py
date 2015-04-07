from sqlalchemy import ForeignKey, DateTime, UniqueConstraint, CheckConstraint, event
import geoalchemy2
from geoalchemy2.types import Geography
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_X, ST_Y
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref, validates
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from pint import UnitRegistry

from app import db, socketio

class SearchSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship("User",foreign_keys=[user_id])
    activity_id = db.Column(db.Integer,nullable=True)
    friends_only = db.Column(db.Boolean)
    men_only = db.Column(db.Boolean)
    women_only = db.Column(db.Boolean)
    age_lower_limit = db.Column(db.Integer, default=18)
    #oldest person to ever live was 122, 130 should be good enough...
    # http://en.wikipedia.org/wiki/Oldest_people
    age_upper_limit = db.Column(db.Integer, default=130)
    _ureg = UnitRegistry()
    #radius with default value of 1 mile
    radius_converted = db.Column(db.Float,
                                 default=(_ureg.mile * 1)\
                                 .to(_ureg.meter).magnitude)
    radius_unit = db.Column(db.String(64), default="mile")
    __table_args__ = (CheckConstraint("age_lower_limit < age_upper_limit"),)

    @hybrid_property
    def radius(self):
        db_val = self.radius_converted * self._ureg.meter
        return db_val.to(self._ureg.parse_expression(self.radius_unit)).magnitude
        
    @radius.setter
    def radius(self, value):
        value = value * self._ureg.parse_expression(self.radius_unit)
        self.radius_converted = value.to(self._ureg.meter).magnitude
    
    @validates("unit_type")
    def validate_unit_type(self, key, value):
        test_unit = self._ureg.parse_expression(value) * 100
        conversion_test = test_unit.to(self._ureg.meter)
        return value
    
    def __init__(self,user,radius=1,radius_unit="mile",activity=None,
                 friends_only=False,men_only=False,
                 women_only=False,age_lower_limit=18,age_upper_limit=130):
        self.user = user
        self.activity = activity
        self.friends_only = friends_only
        self.men_only = men_only
        self.women_only = women_only
        self.age_lower_limit = age_lower_limit
        self.age_upper_limit = age_upper_limit
        self.radius_unit = radius_unit
        self.radius = radius
        
    def dict_repr(self):
        return {
            "id":self.id,
            "user_id":self.user_id,
            "activity_id":self.activity_id,
            "friends_only":self.friends_only,
            "men_only":self.men_only,
            "women_only":self.women_only,
            "age_lower_limit":self.age_lower_limit,
            "age_upper_limit":self.age_upper_limit,
            "radius_unit":self.radius_unit,
            "radius":self.radius
        }

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    fb_id = db.Column(db.String(2048), unique=True, nullable=False)
    fb_secret = db.Column(db.String(2048), unique=True, nullable=False)
    location = db.Column(Geography(geometry_type="POINT",srid=4326))
    search_settings = relationship("SearchSettings",
                                  uselist=False,
                                  backref="parent",
                                  cascade="save-update, merge, delete")
    about_me = db.Column(db.String(2048))
    name = db.Column(db.String(256))
    gender = db.Column(db.String(32))
    pictures = relationship("Picture", lazy="dynamic",
                            cascade="save-update, merge, delete")
    last_updated =\
        db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    dob = db.Column(db.Date,nullable=False)
    available = db.Column(db.Boolean, default=False)
    friends = relationship("Friend",
        primaryjoin="User.id==Friend.user_id", lazy="dynamic",
        cascade="save-update, merge, delete")
    matches = relationship("Match",
        primaryjoin="User.id==Match.user_id", lazy="dynamic",
        cascade="save-update, merge, delete")
    devices = relationship("Device", lazy="dynamic",
        cascade="save-update, merge, delete")
    activity_settings = relationship("ActivitySetting", lazy="dynamic",
        cascade="save-update, merge, delete")
    
    @hybrid_property
    def password(self):
        return self.fb_secret

    @hybrid_property
    def longitude(self):
        return db.session.query(ST_X(self.location)).first()[0]

    @hybrid_property
    def latitude(self):
        return db.session.query(ST_Y(self.location)).first()[0]
        
    @hybrid_property
    def dob_year(self):
        return self.dob.year

    @hybrid_property
    def dob_month(self):
        return self.dob.month

    @hybrid_property
    def dob_day(self):
        return self.dob.day
    
    @hybrid_property
    def online(self):
        return str(self.id) in socketio.rooms[""] if socketio.rooms!={} else False

    def __init__(self,fb_id,fb_secret,longitude=None,latitude=None,about_me=None,
        dob=None, available=False, name=None, gender=None):
        self.fb_id = fb_id
        self.fb_secret = fb_secret
        if longitude!=None and latitude!=None:
            self.location = WKTElement("POINT(%f %f)"%(longitude,latitude))
        self.search_settings = SearchSettings(self)
        if about_me: self.about_me = about_me
        if dob != None: self.dob = dob
        self.available = available
        self.name=name
        self.gender=gender

    def dict_repr(self,public=True,show_online_status=False):
        dict_repr = {
            "id":self.id,
            "fb_id":self.fb_id,
            "longitude":self.longitude,
            "latitude":self.latitude,
            "search_settings_id":self.search_settings.id,
            "about_me":self.about_me,
            "dob_year":self.dob_year,
            "dob_month":self.dob_month,
            "dob_day":self.dob_day,
            "available":self.available,
            "name":self.name,
            "gender":self.gender
        }
        if show_online_status:
            dict_repr["online"] = self.online
        if not public:
            dict_repr["online"] = self.online
            dict_repr["fb_secret"] = self.fb_secret
            dict_repr["password"] = self.password
        return dict_repr

@event.listens_for(User.__table__, "before_create")
def user_ensure_postgis_extension(mapper, connection, **kwargs):
    connection.execute("CREATE EXTENSION IF NOT EXISTS postgis")

@event.listens_for(User, "before_delete")
def user_message_thread_cascade_delete(mapper, connection, user):
    #delete all message threads where user is thread.user1
    threads = MessageThread.query.filter(MessageThread.user1_id==user.id).all()
    for thread in threads:
        thread.user1_deleted = True
        db.session.commit()

    #delete all message threads where user is thread.user2
    threads = MessageThread.query.filter(MessageThread.user2_id==user.id).all()
    for thread in threads:
        thread.user2_deleted = True
        db.session.commit()

class UserReport(db.Model):
    __tablename__ = "user_reports"
    id = db.Column(db.Integer, primary_key=True)
    owner_fb_id = db.Column(db.String(2048))
    reported_fb_id = db.Column(db.String(2048))
    reason = db.Column(db.String(2048))
    reviewed = db.Column(db.Boolean, default=False, nullable=False)
    
    def __init__(self,owner_fb_id,reported_fb_id,reason):
        self.owner_fb_id = owner_fb_id
        self.reported_fb_id = reported_fb_id
        self.reason = reason
        
    def dict_repr(self):
        return {
            "id":self.id,
            "owner_fb_id":self.owner_fb_id,
            "reported_fb_id":self.reported_fb_id,
            "reason":self.reason,
            "reviewed":self.reviewed
        }
    
class Friend(db.Model):
    __tablename__ = "friends"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship("User",foreign_keys=[user_id])
    friend_user_id = db.Column(db.Integer, ForeignKey("users.id"))
    friend_user = relationship("User",foreign_keys=[friend_user_id])
    
    __table_args__ = (UniqueConstraint("user_id","friend_user_id"),)
    
    def __init__(self, user, friend_user):
        self.user = user
        self.friend_user = friend_user

    def dict_repr(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "friend_user_id": self.friend_user_id
        }

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

class Match(db.Model):
    __tablename__ = "matches"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship("User",foreign_keys=[user_id])
    matched_user_id = db.Column(db.Integer, ForeignKey("users.id"))
    matched_user = relationship("User",foreign_keys=[matched_user_id])
    liked = db.Column(db.Boolean, index=True, nullable=False)

    __table_args__ = (CheckConstraint("user_id != matched_user_id"),)

    def __init__(self, user, matched_user,liked=False):
        self.user = user
        self.matched_user = matched_user
        self.liked = liked

    def dict_repr(self):
        return {
            "id":self.id,
            "user_id":self.user_id,
            "matched_user_id":self.matched_user_id,
            "liked":self.liked
        }

class Device(db.Model):
    __tablename__ = "devices"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship("User",foreign_keys=[user_id])
    token = db.Column(db.String(2048), nullable=False)
    
    __table_args__ = (UniqueConstraint('user_id','token'),)

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

class Question(db.Model):
    __tablename__ = "activity_questions"
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, ForeignKey("activities.id"))
    activity = relationship("Activity", foreign_keys=[activity_id])
    question = db.Column(db.String(2048), nullable=False)
    unit_type = db.Column(db.String(128), nullable=False)
    _ureg = UnitRegistry()

    @validates("unit_type")
    def validate_unit_type(self, key, value):
        test = self._ureg.parse_expression(value)
        return value

    def __init__(self, activity, question_string, unit_type):
        self.question = question_string
        self.activity = activity
        self.unit_type = unit_type

    def dict_repr(self):
        return {
            "id":self.id,
            "activity_id":self.activity_id,
            "question":self.question,
            "unit_type": self.unit_type
        }

class ActivitySetting(db.Model):
    __tablename__ = "activity_settings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship("User",foreign_keys=[user_id])
    question_id = db.Column(db.Integer, ForeignKey("activity_questions.id"))
    question = relationship("Question", foreign_keys=[question_id])
    lower_value_converted = db.Column(db.Float)
    upper_value_converted = db.Column(db.Float)
    unit_type = db.Column(db.String(128), nullable=False)
    _ureg = UnitRegistry()
    
    __table_args__ = (CheckConstraint(
        "lower_value_converted <= upper_value_converted"),)
    
    @hybrid_property
    def lower_value(self):
        db_val = self.lower_value_converted *\
                 self._ureg.parse_expression(self.question.unit_type)
        return db_val.to(self._ureg.parse_expression(self.unit_type)).magnitude

    @lower_value.setter
    def lower_value(self, value):
        value = value * self._ureg.parse_expression(self.unit_type)
        self.lower_value_converted = value.to(self._ureg.parse_expression(
            self.question.unit_type)).magnitude

    @hybrid_property
    def upper_value(self):
        db_val = self.upper_value_converted *\
                 self._ureg.parse_expression(self.question.unit_type)
        return db_val.to(self._ureg.parse_expression(self.unit_type)).magnitude
        
    @upper_value.setter
    def upper_value(self, value):
        value = value * self._ureg.parse_expression(self.unit_type)
        self.upper_value_converted = value.to(self._ureg.parse_expression(
            self.question.unit_type)).magnitude
    
    @validates("unit_type")
    def validate_unit_type(self, key, value):
        test_unit = self._ureg.parse_expression(value) * 100
        conversion_test = test_unit.to(self._ureg.parse_expression(
            self.question.unit_type))
        return value

    def __init__(self,user,question,unit_type,lower_value=None,upper_value=None):
        self.user = user
        self.question = question
        self.unit_type = unit_type
        self.lower_value = lower_value
        self.upper_value = upper_value

    def dict_repr(self):
        return {
            "id":self.id,
            "user_id":self.user_id,
            "question_id":self.question_id,
            "lower_value":self.lower_value,
            "upper_value":self.upper_value,
            "unit_type":self.unit_type
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
    
    @hybrid_property
    def epoch(self):
        return int((self.time - datetime(1970,1,1)).total_seconds())

    def __init__(self, message_thread, direction, body):
        self.message_thread = message_thread
        self.direction = direction
        self.body = body
        
    def dict_repr(self):
        return {
            "id":self.id,
            "direction":self.direction,
            "body":self.body,
            "time":self.epoch,
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

#These 2 events ensure that a MessageThread gets deleted if both it's
# user1_deleted and user2_deleted fields are True
@event.listens_for(MessageThread.user1_deleted, "set")
def message_threads_user1_delete(thread, value, old_value, initiator):
    if thread.user2_deleted:
        db.session.delete(thread)
        db.session.commit()

@event.listens_for(MessageThread.user2_deleted, "set")
def message_threads_user2_delete(thread, value, old_value, initiator):
    if thread.user1_deleted:
        db.session.delete(thread)
        db.session.commit()
