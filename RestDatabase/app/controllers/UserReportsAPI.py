from flask.ext.restful import Resource, reqparse, Api
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from datetime import date

from app import db, api, app, exception_is_validation_error
from app.models import *
from app.utils.Response import Response

@api.resource("/user_reports")
class UserReportsAPI(Resource):
    def post(self):
        """
        Report User by creating new UserReport.
        
        :reqheader Authorization: facebook secret
        
        :form str owner_fb_id: Facebook id of person sending report
        :form str reported_fb_id: Facebook id of person being reported
        :form str reason: Reason for why person is being reported
        
        :status 401: Not Authorized.
        :status 404: User not found.
        :status 201: User report created.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str,location="headers",required=True)
        parser.add_argument("reported_user_id",
            type=str,location="form",required=True)
        parser.add_argument("reason",
            type=str,location="form",required=True)
        args = parser.parse_args()
        
        try:
            #ensure owner is authorized
            owner = User.query.filter(User.fitpals_secret==args.Authorization).first()
            if not owner:
                return Response(status=401,message="Not Authorized.").__dict__,401

            #get reported_user from db
            reported_user = User.query.get(args.reported_user_id)
            if not reported_user:
                return Response(status=404,message="User not found.").__dict__,404

            #create new UserReport
            user_report = UserReport(owner,reported_user,args.reason)
            db.session.add(user_report)
            db.session.commit()
            return Response(status=201, message="User report created.",
                            value=user_report.dict_repr()).__dict__,201
        except Exception as e:
            app.logger.error(e)
            return Response(status=500, message="Internal server error.").__dict__,500
