from flask import Flask
from flask.ext.restful import Resource, reqparse, Api
import simplejson as json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

from app import db, api
from app.models import *
from app.utils.Response import Response

@api.resource("/users/<int:user_id>/pictures")
class PicturesAPI(Resource):
    #get all pictures for user_id
    def get(self, user_id):
        """
        Get all (secondary)pictures for a user.

        :param int user_id: Id of user.

        :status 400: Could not find user.
        :status 200: Pictures found.
        """

        #get user from database
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400,
                message="Could not find user.").__dict__,400

        return Response(status=200, message="Pictures found.",
            value=[p.dict_repr() for p in user.secondary_pictures.all()])\
            .__dict__, 200

    #add a picture for a user
    def post(self, user_id):
        """
        Post new (secondary)picture for a user.

        :reqheader Authorization: fb_id token needed here

        :param int user_id: Id of user.

        :form str picture_id: Facebook Picture Id string.

        :status 401: Not Authorized.
        :status 400: Could not find user.
        :status 201: Picture added.
        """

        parser = reqparse.RequestParser()
        parser.add_argument("picture_id",
            type=str, location="form", required=True)
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()

        #get user from database
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400,
                message="Could not find user.").__dict__,400

        #ensure user is valid by checking if fb_id is correct
        if user.fb_id != args.Authorization:
            return Response(status=401,message="Not Authorized.").__dict__,401

        picture = Picture(user,args.picture_id)
        user.secondary_pictures.append(picture)
        db.session.commit()

        return Response(status=201, message="Picture added.").__dict__,201

    #delete either a single, or all pictures for a user
    def delete(self, user_id):
        """
        Delete (secondary)picture for a user.

        :reqheader Authorization: fb_id token needed here

        :param int user_id: Id of user.

        :form str picture_id: Facebook Picture Id string.

        :status 401: Not Authorized.
        :status 400: "Could not find user" or "Picture not found".
        :status 201: "Picture removed" or "Pictures removed".
        """

        parser = reqparse.RequestParser()
        parser.add_argument("picture_id",
            type=str, location="form", required=False)
        parser.add_argument("Authorization",
            type=str, location="headers", required=True)
        args = parser.parse_args()

        #get user from database
        user = User.query.filter(User.id==user_id).first()
        if not user:
            return Response(status=400,
                message="Could not find user.").__dict__,400

        #remove all pictures if no single picture specified
        if not args.picture_id:
            user.secondary_pictures = []
            db.session.commit()
            return Response(status=200,message="Pictures removed.").__dict__,200

        #ensure user is valid by checking if fb_id is correct
        if user.fb_id != args.Authorization:
            return Response(status=401,message="Not Authorized.").__dict__,401

        #get specified picture to delete
        picture = user.secondary_pictures\
            .filter(Picture.picture==args.picture_id).first()
        if not picture:
            return Response(status=400,
                message="Picture not found.").dict__,400

        #delete picture
        user.secondary_pictures.remove(picture)
        db.session.commit()
        return Response(status=200, message="Picture removed.").__dict__, 200
