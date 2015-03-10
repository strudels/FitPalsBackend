from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
from flask.ext.socketio import emit
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from sqlalchemy import func,or_, and_

from app import db, api, socketio
from app.models import *
from app.utils.Response import Response

@api.resource("/search_settings/<int:setting_id>")
class SearchSettingsAPI(Resourse):
    def put(self, setting_id):
        """
        Create new search_setting.
        
        :form int user_id: Owner user id for search setting.
        :form int activity_id: Activity id.
        :form bool friends_only: Set if user wants friends only
        :form bool men_only: Set if user wants men only
        :form bool women_only: Set if user wants women only
        :form int age_lower_limit: Set if user want lower age limit. Default is 18.
        :form int age_upper_limit: Set if user want upper age limit. Default is 130.
        http://en.wikipedia.org/wiki/Oldest_people
        
        :status 201: SearchSettings created
        """
