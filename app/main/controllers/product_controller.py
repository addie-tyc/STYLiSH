from werkzeug.datastructures import FileStorage
from flask import (Flask, request, make_response, render_template, abort,
                   flash, redirect, url_for, jsonify)
from flask_restful import Resource, reqparse
import pymysql

import math
import os

from app.main.services.admin import Admin
from app.main.services.product import Product


class Products_all(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

    def post(self):
        pass
    
    #@rate_limit_ip
    def get(self, paging=0):
        if request.args.get('paging'):
            paging = int(request.args.get('paging'))
        else:
            paging = 0
        db = Admin()
        all, result = db.select_product_all()
        max_paging = int(math.ceil(all/6))-1
        if paging > max_paging:
            return abort(400)
        elif paging == max_paging:
            data = {"data": result}
        else:
            data = {"data": result, "next_paging": paging+1}
        return make_response(jsonify(data), 200)


class Products_men(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

    def post(self):
        pass
    
    #@rate_limit_ip
    def get(self, paging=0):
        if request.args.get('paging'):
            paging = int(request.args.get('paging'))
        else:
            paging = 0
        db = Admin()
        all, result = db.select_product_condition("category", "men")
        max_paging = int(math.ceil(all/6))-1
        if paging > max_paging:
            return abort(400)
        elif paging == max_paging:
            data = {"data": result}
        else:
            data = {"data": result, "next_paging": paging+1}
        return make_response(jsonify(data), 200)


class Products_women(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

    def post(self):
        pass
    
    #@rate_limit_ip
    def get(self, paging=0):
        if request.args.get('paging'):
            paging = int(request.args.get('paging'))
        else:
            paging = 0
        db = Admin()
        all, result = db.select_product_condition("category", "women")
        max_paging = int(math.ceil(all/6))-1
        if paging > max_paging:
            return abort(400)
        elif paging == max_paging:
            data = {"data": result}
        else:
            data = {"data": result, "next_paging": paging+1}
        return make_response(jsonify(data), 200)


class Products_accessories(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

    def post(self):
        pass

    #@rate_limit_ip
    def get(self, paging=0):
        if request.args.get('paging'):
            paging = int(request.args.get('paging'))

        db = Admin()
        all, result = db.select_product_condition("category", "accessories")
        max_paging = int(math.ceil(all/6))-1
        if paging > max_paging:
            return abort(400)
        elif paging == max_paging:
            data = {"data": result}
        else:
            data = {"data": result, "next_paging": paging+1}
        return make_response(jsonify(data), 200)

class Products_search(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

    def post(self):
        pass

    def get(self, paging=0, keyword=""):
        keyword = request.args.get('keyword')
        if request.args.get('paging'):
            paging = int(request.args.get('paging'))

        db = Admin()
        all, result = db.select_product_like("title", "%{}%".format(keyword))
        max_paging = int(math.ceil(all/6))-1
        if paging > max_paging:
            return abort(400)
        elif paging == max_paging:
            data = {"data": result}
        else:
            data = {"data": result, "next_paging": paging+1}
        return make_response(jsonify(data), 200)

class Products_details(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

    def post(self):
        pass

    def get(self, id=0):
        id = request.args.get('id')
        if not request.args.get('id'):
            return abort(400)

        db = Admin()
        all, result = db.select_product_condition("id", id)
        try:
            result = result[0] # result is a list of dict, so get index 0
        except:
            abort(400)
        data = {"data": result}
        return make_response(jsonify(data), 200)