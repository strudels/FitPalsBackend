from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api
from ConfigParser import ConfigParser
import MySQLdb as mysql
from os.path import dirname

config = ConfigParser()
config.read([dirname(__file__) + "/fitpals_api.cfg"])

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] =\
    "postgresql://fitpals:Bb0ffline!@192.168.1.12/fitpals_db"

api = Api(app)

db = SQLAlchemy(app)

jabber_db = mysql.connect(
    host=config.get("tigase","hostname"),
    user=config.get("tigase","username"),
    passwd=config.get("tigase","password"),
    db=config.get("tigase","dbname"),
    port=config.getint("tigase","port")
)

from models import *
from controllers import *
