from flask import render_template, request, jsonify, redirect
from bson.json_util import dumps
from bson.objectid import ObjectId 
from werkzeug.security import generate_password_hash, check_password_hash

from saveYourGroceries.app import app
from saveYourGroceries.data.users import users_db, find_user

@app.route('/') 
def index():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/create')
def create(): 
    return render_template("create.html")

@app.route('/adduser', methods=['POST'])
def add_user():
    if request.method == 'POST':
        _username = request.form['inputUsername']
        if find_user(_username):
            # how to send message? 
            return redirect('/create')

        _password = request.form['inputPassword']
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _hashed_pwd = generate_password_hash(_password)
        query = {
            'name': _name,
            'email': _email,
            'username': _username,
            'password': _hashed_pwd
        }
        users_db.users.insert_one(query)
        return redirect('/login')
    else: 
        return not_found()
