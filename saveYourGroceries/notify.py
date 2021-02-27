from twilio.rest import Client 
from celery import Celery
from celery.schedules import crontab
import redis

from datetime import date

from saveYourGroceries.app import app
from saveYourGroceries.config import account_sid, auth_token, twilio_number, redis_url
from saveYourGroceries.data.user import get_all_users
from saveYourGroceries.data.db import groceries_db

# SMS Messaging 
twilio_client = Client(account_sid, auth_token)

# Celery Scheduler
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL'],
        timezone='US/Central'   # Must have for periodic tasks
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    print("Celery configuration complete")
    return celery

celery = make_celery(app)

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    # Executes everyday at 8:00 a.m.
    sender.add_periodic_task(
        crontab(hour=8),
        daily_notification.s()
    )

"""
Run daily at 8:00AM CST 
Sends sms notification to all users if they have groceries
with eat by current date
"""
@celery.task
def daily_notification():
    print(8*'*'+"Daily notification"+8*'*')
    users = get_all_users()

    for user in users: 
        eat_bys = find_eat_bys(user)
        if len(eat_bys) > 0:        
            message = format_message(eat_bys)
            ret = send_notification(user["number"], message)
            print(ret)

"""
param user: dict, an entry in users_db
return eat_bys: list, all groceries of users with eat_by date of current date
"""
def find_eat_bys(user):
    today = date.today().toordinal()
    # Query product for user by date_expiration
    query = {
        "user": user['username'], 
        "date_expiration": today 
    }
    ret = groceries_db.find(query)
    eat_bys = [eat_by for eat_by in ret]
    return eat_bys

"""
param eat_bys: pymongo cursor of item names with eat-by date as today
return message: string, formatted text notification 
"""
def format_message(eat_bys):
    items = [item['item'] for item in eat_bys]
    message = "These items have reached their eat-by dates. Consider eating them!\n"
    message += "\n\t".join(items)
    message += "\n\nFrom SaveYourGroceries"
    return message 

"""
param number: int, client number
param message: string, formatted notification message
return string status
"""
def send_notification(number, message):

    message = twilio_client.messages.create(from_=twilio_number,
                      to=number,
                      body=message)
    return message.sid