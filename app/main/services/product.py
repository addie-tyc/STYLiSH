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

def find_product(category, paging):
    if (category == 'all') :
        return get_products(PAGE_SIZE, paging, {"category": category})
    elif (category in ['men', 'women', 'accessories']):
        return get_products(PAGE_SIZE, paging, {"category": category})
    elif (category == 'search'):
        keyword = request.values["keyword"]
        if (keyword):
            return get_products(PAGE_SIZE, paging, {"keyword": keyword})
    elif (category == 'details'):
        product_id = request.values["id"]
        return get_products(PAGE_SIZE, paging, {"id": product_id})
    elif (category == 'recommend'):
        product_id = request.values["id"]
        return get_products(3, paging, {"recommend": product_id})


class Product():

    def __init__(self, *args, **kwargs):
        self.db = pymysql.connect(host=host, user=user, password=psw, database="stylish")

    def insert_product(self, args):
        db = self.db
        cursor = db.cursor()
        cursor.execute('''INSERT INTO product
                          ( item_id, category, title, description, 
                            price, texture, main_image, created_at)
                          VALUES(%s,%s,%s,%s,
                                 %s,%s,%s,%s)''',
                      ( args["item_id"], args["category"], args["title"], args["description"], 
                        args["price"], args["texture"], args["main_image"], args["created_at"])
                      )
        db.commit()
        db.close()

    def insert_product_update(self, args):
        db = self.db
        cursor = db.cursor()
        cursor.execute('''INSERT INTO product (id, category)
                          (SELECT `id`, `item_id` FROM product WHERE `item_id` = %s)
                          ON DUPLICATE KEY UPDATE `category`= %s;''',
                      ( args["item_id"],  
                        args["category"])
                      )
        db.commit()
        db.close()

    def select_self(self, item_id):
        db = self.db
        db.ping()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            '''
            SELECT `title`, main_image, price
            FROM product
            WHERE `item_id` = %s
            ''',
            (item_id)
        )
        result = cursor.fetchone() # a dict
        db.close()

        return result

    def select_recom(self, item_id_lst, limit=3):
        db = self.db
        db.ping()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            '''
            SELECT `title`, main_image, price
            FROM product
            WHERE `item_id` IN ( %s, %s, %s )
            ''',
            ( item_id_lst[0], item_id_lst[1], item_id_lst[2])
        )
        result = cursor.fetchall() # a list of dicts
        db.close()

        return result

    def select_product_condition(self, field, condition):
        db = self.db
        db.ping()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute('''SELECT `item_id`, `title`
                            FROM product
                           WHERE {} = %s;'''.format(field), (condition)
                           )
        result = cursor.fetchall()
        db.close()
        return result

    def select_min_id_by_time(self):
        db = self.db
        db.ping()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute('''
                       SELECT MAX(`id`)
                         FROM product
                       ''')
        result = cursor.fetchone()
        db.close()
        return result