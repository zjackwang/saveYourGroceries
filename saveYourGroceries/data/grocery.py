import datetime 
from saveYourGroceries.data.db import groceries_db, dates_db, products_db


def add_groceries(user, item, date, exp_date):
    if date == None:
        date = datetime.date.today().strftime('%Y/%m/%d')
    query = { 
        'user': user,
        'item': item,
        'date_purchased': date,
        'date_expiration': exp_date
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

def get_product_fridge_life(item):
    query = {
        'product': item
    }

    return dates_db.find(query)[0]['days_in_fridge']

def get_product_list():
    return products_db.find({'name':'products'})[0]['products']