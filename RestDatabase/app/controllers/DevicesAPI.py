from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from app import db, api
from app.models import *
from app.utils.Response import Response

@api.resource("/devices")
class DevicesAPI(Resource):
    #add a device
    def post(self):
        """
        Post new device

        :reqheader Authorization: facebook token

        :form int user_id: Id of user.
        :form str token: device token to be posted

        :status 400: Could not register device.
        :status 401: Not Authorized.
        :status 404: User not found.
        :status 200: Device already registered.
        :status 201: Device registered.
        """

        parser = reqparse.RequestParser()
        parser.add_argument("user_id",
            type=int, location="form", required=True)
        parser.add_argument("token",
            type=str, location="form", required=True)
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()

        #get user from database
        user = User.query.get(args.user_id)
        if not user:
            return Response(status=404,
                message="User not found.").__dict__,404
            
        if user.fb_id != args.Authorization:
            return Response(status=401,
                message="Not Authorized.").__dict__, 401
            
        device = Device.query.filter(Device.token==args.token).first()
        if device:
            return Response(status=200, message="Device already registered.",
                            value=device.dict_repr()).__dict__, 200

        try:
            new_device = Device(user, args.token)
            user.devices.append(new_device)
            db.session.commit()
        except: return Response(status=400, message="Could not register device.")\
            .__dict__,400

        return Response(status=201, message="Device registered.",
                        value=new_device.dict_repr()).__dict__,201

@api.resource("/devices/<int:device_id>")
class DeviceAPI(Resource):
    #delete a specific device
    def delete(self, device_id):
        """
        Delete device

        :reqheader Authorization: facebook token

        :status 400: Could not delete device.
        :status 401: Not Authorized.
        :status 404: Device not found.
        :status 200: Device deleted.
        """

        parser = reqparse.RequestParser()
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()

        #get specific token to delete
        device = Device.query.get(device_id)
        if not device:
            return Response(status=404,
                message="Device not found.").__dict__,404

        #get user from database
        if not device.user.fb_id == args.Authorization:
            return Response(status=401,
                message="Not Authorized.").__dict__,401
            
        try:
            device.user.devices.remove(device)
            db.session.delete(device)
            db.session.commit()
        except:
            return Response(status=400, 
                message="Could not delete device.").__dict__,400

        return Response(status=200,
            message="Device deleted.").__dict__,200
