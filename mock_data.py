from pymongo import MongoClient
from dotenv import load_dotenv

from datetime import datetime, timedelta
import re
import time
import os
import random
import csv
import pytz

from models import Mongodb

load_dotenv()
user = os.getenv("MONGO_USER")
psw = os.getenv("MONGO_PSW")
host = os.getenv("MONGO_HOST")

# ---- connect db ----
uri = "mongodb://{user}:{psw}@{host}:27017".format(user=user, psw=psw, host=host)
client = MongoClient(uri)
db = client["mockData"]
db_coll = db["event"]

# ---- read last_id, how_many ----

def get_last_cid_numNew():
    last_day = str((datetime.now(pytz.utc)+timedelta(-1)).date())
    today = str(datetime.now(pytz.utc).date())
    sqldb = Mongodb()
    last_client_id = sqldb.select_last_id(last_day, today)["last_id"]
    how_many = sqldb.select_numNew(last_day)["numNew"]
    if how_many > 6500:
        how_many = 6000
    print("last_client_id: " + str(last_client_id), "how_many: " + str(how_many))
    return last_client_id, how_many

# -------- gen mock data --------


# data = [] # for batch insert
# for i in range(15000 + random.randint(-5000, 5000)): # for batch insert
def gen_mock_data():

    # ---- read last_id ----
    last_client_id, how_many = get_last_cid_numNew()

    # ---- gen data ----
    for j in range(random.randint(1, 2)):
        cp = random.uniform(0, 1)
        if cp < 0.76:
            event_type = "view"
            event_key = "view_type"
            if cp < 0.25:
                event_value = "ShoppingCart"
            elif cp < 0.5:
                event_value = "Home"
            elif cp < 0.13:
                event_value = "Login"
            else:
                event_value = "Pay"
        elif cp < 0.9:
            event_type = "view_item"
            event_key = "item_id"
            event_value = 5948755555
        elif cp < 0.96:
            event_type = "add_to_cart"
            event_key = "item_id"
            event_value = 5948755555
        else:
            event_type = "checkout_progress"
            event_key = "checkout_step"
            event_value = 3

        # if a return user
        return_cp = random.uniform(0, 1)
        if return_cp < 0.03:
            return_status = True
        else:
            return_status = False

        # gen cid
        cid_cp = random.uniform(0, 1)
        if return_status:
            if cid_cp < 0.8:
                cid = random.randint(1, last_client_id)
            elif cid_cp < 0.95:
                cid = random.randint(1, int(how_many*0.15))
            else:
                cid = random.randint(1, int(how_many*0.05))
        else:
            if cid_cp < 0.8:
                cid = random.randint(last_client_id+1, last_client_id+how_many+1)
            elif cid_cp < 0.95:
                cid = random.randint(last_client_id+1, (last_client_id+1+int(how_many*0.15)))
            else:
                cid = random.randint(last_client_id+1, (last_client_id+1+int(how_many*0.05)))
        # print("cp: "+str(cp), "return_cp: "+str(return_cp), "cid_cp: "+str(cid_cp))

        doc = {"request_url": "https://track.91app.io/v2/collect?v=1&_v=j{random_key}&a=&cid={cid}&evtn={event_type}&evtk1={event_key}&evtvs1={event_value}".format(random_key=random.randint(1, 1000), cid=cid, event_type=event_type, event_key=event_key, event_value=event_value),
            "created_at": str(datetime.now(pytz.utc))[:19]
            }
        # data.append(doc) # for batch insert
        db_coll.insert_one(doc)
        # print("Mock new data success! " + str(i+1)) # for batch insert
        print("Mock data success!")
        print(doc)
# db_coll.insert_many(data) # for batch insert

# ---- check ----
# for i in db_coll.find():
#     print(i)

pipeline = [{"$group" : {"_id": "$event_type", "count":{"$sum":1}}}]

for sample in db_coll.aggregate(pipeline):
    print(sample)

# ---- update last_newuser_id ----

def update_last_newuser_id():

    #  last_client_id
    last_day = str((datetime.now(pytz.utc)+timedelta(-1)).date())
    today = str(datetime.now(pytz.utc).date())
    sqldb = Mongodb()
    last_client_id = sqldb.select_last_id(last_day, today)["last_id"]

    filepath = "last_newuser_id.csv"
    # open csv file
    with open(filepath, newline='') as csvfile:
        # read content
        rows = csv.reader(csvfile)
        # each
        for row in rows:
            how_many = int(row[1])
    
    last_client_id += how_many
    how_many += random.randint(-500, 500)
    #  open csv file
    with open(filepath, 'w', newline='') as csvfile:
        # write
        writer = csv.writer(csvfile)

        # each
        writer.writerow([last_client_id, how_many])

