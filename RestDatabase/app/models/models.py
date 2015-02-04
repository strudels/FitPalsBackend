from sqlalchemy import ForeignKey, DateTime
from geoalchemy2.types import Geography
from geoalchemy2.elements import WKTElement
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref
import app
print "model: ", dir(app)

"""
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] =\
    "postgresql://fitpals:Bb0ffline!@192.168.1.12/fitpals_db"
db = SQLAlchemy(app)
"""

"""
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    fb_id = db.Column(db.String(2048), unique=True, nullable=False)
    password = db.Column(db.String(2048), unique=True, nullable=False)
    location = db.Column(Geography(geometry_type="POINT",srid=4326))
    about_me = db.Column(db.String(2048))
    primary_picture = db.Column(db.String(2048))
    secondary_pictures = relationship("SecondaryPicture")
    last_updated =\
        db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    dob = db.Column(db.Integer)
    available = db.Column(db.Boolean, default=False)
    jabber_id = db.Column(db.String(2048), unique=True, nullable=False)
    approved_users = relationship("ApprovedUser")
    denied_users = relationship("DeniedUser")
    apn_tokens = relationship("APNToken")
    activities = relationship("Activity")

    def __init__(self,fb_id,longitude=None,latitude=None,about_me=None,
        primary_picture=None,secondary_pictures=[], dob=None, available=False,
        approved_users=[],denied_users=None, apn_tokens=None,activities=None):

        self.fb_id = fb_id
        self.password = fb_id
        self.jabber_id = self.id + "@strudelcakes.sytes.net"

        if longitude and latitude:
            self.location = WKTElement("POINT(%f %f)"%(longitude,latitude))
        if about_me: self.about_me = about_me
        if primary_picture: self.primary_picture = primary_picture
        self.secondary_pictures = secondary_pictures
        if dob: self.dob = dob
        self.available = available
        self.approved_users = approved_users
        self.denied_users = denied_users
        self.apn_tokens = apn_tokens
        self.activities = activities


class SecondaryPicture(db.Model):
    __tablename__ = "secondary_pictures"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    picture = db.Column(db.String(2048), nullable=False)

    def __init__(self, user_id, picture):
        self.user_id = user_id
        self.picture = picture

class ApprovedUser(db.Model):
    __tablename__ = "approved_users"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    approved_user_id = db.Column(db.Integer,
        ForeignKey("users.id"), nullable=False)

    def __init__(self, user_id, approved_user_id):
        self.user_id = user_id
        self.approved_user_id = approved_user_id

class DeniedUser(db.Model):
    __tablename__ = "denied_users"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    Denied_user_id = db.Column(db.Integer,
        ForeignKey("users.id"), nullable=False)

    def __init__(self, user_id, denied_user_id):
        self.user_id = user_id
        self.denied_user_id = denied_user_id

class APNToken(db.Model):
    __tablename__ = "apn_tokens"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    token = db.Column(db.String(2048), nullable=False)

    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token

class Activity(db.Model):
    __tablename__ = "activities"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    name = db.Column(db.Enum("running", "walking", "biking", "strolling",
        name="activity_names"))
    miles = db.Column(db.Float)
    seconds = db.Column(db.Integer)

    def __init__(self, user_id, name, miles=None, seconds=None):
        self.user_id = user_id
        self.name = name
        if miles: self.miles = miles
        if seconds: self.seconds = seconds
"""
