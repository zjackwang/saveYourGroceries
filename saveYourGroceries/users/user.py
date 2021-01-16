from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from saveYourGroceries.users.db import users_db


class User(UserMixin):
    def __init__(self, username, email, name):
        self.username = username
        self.email = email
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
    def find_user(username="user", email=None):
        query = {}
        if email:
            query["email"] = email
        else: 
            query["username"] = username
        user = users_db.find_one(query)
        if not user:
            return None
        return user 
    
    @staticmethod 
    def add_user(user):
        users_db.insert_one(user)
