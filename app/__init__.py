from flask import Blueprint, request, make_response, jsonify
from flask_restful import Api
import redis

from app.main.controllers.admin_controller import Product, Variant
from app.main.controllers.product_controller import (Products_all, Products_men, Products_women,
                                                    Products_accessories, Products_search, Products_details)
from app.main.controllers.recom_controller import Products_recom_parents, Products_recom_info
from app.main.controllers.user_controller import User_signup, User_signin, User_profile
from app.main.controllers.fb_login_controller import Fb_login, Fb_callback
from app.main.controllers.dashboard_controller import Dashboard_data
from app.main.controllers.page_controller import (Main_page, All_page, Men_page, Women_page, Acc_page,
                                                 Recom_page, Dashboard_page)


# admin
admin_blue = Blueprint("admin", __name__)
api = Api(admin_blue)
api.add_resource(Product, "/product.html")
api.add_resource(Variant, "/variant.html")

# products
products_blue = Blueprint("products", __name__)
api = Api(products_blue)
api.add_resource(Products_all, "/all", "/all")
api.add_resource(Products_women, "/women", "/women")
api.add_resource(Products_men, "/men", "/men")
api.add_resource(Products_accessories, "/accessories", "/accessories")
api.add_resource(Products_search, "/search", "/search")
api.add_resource(Products_details, "/details", "/details")

# recoms
recom_blue = Blueprint("recom", __name__)
api = Api(recom_blue)
api.add_resource(Products_recom_parents, "/recom-parents", "/recom-parents")
api.add_resource(Products_recom_info, "/recom-info", "/recom-info")

# @products_blue.app_errorhandler(404)
# def page_not_found(error):
#     return render_template("404.html"), 400

# user
user_blue = Blueprint("user", __name__)
api = Api(user_blue)
api.add_resource(User_signup, "/signup", "/signup")
api.add_resource(User_signin, "/signin", "/signin")
api.add_resource(User_profile, "/profile", "/profile")

# @user_blue.app_errorhandler(404)
# def page_not_found(error):
#     return render_template("404.html"), 400

# fb
fb_blue = Blueprint("fb", __name__)
api = Api(fb_blue)
api.add_resource(Fb_login, "/fb-login")
api.add_resource(Fb_callback, "/fb-callback")

# dashboard
dashboard_blue = Blueprint("dashboard", __name__)
api = Api(dashboard_blue)
api.add_resource(Dashboard_data, "/data", "/data")

# page
page_blue = Blueprint("page", __name__)
api = Api(page_blue)
api.add_resource(Main_page, "/", "/")
api.add_resource(All_page, "/stylish-all", "/stylish-all")
api.add_resource(Men_page, "/stylish-men", "/stylish-men")
api.add_resource(Women_page, "/stylish-women", "/stylish-women")
api.add_resource(Acc_page, "/stylish-accessories", "/stylish-accessories")
api.add_resource(Recom_page, "/recom", "/recom")
api.add_resource(Dashboard_page, "/dashboard", "/dashboard")


@products_blue.before_request
def rate_limit_beforerequest():
    ip = request.remote_addr
    print(ip)
    r = redis.Redis(host="127.0.0.1", port=6379)
    r.set(ip, 10, ex=1, nx=True)
    r.decr(ip)
    print(r.get(ip))
    if int(r.get(ip)) <= 0:
        data = {"data": {"message": "Too many requests!"}}
        return make_response(jsonify(data), 429)