from werkzeug.datastructures import FileStorage
from flask import (Flask, request, make_response, render_template, abort,
                   flash, redirect, url_for, jsonify)
from flask_restful import Resource, reqparse
import pymysql

import math
import os
from datetime import datetime
import pytz

from app.main.services.dashboard import Dashboard


class Dashboard_data(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        self.reqparse.add_argument("datetime")

    def post(self):
        pass
    
    #@rate_limit_ip
    def get(self, date="0"):

        if request.args.get('date'):
            date = request.args.get('date')
        else:
            abort(400)

        today = str(datetime.now(pytz.utc).date())
        if date == today:
            db = Dashboard()
            fetch = db.select_lastest_temp(date) 
        else:
            db = Dashboard()
            fetch = db.select_lastest_agg(date)

        try:
            data = {"behavior_count": [fetch["view_count"], fetch["view_item_count"], 
                                       fetch["add_to_cart_count"], fetch["checkout_count"]],
                    "user_count": [fetch["all_user_count"], fetch["active_user_count"],
                                   fetch["new_user_count"], fetch["return_user_count"]]}
        except TypeError:
            data = {"behavior_count": [0, 0, 0, 0],
                    "user_count": [0, 0, 0, 0]}
    

        return make_response(jsonify(data), 200)