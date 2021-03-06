from sqlalchemy import ForeignKey, DateTime, UniqueConstraint, CheckConstraint, event, desc
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
    available = db.Column(db.Boolean, default=True)
    friends_only = db.Column(db.Boolean)
    men = db.Column(db.Boolean)
    women = db.Column(db.Boolean)
    age_lower_limit = db.Column(db.Integer, default=18)
    #oldest person to ever live was 122, 130 should be good enough...
    # http://en.wikipedia.org/wiki/Oldest_people
    age_upper_limit = db.Column(db.Integer, default=85)
    _ureg = UnitRegistry()
    #radius with default value of 1 mile
    radius_converted = db.Column(db.Float,
                                 default=(_ureg.mile * 1)\
                                 .to(_ureg.meter).magnitude)
    radius_unit = db.Column(db.String, default="mile")
    __table_args__ = (CheckConstraint("age_lower_limit < age_upper_limit"),
                      CheckConstraint("age_lower_limit >= 18"),
                      CheckConstraint("age_lower_limit <= 85"),)

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
    
    def __init__(self,user,available=True,radius=5,radius_unit="mile",activity=None,
                 friends_only=False,men=True,
                 women=True,age_lower_limit=18,age_upper_limit=85):
        self.user = user
        self.available = available
        self.friends_only = friends_only
        self.men = men
        self.women = women
        self.age_lower_limit = age_lower_limit
        self.age_upper_limit = age_upper_limit
        self.radius_unit = radius_unit
        self.radius = radius
        
    def dict_repr(self):
        return {
            "id":self.id,
            "user_id":self.user_id,
            "available":self.available,
            "friends_only":self.friends_only,
            "men":self.men,
            "women":self.women,
            "age_lower_limit":self.age_lower_limit,
            "age_upper_limit":self.age_upper_limit,
            "radius_unit":self.radius_unit,
            "radius":self.radius
        }

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    fb_id = db.Column(db.String, unique=True, nullable=False)
    fitpals_secret = db.Column(db.String, unique=True, nullable=False)
    location = db.Column(Geography(geometry_type="POINT",srid=4326))
    search_settings = relationship("SearchSettings",
                                  uselist=False,
                                  backref="parent",
                                  cascade="save-update, merge, delete")
    about_me = db.Column(db.String)
    name = db.Column(db.String)
    gender = db.Column(db.String(6),nullable=False)
    pictures = relationship("Picture", lazy="dynamic",
                            cascade="save-update, merge, delete")
    dob = db.Column(db.Date,nullable=False)
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
    blocks = relationship("UserBlock",
        primaryjoin="User.id==UserBlock.user_id", lazy="dynamic",
        cascade="save-update, merge, delete")
    
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
        if socketio.rooms=={} or not str(self.id) in socketio.rooms[""]:
            is_online = False
        else:
            room = socketio.rooms[""][str(self.id)]
            is_online = reduce(
                (lambda x,ns:
                 x if x else ns in [s.active_ns[""] for s in socketio.server.sockets.values()]),
                [ns for ns in room],
                False
            )
        return is_online
        
    @hybrid_property
    def primary_picture(self):
        pic = self.pictures.order_by(Picture.ui_index).first()
        return pic.dict_repr() if pic else None
        
    @validates("gender")
    def validate_gender(self, key, gender):
        assert gender == "male" or gender == "female"
        return gender

    def __init__(self,fb_id,fitpals_secret,gender,longitude=None,latitude=None,
                 about_me=None, dob=None, available=False, name=None):
        self.fb_id = fb_id
        self.fitpals_secret = fitpals_secret
        if longitude!=None and latitude!=None:
            self.location = WKTElement("POINT(%f %f)"%(longitude,latitude))
        self.search_settings = SearchSettings(self)
        if about_me: self.about_me = about_me
        if dob != None: self.dob = dob
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
            "name":self.name,
            "gender":self.gender,
            "primary_picture":self.primary_picture
        }
        if show_online_status:
            dict_repr["online"] = self.online
        if not public:
            dict_repr["online"] = self.online
            dict_repr["fitpals_secret"] = self.fitpals_secret
        return dict_repr
       
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
    owner_user_id = db.Column(db.Integer, ForeignKey("users.id"))
    owner_user = relationship("User",foreign_keys=[owner_user_id])
    reported_user_id = db.Column(db.Integer, ForeignKey("users.id"))
    reported_user = relationship("User",foreign_keys=[reported_user_id])
    reason = db.Column(db.String)
    reviewed = db.Column(db.Boolean, default=False, nullable=False)
    
    def __init__(self,owner_user,reported_user,reason):
        self.owner_user = owner_user
        self.reported_user = reported_user
        self.reason = reason
        
    def dict_repr(self):
        return {
            "id":self.id,
            "owner_user_id":self.owner_user_id,
            "reported_user_id":self.reported_user_id,
            "reason":self.reason,
            "reviewed":self.reviewed
        }
        