def data_cleaning(sample):

    text_list = re.split("&", sample["request_url_match"]["match"])
    text_dict = dict((k.strip(), v.strip())
                    for k, v in [s.split("=") for s in text_list])  

    # key
    for i in range(1, 6):
        try:
            text_dict["evtk{}".format(str(i))]
        except KeyError:
            text_dict["evtk{}".format(str(i))] = None

    # value    
    text_value = [key for key in text_dict.keys() if key.startswith('evtv')]

    for i in range(1, 6):
            text_dict["evtv{}".format(str(i))] = None

    for i in range(1, len(text_value)+1):
        text_dict["evtv{}".format(str(i))] = text_dict[text_value[i-1]]

    sample["created_at"] = datetime.strptime(sample["created_at"], '%Y-%m-%d %H:%M:%S')

    data = [sample["_id"], text_dict["cid"], text_dict["evtn"], sample["created_at"], 
            text_dict["evtk1"], text_dict["evtv1"], text_dict["evtk2"], text_dict["evtv2"], 
            text_dict["evtk3"], text_dict["evtv3"], text_dict["evtk4"], text_dict["evtv4"],
            text_dict["evtk5"], text_dict["evtv5"]]

    return data


def query_clean_all():
    
    # ---- connect db ----
    uri = "mongodb://{user}:{psw}@{host}:27017".format(user=user, psw=psw, host=host)
    client = MongoClient(uri)
    db = client["mockData"]
    db_coll = db["event"]

    # ---- query ----
    start = datetime.now()
    rule = '(cid=(.+)$)'
    pipeline = [
        {'$addFields': {
                'request_url_match': {
                    '$regexFind': {
                        'input': '$request_url',
                        'regex': rule,
                    }
                }
            }
        },
    {
            '$project': {
                'request_url': 0,
            }
        }]
    all_samples = db_coll.aggregate(pipeline)
    end = datetime.now()
    print(end - start)

    # ---- data cleaning ----
    df_lst = []
    for sample in all_samples:
        data = data_cleaning(sample)
        df_lst.append(data)
    end = datetime.now()
    print("all: " + str(end - start))

    print(len(df_lst))

    db = Mongodb()
    db.insert_many(df_lst)


def query_clean_new():

    # ---- connect db ----
    # uri = "mongodb://{user}:{psw}@{host}:27017".format(user=user, psw=psw, host=host)
    # client = MongoClient(uri)
    # db = client["mockData"]
    # db_coll = db["event"]

    # ---- create benchmark ----
    sql = Mongodb()
    last_id, last_time = sql.select_last()
    # print(last_id, last_time)
    # print(type(last_id), type(last_time))

    # ---- query ----
    # start = datetime.now()
    rule = '(cid=(.+)$)'
    pipeline = [
        {"$match":
        {'created_at': {
            "$gte": last_time
            },
        }
        },
        {'$addFields': {
                'request_url_match': {
                    '$regexFind': {
                        'input': '$request_url',
                        'regex': rule,
                    }
                }
            }
        },
        {
            '$project': {
                'request_url': 0,
            }
        }]
    new_samples = db_coll.aggregate(pipeline)
    # for i in new_samples:
    #     print(i)
    # end = datetime.now()
    # print(end - start)

    # ---- data cleaning ----
    df_lst = []
    for sample in new_samples:
        if (sample["created_at"] == last_time) & (str(sample["_id"]) > last_id):
            data = data_cleaning(sample)
            df_lst.append(data)
        elif (sample["created_at"] > last_time):
            data = data_cleaning(sample)
            df_lst.append(data)
    # end = datetime.now()
    # print("new: " + str(end - start))

    # print(len(df_lst))
    if len(df_lst) > 0:
        sql = Mongodb()
        sql.insert_many(df_lst)
        print("Insert {} new data success!".format(len(df_lst)))

# if __name__ == "__main__":
#     # query_clean_all()
#     # query_clean_new()
#     # os.system("pm2 start scheduler.py")
#     # gen_mock_data()
#     # update_last_newuser_id()