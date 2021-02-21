from pymongo import MongoClient
from saveYourGroceries.config import mongo_key

client = MongoClient(f"mongodb+srv://zjackwang:{mongo_key}@cluster0.5ocd6.mongodb.net/test?authSource=admin&replicaSet=atlas-q2c9r8-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true")
products_db = client['users'].products
dates_db = client['users'].dates
users_db = client['users'].users
groceries_db = client['users'].groceries