class UserBlock(db.Model):
    __tablename__ = "user_blocks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship("User",foreign_keys=[user_id])
    blocked_user_id = db.Column(db.Integer, ForeignKey("users.id"))
    blocked_user = relationship("User",foreign_keys=[blocked_user_id])
    block_time =\
        db.Column(db.DateTime, default=db.func.now(), nullable=False)
    #unblock_time will be enforced to be >= block_time via controller
    unblock_time = db.Column(db.DateTime, default=None, nullable=True)

    @hybrid_property
    def block_time_epoch(self):
        return int((self.block_time - datetime(1970,1,1)).total_seconds())

    @hybrid_property
    def unblock_time_epoch(self):
        if self.unblock_time:
            return int((self.unblock_time - datetime(1970,1,1)).total_seconds())
        else: return None
    
    def __init__(self, user, blocked_user):
        self.user = user
        self.blocked_user = blocked_user
        
    def dict_repr(self):
        return {
            "id":self.id,
            "user_id":self.user_id,
            "blocked_user_id":self.blocked_user_id,
            "block_time":self.block_time_epoch,
            "unblock_time":self.unblock_time_epoch
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
    uri = db.Column(db.String, nullable=False)
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
    user_id = db.Column(db.Integer, ForeignKey("users.id"),nullable=False)
    user = relationship("User",foreign_keys=[user_id])
    matched_user_id = db.Column(db.Integer, ForeignKey("users.id"),nullable=False)
    matched_user = relationship("User",foreign_keys=[matched_user_id])
    liked = db.Column(db.Boolean, index=True, nullable=False)
    time =\
        db.Column(db.DateTime, default=db.func.now(), nullable=False)
    read = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (CheckConstraint("user_id != matched_user_id"),)

    @hybrid_property
    def epoch(self):
        return int((self.time - datetime(1970,1,1)).total_seconds())

    def __init__(self, user, matched_user,liked=False):
        self.user = user
        self.matched_user = matched_user
        self.liked = liked

    def dict_repr(self):
        return {
            "id":self.id,
            "user_id":self.user_id,
            "matched_user_id":self.matched_user_id,
            "matched_user":self.matched_user.dict_repr(),
            "liked":self.liked,
            "time":self.epoch,
            "read":self.read
        }

class Device(db.Model):
    __tablename__ = "devices"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    user = relationship("User",foreign_keys=[user_id])
    token = db.Column(db.String, nullable=False)
    
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
    name = db.Column(db.String, nullable=False)
    questions = relationship("Question", lazy="dynamic",
        cascade="save-update, merge, delete")
    active_image = db.Column(db.String, nullable=True)
    inactive_image = db.Column(db.String, nullable=True)

    def __init__(self, name, active_image=None, inactive_image=None):
        self.name = name
        self.active_image = active_image
        self.inactive_image = inactive_image

    def dict_repr(self):
        return {
            "id":self.id,
            "name":self.name,
            "active_image":self.active_image,
            "inactive_image":self.inactive_image,
        }
        
    def __repr__(self):
        return "<Activity id=%d name=%s>" % (self.id,self.name)

class Question(db.Model):
    __tablename__ = "activity_questions"
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, ForeignKey("activities.id"))
    activity = relationship("Activity", foreign_keys=[activity_id])
    question = db.Column(db.String, nullable=False)
    unit_type = db.Column(db.String, nullable=False)
    min_value = db.Column(db.Float, nullable=False)
    max_value = db.Column(db.Float, nullable=False)
    _ureg = UnitRegistry()
    
    __table_args__ = (CheckConstraint("min_value <= max_value"),)

    @validates("unit_type")
    def validate_unit_type(self, key, value):
        test = self._ureg.parse_expression(value)
        return value
        
    def __init__(self, activity, question_string, unit_type, min_value, max_value):
        self.question = question_string
        self.activity = activity
        self.unit_type = unit_type
        self.min_value = min_value
        self.max_value = max_value

    def dict_repr(self):
        return {
            "id":self.id,
            "activity_id":self.activity_id,
            "question":self.question,
            "unit_type": self.unit_type,
            "min_value": self.min_value,
            "max_value": self.max_value,
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
    unit_type = db.Column(db.String, nullable=False)
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
        
    @validates("lower_value_converted","upper_value_converted")
    def validate_value_converted(self, key, value):
        assert self.question.min_value <= value <= self.question.max_value
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
    body = db.Column(db.String, index=True, nullable=False)
    time =\
        db.Column(db.DateTime, default=db.func.now(), nullable=False)
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
    user1_delete_time =\
        db.Column(db.DateTime, default=None, nullable=True)
    user1_has_unread =\
        db.Column(db.Boolean, nullable=False, default=False)
    user2_id = db.Column(db.Integer, ForeignKey("users.id"))
    user2 = relationship("User",foreign_keys=[user2_id])
    user2_delete_time =\
        db.Column(db.DateTime, default=None, nullable=True)
    user2_has_unread =\
        db.Column(db.Boolean, nullable=False, default=False)

    #POST /message_threads will have to enforce that user2 cannot make a new
    # thread in which user1 and user2 are swapped.
    __table_args__ = (UniqueConstraint("user1_id","user2_id"),)
    
    def __init__(self, user1, user2):
        self.user1 = user1
        self.user2 = user2
        
    @hybrid_property
    def last_message(self):
        message = self.messages.order_by(desc(Message.time)).first()
        return message.dict_repr() if message else None
        
    def dict_repr(self):
        return {
            "id":self.id,
            "user1_id":self.user1_id,
            "user1":self.user1.dict_repr(),
            "user2_id":self.user2_id,
            "user2":self.user2.dict_repr(),
            "last_message":self.last_message,
            "user1_has_unread":self.user1_has_unread,
            "user2_has_unread":self.user2_has_unread
        }

"""
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
"""
