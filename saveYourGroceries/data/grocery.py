from saveYourGroceries.data.db import groceries_db 
import datetime 

def add_groceries(user, item, date):
    if date == None:
        date = datetime.date.today().strftime('%Y/%m/%d')
    query = { 
        'user': user,
        'item': item,
        'date_purchased': date
    }

    groceries_db.insert_one(query) 

def get_groceries(user):
    query = {
        'user': user
    }

    return groceries_db.find(query)

def remove_grocery(user, item):
    query = {
        'user': user,
        'item': item 
    }

    groceries_db.delete_one(query)