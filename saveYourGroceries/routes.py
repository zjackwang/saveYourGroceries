from flask import render_template, flash, request, jsonify, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash, check_password_hash

import json 
import re
from datetime import date, timedelta

from saveYourGroceries.app import app
from saveYourGroceries.data.user import User 
from saveYourGroceries.forms import LoginForm, RegisterForm
from saveYourGroceries.rparser import analyze_receipt

import saveYourGroceries.data.login
import saveYourGroceries.config 
from saveYourGroceries.data import grocery


@app.route('/', methods=['GET', 'POST']) 
def index():
    if current_user.is_anonymous:
        return render_template("index.html")
    else:
        # json of item name, brand (if possible), category, and expiration date 
        ret = grocery.get_groceries(current_user.username)
        groceries = [{
            'name': item['item'], 
            'date_purchased': date.fromordinal(item['date_purchased']),
            'date_expiration': date.fromordinal(item['date_expiration'])
            } 
            for item in ret
        ]
        return render_template("user.html", groceries=groceries)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm() 
    if form.validate_on_submit():
        user = User.find_user(form.username.data) 
        if user and User.check_password(user['hashed_pwd'], form.password.data):
            user_obj = User(user['username'], user['email'], user['name'])
            login_user(user_obj)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        else:
            flash("Invalid username or password")
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register(): 
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        
        user = {
            "username": username,
            "email": email,
            "name": form.name.data,
            "hashed_pwd": User.generate_password(form.password.data)
        }

        User.add_user(user) 
        return redirect(url_for('index'))
            
    return render_template("register.html", form=form)

@app.route('/scan')
@login_required
def scan():
    return render_template("scan.html")


"""
Finds only exact delimited words 
@param item: str, grocery item name
@param purchase_date: date object, when item was purchase
@param product_list: list, all products in expiration database
@return date_item: datetime, day of recommended grocery usage 
"""
def process_grocery_exp(item, purchase_date, product_list):
    DEFAULT_DAYS = timedelta(days=7)
    for product in product_list: 
        c = re.compile(f"(?:^|\W){product}(?:$|\W)")
        item_lower = item.lower()
        if len(c.findall(item_lower)) > 0:
            days = grocery.get_product_fridge_life(product)
            # use timedelta to change date
            delta_t = timedelta(days=days)
            return purchase_date + delta_t

    return purchase_date + DEFAULT_DAYS


@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        flash("No file part")
        return redirect(url_for('scan'))
    
    receipt = request.files['image']
    if receipt.filename == '':
        flash("No image selected for uploading")
        return redirect(url_for('scan'))

    receipt_json = analyze_receipt(receipt)
    r_info = receipt_json['analyzeResult']['documentResults'][0]['fields']
    store_name = r_info['MerchantName']['text'] if r_info['MerchantName']['confidence'] > .5 else None 
    store_products = [(obj['valueObject']['Name']['text'], obj['valueObject']['TotalPrice']['text']) for obj in r_info['Items']['valueArray']]

    if len(receipt_json['analyzeResult']['documentResults'][0]['fields']) > 4:
        r_date = receipt_json['analyzeResult']['documentResults'][0]['fields']['TransactionDate']['valueDate'],split('/')
        p_date = date(r_date[0], r_date[1], r_date[2])
    else:
        p_date = date.today()

    # omit prices for now 
    items = [item for item, price in store_products]
    # get specific grocery list 
    product_list = grocery.get_product_list()
    # try to match each item to one on list
    for item in items: 
        exp_date = process_grocery_exp(item, p_date, product_list)
        # store ordinal 
        print(f"Storing {item} with {str(exp_date)} exp date")
        grocery.add_groceries(current_user.username, item, p_date.toordinal(), exp_date.toordinal())

    flash(f"Success! You have added {len(items)} groceries to your account")
    return redirect(url_for("scan"))


@app.route('/delete', methods=["POST"])
def delete():
    item = request.form['item']
    grocery.remove_grocery(current_user.username, item) 

    return redirect(url_for('index'))