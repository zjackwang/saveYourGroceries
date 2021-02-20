from flask import Flask

from saveYourGroceries.config import secret_key

app = Flask(__name__) 
app.config['SECRET_KEY'] = secret_key
app.secret_key = secret_key

from saveYourGroceries import routes

