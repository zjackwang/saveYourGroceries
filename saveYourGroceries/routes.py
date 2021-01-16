from flask import render_template, flash, request, jsonify, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from saveYourGroceries.app import app
from saveYourGroceries.users.user import User 
from saveYourGroceries.forms import LoginForm, RegisterForm

import saveYourGroceries.users.login
import saveYourGroceries.config

@app.route('/') 
def index():
    if current_user.is_anonymous:
        return render_template("index.html")

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
