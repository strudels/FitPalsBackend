from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api

from models import User

it_works = User(0, 1, 1)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] =\
    "postgresql://fitpals:Bb0ffline!@192.168.1.12/fitpals_db"
api = Api(app)
db = SQLAlchemy(app)
