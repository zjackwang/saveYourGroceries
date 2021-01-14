from os import getenv 
from os.path import join, dirname
from dotenv import load_dotenv 
from bson.objectid import ObjectId

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
mongo_key = getenv('MONGO_KEY')

from pymongo import MongoClient

client = MongoClient(f"mongodb+srv://zjackwang:{mongo_key}@cluster0.5ocd6.mongodb.net/test?authSource=admin&replicaSet=atlas-q2c9r8-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true")
users_db = client['users']

def find_user(_username):
    query = {
        'username': _username
    }
    user = users_db.users.find_one(query)
    return user

# if __name__ == "__main__": 
#     users = users_db.users

#     data = {'name': 'John', 'age': 30, 'username': 'johnjohn'}

#     users.insert_one(data)