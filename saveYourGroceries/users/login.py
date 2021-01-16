from flask_login import LoginManager

from saveYourGroceries.users.user import User 
from saveYourGroceries.users.db import users_db
from saveYourGroceries.app import app 

loginManager = LoginManager(app) 
loginManager.login_view = 'login'

@loginManager.user_loader
def load_user(username): 
    query = {
        "username": username 
    }
    user = users_db.find_one(query)
    if not user: 
        return None 
    return User(user['username'], user['email'], user['name'])



