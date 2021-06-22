import pymysql
from dotenv import load_dotenv
from flask import request

import pytz
from datetime import datetime, timedelta
import os

load_dotenv()

user = os.getenv("SQL_USER")
psw = os.getenv("SQL_PSW")
host = os.getenv("SQL_HOST")

class Admin():
    def __init__(self, *args, **kwargs):
        self.db = pymysql.connect(host=host, user=user, password=psw, database="stylish")

    def insert_product(self, args):
        db = self.db
        cursor = db.cursor()
        cursor.execute('''INSERT INTO product
                          (title, description, price, texture,
                           wash, place, note, story, main_image, 
                           image_1, image_2, image_3, image_4, category)
                          VALUES(%s,%s,%s,%s,%s,
                                 %s,%s,%s,%s,%s,
                                 %s,%s,%s,%s)''',
                      ( args["title"], args["description"], args["price"], 
                        args["texture"], args["wash"], args["place"], args["note"], 
                        args["story"], args["main_image"], args["image_1"], 
                        args["image_2"], args["image_3"], args["image_4"], args["category"])
                      )
        db.commit()

    def select_product_id(self, title):
        db = self.db
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute('''SELECT id FROM product
                           WHERE title = %s''',
                      (title)
                      )
        return cursor.fetchone()["id"]

    def insert_variant(self, product_id, color_id, size, stock):
        db = self.db
        cursor = db.cursor()
        cursor.execute('''INSERT INTO variant
                          (product_id, color_id, size, stock) 
                          VALUES(%s,%s,%s,%s)''',
                          (product_id, color_id, size, stock)
                      )
        db.commit()

    def insert_color(self, args):
        db = self.db
        cursor = db.cursor()
        cursor.execute('''INSERT INTO color
                          (code, name) VALUES(%s,%s)''',
                      (args["code"], args["name"])
                      )
        db.commit()

    def select_color_id(self, args):
        db = self.db
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute('''SELECT color_id FROM color
                           WHERE code = %s''',
                      (args["code"])
                      )
        return cursor.fetchone()["color_id"]

    def insert_product_color(self, product_id, color_id):
        db = self.db
        cursor = db.cursor()
        cursor.execute('''INSERT INTO product_color
                          (product_id, color_id) VALUES(%s,%s)''',
                      (product_id, color_id)
                      )
        db.commit()
    
    def select_product_all(self):
        db = self.db
        if request.args.get('paging'):
            paging = int(request.args.get('paging'))
        else:
            paging = 0

        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute('''SELECT id, title, `description`, price, texture, wash, place, note, story, main_image
                            FROM product;'''
                           )
        all = len(cursor.fetchall())

        cursor.execute('''SELECT id, title, `description`, price, texture, wash, place, note, story, main_image
                            FROM product
                           LIMIT %s, %s;''', (paging*6, 6)
                           )
        result = cursor.fetchall()
        # for i in range(len(result)):
        #     result[i]["main_image"] = request.url_root + result[i]["main_image"]
        
        # modify images 
        # for i in range(len(result)):
        #     id = result[i]["id"]
        #     cursor.execute('''SELECT image_1, image_2, image_3, image_4
        #                         FROM product
        #                        WHERE id = %s;''', (id)
        #                    )                  
        #     images = cursor.fetchone() # a dict
        #     lst_images = []
        #     for k in images:
        #         if images[k]:
        #             lst_images.append(request.url_root + images[k])
        #     result[i]["images"] = lst_images
        
        #modify colors
        for i in range(len(result)):
            id = result[i]["id"]
            cursor.execute('''SELECT DISTINCT(color_code), color_name
                                FROM product
                               INNER JOIN variant ON variant.product_id = product.id
                               WHERE product.id = %s;''', (id))
            colors = cursor.fetchall()
            result[i]["colors"] = colors
        
        #modify sizes
        for i in range(len(result)):
            id = result[i]["id"]
            cursor.execute('''SELECT DISTINCT(variant.`size`)
                                FROM product
                               INNER JOIN variant ON product.id = variant.product_id
                               WHERE product.id = %s;''', (id))
            sizes = cursor.fetchall()
            lst_sizes = []
            for j in range(len(sizes)):
                lst_sizes.append(sizes[j]["size"])
            result[i]["sizes"] = lst_sizes

        # modify variants
        for i in range(len(result)):
            id = result[i]["id"]
            cursor.execute('''SELECT variant.`color_code`, variant.`size`, variant.`stock`
                                FROM product
                               INNER JOIN variant ON product.id = variant.product_id
                               WHERE product.id = %s;''', (id))
                               # INNER JOIN color ON color.color_id = variant.color_id
            variants = cursor.fetchall()
            result[i]["variants"] = variants

        return all, result
    
    def select_product_condition(self, field, condition):
        db = self.db
        if request.args.get('paging'):
            paging = int(request.args.get('paging'))
        else:
            paging = 0

        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute('''SELECT id, title, `description`, price, texture, wash, place, note, story, main_image
                            FROM product
                           WHERE {} = %s;'''.format(field), (condition)
                           )
        all = len(cursor.fetchall())

        cursor.execute('''SELECT id, title, `description`, price, texture, wash, place, note, story, main_image
                            FROM product
                           WHERE {} = %s
                           LIMIT %s, %s;'''.format(field), (condition, paging*6, 6)
                           )
        result = cursor.fetchall()
        # for i in range(len(result)):
        #     result[i]["main_image"] = request.url_root + result[i]["main_image"]
        
        # modify images 
        # for i in range(len(result)):
        #     id = result[i]["id"]
        #     cursor.execute('''SELECT image_1, image_2, image_3, image_4
        #                         FROM product
        #                        WHERE id = %s AND {} = %s;'''.format(field), (id, condition)
        #                    )                  
        #     images = cursor.fetchone() # a dict
        #     lst_images = []
        #     for k in images:
        #         if images[k]:
        #             lst_images.append(request.url_root + images[k])
        #     result[i]["images"] = lst_images
        
        #modify colors
        for i in range(len(result)):
            id = result[i]["id"]
            cursor.execute('''SELECT DISTINCT(color_code), color_name
                                FROM product
                               INNER JOIN variant ON variant.product_id = product.id
                               WHERE product.id = %s AND {} = %s;'''.format(field), (id, condition))
            colors = cursor.fetchall()
            result[i]["colors"] = colors

        #modify sizes
        for i in range(len(result)):
            id = result[i]["id"]
            cursor.execute('''SELECT DISTINCT(variant.`size`)
                                FROM product
                               INNER JOIN variant ON product.id = variant.product_id
                               WHERE product.id = %s AND {} = %s;'''.format(field), (id, condition))
            sizes = cursor.fetchall()
            lst_sizes = []
            for j in range(len(sizes)):
                lst_sizes.append(sizes[j]["size"])
            result[i]["sizes"] = lst_sizes

        # modify variants
        for i in range(len(result)):
            id = result[i]["id"]
            cursor.execute('''SELECT variant.`color_code`, variant.`size`, variant.`stock`
                                FROM product
                               INNER JOIN variant ON product.id = variant.product_id
                               WHERE product.id = %s AND {} = %s;'''.format(field), (id, condition))
            variants = cursor.fetchall()
            result[i]["variants"] = variants

        return all, result

    def select_product_like(self, field, condition):
        db = self.db
        if request.args.get('paging'):
            paging = int(request.args.get('paging'))
        else:
            paging = 0

        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute('''SELECT id, title, `description`, price, texture, wash, place, note, story, main_image
                            FROM product
                           WHERE {} LIKE %s;'''.format(field), (condition)
                           )
        all = len(cursor.fetchall())

        cursor.execute('''SELECT id, title, `description`, price, texture, wash, place, note, story, main_image
                            FROM product
                           WHERE {} LIKE %s
                           LIMIT %s, %s;'''.format(field), (condition, paging*6, 6)
                           )
        result = cursor.fetchall()
        for i in range(len(result)):
            result[i]["main_image"] = request.url_root + result[i]["main_image"]
        
        # modify images 
        for i in range(len(result)):
            id = result[i]["id"]
            cursor.execute('''SELECT image_1, image_2, image_3, image_4
                                FROM product
                               WHERE id = %s AND {} LIKE %s;'''.format(field), (id, condition)
                           )                  
            images = cursor.fetchone() # a dict
            lst_images = []
            for k in images:
                if images[k]:
                    lst_images.append(request.url_root + images[k])
            result[i]["images"] = lst_images
        
        #modify colors
        for i in range(len(result)):
            id = result[i]["id"]
            cursor.execute('''SELECT color.`code`, color.`name`
                                FROM product
                               INNER JOIN product_color ON product.id = product_color.product_id
                               INNER JOIN color ON color.color_id = product_color.color_id
                               WHERE id = %s AND {} LIKE %s;'''.format(field), (id, condition))
            colors = cursor.fetchall()
            result[i]["colors"] = colors
        
        #modify sizes
        for i in range(len(result)):
            id = result[i]["id"]
            cursor.execute('''SELECT variant.`size`
                                FROM product
                               INNER JOIN variant ON product.id = variant.product_id
                               WHERE id = %s AND {} LIKE %s;'''.format(field), (id, condition))
            sizes = cursor.fetchall()
            lst_sizes = []
            for j in range(len(sizes)):
                lst_sizes.append(sizes[j]["size"])
            result[i]["sizes"] = lst_sizes

        # modify variants
        for i in range(len(result)):
            id = result[i]["id"]
            cursor.execute('''SELECT color.`code` AS "color_code", variant.`size`, variant.`stock`
                                FROM product
                               INNER JOIN variant ON product.id = variant.product_id
                               INNER JOIN color ON color.color_id = variant.color_id
                               WHERE id = %s AND {} LIKE %s;'''.format(field), (id, condition))
            variants = cursor.fetchall()
            result[i]["variants"] = variants

        return all, result