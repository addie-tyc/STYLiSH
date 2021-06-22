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


class Dashboard():

    def __init__(self, *args, **kwargs):
        self.db = pymysql.connect(host=host, user=user, password=psw, database="mongodb")
    
    def insert_many(self, data):
        db = self.db
        cursor = db.cursor()
        cursor.executemany('''INSERT INTO `app91`
                          (mongo_id, client_id, event_type, created_at, 
                           key1, value1, key2, value2, key3, value3, key4, value4, key5, value5)
                           VALUE (%s, %s, %s, %s, 
                                  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);''', 
                          data )
        db.commit()
        db.close()

    def select_last(self):
        db = self.db
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute('''SELECT `mongo_id`, `created_at` FROM `app91` ORDER BY `created_at` DESC LIMIT 1;''')
        result = cursor.fetchone()
        db.close()
        return str(result["mongo_id"]), str(result["created_at"])


    def insert_daily_agg(self):
        '''
        Use to insert agg. info at 00:01 everyday
        '''
        db = self.db
        cursor = db.cursor()
        #today = str(datetime.now(pytz.utc).date())
        last_day = str(datetime.now(pytz.utc).date()-timedelta(days=1))
        before_last_day = str(datetime.now(pytz.utc).date()-timedelta(days=2)) # us time
        cursor.execute(
            '''
            INSERT INTO daily_agg (
            `id`,
            `date`,
            `all_user_count`,
            `active_user_count`,
            `new_user_count`,
            `return_user_count`,
            `view_count`,
            `view_item_count`,
            `add_to_cart_count`,
            `checkout_count`)
            SELECT (SELECT `id`+1 FROM daily_agg WHERE `date`= %s),
                `date`, 
                `all_user_count`, 
                `active_user_count`,
                `new_user_count`,
                `return_user_count`,
                `view_count`,
                `view_item_count`,
                `add_to_cart_count`,
                `checkout_count`
            FROM temp
            WHERE `date` = %s
            ORDER BY temp.id DESC LIMIT 1
            ON DUPLICATE KEY UPDATE `all_user_count`=temp.`all_user_count`,
							 `active_user_count`=temp.`active_user_count`,
                             `new_user_count`=temp.`new_user_count`,
                             `return_user_count`=temp.`return_user_count`,
                             `view_count`=temp.`view_count`,
						     `view_item_count`=temp.`view_item_count`,
							 `add_to_cart_count`=temp.`add_to_cart_count`,
							 `checkout_count`=temp.`checkout_count`;
            ''',
            (before_last_day, last_day)
            # (last_day, today)
        )
        db.commit()
        cursor.execute("DELETE FROM temp;")
        db.commit()
        db.close()

    def insert_temp(self):
        db = self.db
        cursor = db.cursor()
        today = str(datetime.now(pytz.utc).date()) # us time
        cursor.execute(
            '''
            INSERT INTO temp (
            `date`,
            `all_user_count`,
            `active_user_count`,
            `new_user_count`,
            `return_user_count`,
            `view_count`,
            `view_item_count`,
            `add_to_cart_count`,
            `checkout_count`)
            (
            WITH alluser AS (
                SELECT MAX(DATE(app91.`created_at`)) AS `date`, COUNT(DISTINCT(`client_id`)) AS `allUser` 
                FROM app91
                WHERE DATE(app91.`created_at`) <= %s
            ),
            appuser AS (
                WITH activeuser AS
                ( SELECT DATE(`created_at`) AS `date`, COUNT(DISTINCT(`client_id`)) AS `numActive` 
                    FROM app91
                    WHERE DATE(`created_at`) = %s
                    GROUP BY DATE(`created_at`)),
                newuser AS 
                ( SELECT `joinDate`, COUNT(`client_id`) AS `numNew`
                    FROM (		
                            SELECT MIN(DATE(`created_at`)) AS `joinDate`, `client_id`
                            FROM app91
                            GROUP BY `client_id`
                            ) temp
                WHERE DATE(`joinDate`) = %s
                GROUP BY `joinDate`)
                SELECT DATE(`created_at`) AS `date`, `numActive` AS `activeUser`, `numNew` AS `newUser`, (`numActive` - `numNew`) AS `returnUser`
                FROM app91
                LEFT JOIN activeuser
                    ON DATE(app91.`created_at`) = activeuser.`date`
                LEFT JOIN newuser
                    ON DATE(app91.`created_at`) = newuser.`joinDate`
                WHERE DATE(app91.`created_at`) = %s
                GROUP BY DATE(app91.`created_at`)
            ),
            eventcount AS (
                SELECT DATE(created_at) AS `date`,
                    SUM(CASE WHEN event_type = "view" THEN 1 END) `view_count`,
                    SUM(CASE WHEN event_type = "view_item" THEN 1 END) `view_item_count`,
                    SUM(CASE WHEN event_type = "add_to_cart" THEN 1 END) `add_to_cart_count`,
                    SUM(CASE WHEN event_type = "checkout_progress" AND value1 = 3 THEN 1 END) `checkout_count`
                    FROM app91
                WHERE DATE(created_at) = %s
                GROUP BY DATE(created_at)
            )
            SELECT MAX(DATE(`created_at`)), 
                alluser.`allUser` AS `allUSer`, 
                appuser.`activeUser` AS `activeUser`,
                appuser.`newUser` AS `newUser`,
                appuser.`returnUser` AS `returnUser`,
                eventcount.`view_count` AS `view`,
                eventcount.`view_item_count` AS `view_item`,
                eventcount.`add_to_cart_count` AS `add_to_cart`,
                eventcount.`checkout_count` AS `checkout`
            FROM app91
            LEFT JOIN alluser
                ON DATE(app91.`created_at`) = alluser.`date`
            LEFT JOIN appuser
                ON DATE(app91.`created_at`) = appuser.`date`
            LEFT JOIN eventcount
                ON DATE(app91.`created_at`) = eventcount.`date`
            WHERE DATE(app91.`created_at`) = %s);
            ''',
            (today, today, today, today, today, today)
            )
        db.commit()

    def select_lastest_agg(self, date):
        db = self.db
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            '''
            SELECT * FROM daily_agg
             WHERE `date` = %s
            ''',
            (date)
        )
        result = cursor.fetchone()
        return result

    def select_lastest_temp(self, date):
        db = self.db
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            '''
            SELECT * 
              FROM temp
             WHERE `date` = %s
             ORDER BY temp.id DESC LIMIT 1;
            ''',
            (date)
        )
        result = cursor.fetchone()
        return result

    def select_last_id(self, last_day, today):
        db = self.db
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            '''
            SELECT MAX(CAST(client_id AS UNSIGNED)) AS last_id FROM app91 
             WHERE created_at BETWEEN %s AND %s;
            ''',
            (last_day, today)
            )
        result = cursor.fetchone()
        return result