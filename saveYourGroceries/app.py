from flask import Flask

from saveYourGroceries.config import secret_key, redis_url

app = Flask(__name__) 
app.config['SECRET_KEY'] = secret_key
app.config['CELERY_BROKER_URL'] = redis_url
app.config['CELERY_RESULT_BACKEND'] = redis_url

app.secret_key = secret_key

from saveYourGroceries import routes

