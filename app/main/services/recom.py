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


class Recom():

    def __init__(self, *args, **kwargs):
        self.db = pymysql.connect(host=host, user=user, password=psw, database="recommendation")

    def insert_rating(self, data):
        db = self.db
        cursor = db.cursor()
        cursor.executemany(
            '''
            INSERT INTO `rating` 
            (`user_id`, `item_id`, `rating`, `created_at`)
            VALUE (%s, %s, %s, %s)
            ''',
            (data)
        )
        db.commit()
        db.close()

    def insert_item_matrix(self, data):
        db = self.db
        cursor = db.cursor()
        cursor.executemany(
            '''
            INSERT INTO `item_matrix` 
            (`item_1`, `item_2`, `value`)
            VALUE (%s, %s, %s)
            ''',
            (data)
        )
        db.commit()
        db.close()
    
    def select_item_2(self, item_1, limit=10):
        db = self.db
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            '''
            SELECT * FROM item_matrix
            WHERE `item_1` = %s
            ORDER BY `value` DESC
            LIMIT %s 
            ''',
            (item_1, limit)
        )
        result = cursor.fetchall()
        db.close()

        return result

    def select_top_recom(self, start=0, limit=20):
        db = self.db
        db.ping()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            '''
            SELECT `item_1`, COUNT(`item_2`) 
            FROM recommendation.item_matrix
            GROUP BY `item_1`
            ORDER BY COUNT(`item_2`) DESC
            LIMIT %s, %s;
            ''',
            (start, limit)
        )
        result = cursor.fetchall()
        db.close()

        return result