from flask.ext.restful import Resource, reqparse, Api
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from datetime import date

from app import db, api
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
        :status 404: fb_id not found.
        :status 201: User report created.
        """
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str,location="headers",required=True)
        parser.add_argument("owner_fb_id",
            type=str,location="form",required=True)
        parser.add_argument("reported_fb_id",
            type=str,location="form",required=True)
        parser.add_argument("reason",
            type=str,location="form",required=True)
        args = parser.parse_args()
        
        #get owner from db
        owner = User.query.filter(User.fb_id==args.owner_fb_id).first()
        if not owner:
            return Response(status=404,message="fb_id not found.").__dict__,404
            
        #ensure owner is authorized
        if owner.fb_secret != args.Authorization:
            return Response(status=401,message="Not Authorized.").__dict__,401
            
        #get reported_user from db
        reported_user = User.query.filter(User.fb_id==args.reported_fb_id).first()
        if not reported_user:
            return Response(status=404,message="fb_id not found.").__dict__,404
            
        #create new UserReport
        try:
            user_report = UserReport(args.owner_fb_id,
                                     args.reported_fb_id,args.reason)
            db.session.add(user_report)
            db.session.commit()
        except:
            db.session.rollback()
            return Response(status=500,
                message="Internal error. Changes not committed.").__dict__,500
        
        return Response(status=201, message="User report created.",
                        value=user_report.dict_repr()).__dict__,201
