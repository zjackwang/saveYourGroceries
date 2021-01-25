from flask import render_template, flash, request, jsonify, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash, check_password_hash
import json 

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
        groceries = [item for item in ret]
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

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        flash("No file part")
        return redirect(url_for('scan'))
    file = request.files['image']
    if file.filename == '':
        flash("No image selected for uploading")
        return redirect(url_for('scan'))
    
    
    receipt_json = analyze_receipt(file)

    r_info = receipt_json['analyzeResult']['documentResults'][0]['fields']
    store_name = r_info['MerchantName']['text'] if r_info['MerchantName']['confidence'] > .5 else None 
    store_products = [(obj['valueObject']['Name']['text'], obj['valueObject']['TotalPrice']['text']) for obj in r_info['Items']['valueArray']]

    date = None 
    
    if len(receipt_json['analyzeResult']['documentResults'][0]['fields']) > 4:
        date = receipt_json['analyzeResult']['documentResults'][0]['fields']['TransactionDate']['valueDate']

    items = [item for item, price in store_products]

    for item in items: 
        grocery.add_groceries(current_user.username, item, date) 

    flash(f"Success! You have added {len(items)} groceries to your account")
    return redirect(url_for("scan"))


@app.route('/delete', methods=["POST"])
def delete():
    item = request.form['item']

    grocery.remove_grocery(current_user.username, item) 

    return redirect(url_for('index'))