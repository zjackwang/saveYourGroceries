from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from saveYourGroceries.data.db import users_db


class User(UserMixin):
    def __init__(self, username, number, name):
        self.username = username
        self.number = number
        self.name = name 
    
    def get_id(self):
        return self.username
    
    @staticmethod 
    def check_password(hashed_password, password):
        return check_password_hash(hashed_password, password)
    
    @staticmethod 
    def generate_password(password):
        return generate_password_hash(password)
    
    @staticmethod
    def find_user(username="user", number=None):
        query = {}
        if number:
            query["number"] = number
        else: 
            query["username"] = username
        user = users_db.find_one(query)
        if not user:
            return None
        return user 
    
    @staticmethod 
    def add_user(user):
        users_db.insert_one(user)

def get_all_users():
    return users_db.find()