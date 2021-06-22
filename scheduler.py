from apscheduler.schedulers.blocking import BlockingScheduler
from pymongo import MongoClient
from dotenv import load_dotenv

import csv
import os
from datetime import datetime, timedelta
import pytz
import random

import mock_data
import models

load_dotenv()

user = os.getenv("MONGO_USER")
psw = os.getenv("MONGO_PSW")
host = os.getenv("MONGO_HOST")

# ---- connect db ----
uri = "mongodb://{user}:{psw}@{host}:27017".format(user=user, psw=psw, host=host)
client = MongoClient(uri)
db = client["mockData"]
db_coll = db["event"]


sched = BlockingScheduler({'apscheduler.timezone': 'UTC'})
sched.add_job(mock_data.gen_mock_data, "interval", seconds=4)
sched.add_job(mock_data.query_clean_new, "interval", seconds=3)
sched.add_job(models.Mongodb().insert_temp, "interval", seconds=5)
# sched.add_job(mock_data.update_last_newuser_id, "cron", hour=23, minute=59, second=50)
sched.add_job(models.Mongodb().insert_daily_agg, "cron", hour=0, minute=0, second=10)
sched.start()
