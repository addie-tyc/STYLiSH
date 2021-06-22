import pymysql
from dotenv import load_dotenv
from flask import request, make_response
import pymysql
import jwt

import pytz
from datetime import datetime, timedelta
import os

load_dotenv()

user = os.getenv("SQL_USER")
psw = os.getenv("SQL_PSW")
host = os.getenv("SQL_HOST")
jwt_key = os.getenv("JWT_SECRET_KEY")
jwt_alg = os.getenv("JWT_ALGORITHM")


class User():

    def __init__(self, *args, **kwargs):
        self.db = pymysql.connect(host=host, user=user, password=psw, database="stylish")

    def encode_jwt(self, email, user_info):
        """
        Generates the JWT
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
                'iat': datetime.datetime.utcnow(),
                'sub': email,
                "user_info": user_info
            }
            return jwt.encode(
                payload,
                jwt_key,
                algorithm=jwt_alg
            )
        except Exception as e:
            return e

    def decode_jwt(self, auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, jwt_key, [jwt_alg])
            return payload["user_info"]
        except jwt.ExpiredSignatureError:
            return make_response("Signature expired. Please log in again.", 403)
        except jwt.InvalidTokenError:
            return make_response("Invalid token. Please log in again.", 403)

    def insert_user(self, args):
        db = self.db
        cursor = db.cursor()
        cursor.execute('''INSERT INTO `user`
                          (provider, name, email, password, picture)
                          VALUE (%s, %s, %s, %s, %s);''', 
                          (args["provider"], args["name"], args["email"], args["password"], args["picture"])
                      )

        # cursor.execute('''INSERT INTO `user`
        #                   (provider, name, email, password, picture)
        #                   VALUE ("facebook", "Addie", "addie@gmail.com", "not_a_password", "nopicture");''')
                                   
        db.commit()

    def select_user_condition(self, field, value):
        db = self.db
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute('''SELECT id, provider, name, email, password, picture
                            FROM user
                           WHERE {} = %s;'''.format(field), (value)
                           )
        result = cursor.fetchone()
        return result