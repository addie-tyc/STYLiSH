from werkzeug.datastructures import FileStorage
import boto3
from flask import (Flask, request, make_response, render_template, abort,
                   flash, redirect, url_for, jsonify)
from flask_restful import Resource, reqparse
import pymysql
import redis

import math
import os
import json

from app.main.services.product import Product
from app.main.services.recom import Recom


class Products_recom_parents(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

    def post(self):
        pass

    def get(self):

        db = Product()
        result = db.select_product_condition("category", "parent")
        data = {"data": result}
        return make_response(jsonify(data), 200)

class Products_recom_info(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

    def post(self):
        pass

    #@rate_limit_ip
    def get(self, id=0):
        id = request.args.get('id')
        if not request.args.get('id'):
            return abort(400)

        try:
            r = redis.Redis(host="127.0.0.1", port=6379)
            result = json.loads(r.get(id))
            item_id_lst = []
            result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))
            for k in result:
                if len(item_id_lst) < 3:
                    item_id_lst.append(k)
        except:
            db = Recom()
            item_id_dict = db.select_item_2(id, limit=3)
            item_id_lst = []
            for item_2_dict in item_id_dict:
                item_id_lst.append(item_2_dict["item_2"])
                
        while len(item_id_lst) < 3:
            item_id_lst.append("A")

        db = Product()
        result = [db.select_self(id)]
        recom = db.select_recom(item_id_lst=item_id_lst)
        for info in recom:
            result.append(info) 

        data = {"data": result}
        return make_response(jsonify(data), 200)