from flask import (make_response, render_template, abort)
from flask_restful import Resource, reqparse

class Main_page(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

    def post(self):
        pass
    
    #@rate_limit_ip
    def get(self):
        return make_response(render_template("main.html"), 200)

class All_page(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

    def post(self):
        pass
    
    #@rate_limit_ip
    def get(self):
        return make_response(render_template("product_list.html"), 200)

class Men_page(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

    def post(self):
        pass
    
    #@rate_limit_ip
    def get(self):
        return make_response(render_template("product_list.html"), 200)

class Women_page(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

    def post(self):
        pass
    
    #@rate_limit_ip
    def get(self):
        return make_response(render_template("product_list.html"), 200)

class Acc_page(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

    def post(self):
        pass

    #@rate_limit_ip
    def get(self):
        return make_response(render_template("product_list.html"), 200)

class Recom_page(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

    def post(self):
        pass
    
    #@rate_limit_ip
    def get(self):
        return make_response(render_template("product_recom.html"), 200)


class Dashboard_page(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

    def post(self):
        pass

    #@rate_limit_ip
    def get(self):
        return make_response(render_template("dashboard.html"), 200)
