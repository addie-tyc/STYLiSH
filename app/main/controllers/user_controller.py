from werkzeug.datastructures import FileStorage
from flask import (Flask, request, make_response, render_template, abort,
                   flash, redirect, url_for, jsonify)
from flask_restful import Resource, reqparse
import pymysql
from flask_bcrypt import generate_password_hash, check_password_hash

import requests
import math
import os
from datetime import datetime
import pytz

from app.main.services.user import User



class User_signup(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
    
    def post(self):
        args = request.json
        user = User()

        try:
            args["provider"]
        except KeyError:
            args["provider"] = "native"

        try:
            args["picture"]
        except KeyError:
            args["picture"] = None

        args["password"] = generate_password_hash(args["password"])
        
        #insert user
        try:
            user.insert_user(args)
        except pymysql.IntegrityError:
            return make_response("This email has been used.", 403)

        # gen response data
        user_info = user.select_user_condition("email", args["email"])
        user_info.pop("password")
        access_token = user.encode_jwt(args["email"], user_info)
        access_expired = 3600
        result = {"data": {"access_token": access_token, 
                           "access_expired": access_expired,
                           "user": user_info}}
        return make_response(jsonify(result), 200)

    def get(self):
        pass

class User_signin(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
    
    def post(self):
        args = request.json

        if args["provider"] == "native":
            user = User()
            user_info = user.select_user_condition("email", args["email"])
            if user_info:
                if check_password_hash(user_info["password"], args["password"]):
                    user_info.pop("password")
                    token = user.encode_jwt(args["email"], user_info)
                    access_expired = 3600
                    result = {"data": {"access_token": token, 
                                       "access_expired": access_expired,
                                       "user": user_info}}
                    return make_response(jsonify(result), 200)
                else:
                    return make_response("Sign in failed.", 403)
            else:
                    return make_response("Sign in failed.", 403)

        elif args["provider"] == "facebook":
            user = User()
            token = args["access_token"]
            profile = requests.get('''https://graph.facebook.com/me?fields=id,name,email,picture
                     &access_token={}'''.format(token)).json()
            try:
                profile["id"]
            except:
                return make_response("Sign in failed.", 403)
                
            profile["picture"] = profile["picture"]["data"]["url"]
            profile["password"] = None
            profile["provider"] = "facebook"

            try:
                user.insert_user(profile)
            except pymysql.IntegrityError:
                pass

            user_info = user.select_user_condition("email", profile["email"])
            if user_info:
                user_info.pop("password")
                token = user.encode_jwt(profile["email"], user_info)
                access_expired = 3600
                result = {"data": {"access_token": token, 
                                   "access_expired": access_expired,
                                   "user": user_info}}
                return make_response(jsonify(result), 200)
        
        else:
            return make_response("Sign in failed.", 403)

    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('login.html'), 200, headers)

class User_profile(Resource):
    # decorators = [jwt_required()]
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

    def post(self):
        pass
        
    def get(self):
        user = User()
        try:
            token = dict(request.headers)["Authorization"].replace("Bearer ", "")
        except KeyError:
            return make_response("No JSON Web Token provided.", 401)
            
        msg = user.decode_jwt(token) # it's an user_info dict if pass the check
        if type(msg) == dict:
            msg.pop("id")
            result = {"data": msg}
            return make_response(jsonify(result), 200)
        else:
            return msg