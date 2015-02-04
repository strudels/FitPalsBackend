from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api

from models import *
from controllers import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] =\
    "postgresql://fitpals:Bb0ffline!@192.168.1.12/fitpals_db"
api = Api(app)
db = SQLAlchemy(app)
