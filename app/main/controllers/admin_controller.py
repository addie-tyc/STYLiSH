from werkzeug.datastructures import FileStorage
import boto3
from flask import (Flask, request, make_response, render_template, abort,
                   flash, redirect, url_for, session, jsonify)
from flask_restful import Resource, reqparse
import pymysql

import os
from app.main.services.admin import Admin

aws_access_key = os.getenv("AWS_ACCESS_KEY")
aws_secret_key = os.getenv("AWS_SECRET_KEY")

class Product(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()

        self.reqparse.add_argument("title", required=True, 
                                   help="No title provided")

        self.reqparse.add_argument("description", required=True, 
                                   help="No description provided")

        self.reqparse.add_argument("price", required=True, 
                                   help="No price provided")

        self.reqparse.add_argument("texture", required=False)

        self.reqparse.add_argument("wash", required=False)

        self.reqparse.add_argument("place", required=False)

        self.reqparse.add_argument("note", required=False)

        self.reqparse.add_argument("story", required=False)

        self.reqparse.add_argument("category", required=True,
                                   help="No category provided")
        
        self.reqparse.add_argument("main_image", required=True, type=FileStorage,
                                   help="No main_image provided", location="files")
                                
        self.reqparse.add_argument("images", required=True, type=FileStorage,
                                   location="files", action="append")

    def post(self):
        args = self.reqparse.parse_args()

        s3 = boto3.resource('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
        s3_bucket = s3.Bucket("aws-bucket-addie")

        # make main_image's path
        root_path = os.path.dirname(os.path.abspath(__file__)) # get current path
        upload_folder = os.path.join(root_path, "static", "uploads") # gen upload path
        file = args['main_image']
        filename = args["title"]+ "_image_main" +".jpg"
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        main_image_key_name = f"stylish_img/{args['title']}_main_image.jpg"
        s3_bucket.upload_file(filepath, main_image_key_name, ExtraArgs={'ContentType': 'image/png', 'ACL':'public-read'})
        main_image_url = "https://aws-bucket-addie.s3.amazonaws.com/" + main_image_key_name
        args["main_image"] = main_image_url

        # sql_path = os.path.join("static", "uploads", filename)
        # args['main_image'] = sql_path

        # make images' path
        for i in ["image_1", "image_2", "image_3", "image_4"]:
            args[i] = None
        if len(args["images"]) == 0:
            pass
        else:
            for i in range(len(args["images"])):
                args["image_"+str(i+1)] = args["images"][i]
                file = args["image_"+str(i+1)]
                filename = args["title"]+ "_image_" + str(i+1) +".jpg"
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)

                image_key_name = f"stylish_img/{args['title']}_image_{str(i)}.jpg"
                s3_bucket.upload_file(filepath, image_key_name, ExtraArgs={'ContentType': 'image/png', 'ACL':'public-read'})
                image_url = "https://aws-bucket-addie.s3.amazonaws.com/" + image_key_name
                args['image'+str(i+1)]= image_url

                # sql_path = os.path.join("static", "uploads", filename)
                # args["image_"+str(i+1)] = sql_path


        # insert products
        try:
            db = Admin()
            db.insert_product(args)
            flash("Please enter vairants information", "success")
            session["title"] = args["title"]
            return redirect(url_for("admin.variant"))
        except pymysql.IntegrityError:
            flash("Product with that name already exists!", "error")

        return redirect(url_for("admin.product"))


    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('product.html'), 200, headers)


class Variant(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        
        self.reqparse.add_argument("variants-count", required=False)
        
        args = self.reqparse.parse_args()
        if args["variants-count"]:
            for i in range(int(args["variants-count"])):
                self.reqparse.add_argument("color-code-{}".format(str(i)), required=True, 
                                        help = "No color provided")

                self.reqparse.add_argument("color-name-{}".format(str(i)), required=True, 
                                        help = "No color name provided")

                self.reqparse.add_argument("variant-sizes-s-{}".format(str(i)), required=True, 
                                        help = "No stock provided")

                self.reqparse.add_argument("variant-sizes-m-{}".format(str(i)), required=True, 
                                        help = "No stock provided")

                self.reqparse.add_argument("variant-sizes-l-{}".format(str(i)), required=True, 
                                        help = "No stock provided")

    def post(self):
        args = self.reqparse.parse_args()
        db = Admin()
        product_id = db.select_product_id(session["title"])
        try:
            for i in range(int(args["variants-count"])):
                args["code"] = args["color-code-{}".format(str(i))]
                args["name"] = args["color-name-{}".format(str(i))]
                args["S"] = args["variant-sizes-s-{}".format(str(i))]
                args["M"] = args["variant-sizes-m-{}".format(str(i))]
                args["L"] = args["variant-sizes-l-{}".format(str(i))]
                
                # insert colors
                try:
                    db.insert_color(args)
                except:
                    pass

                # insert product_color
                color_id = db.select_color_id(args)
                db.insert_product_color(product_id, color_id)
                
                # insert variant
                for size in ["S", "M", "L"]:
                    if args[size]:
                        db.insert_variant(product_id, color_id, size, args[size])
            flash("The product has been added!", "success")
            session["title"] = None
            return redirect(url_for("admin.product"))
        except:
            flash("Something went wrong, please try again!", "error")
            return redirect(url_for("admin.variant"))

    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('variant.html'), 200, headers)