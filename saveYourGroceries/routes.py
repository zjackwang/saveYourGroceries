from flask import render_template, request 

from saveYourGroceries.app import app

@app.route('/') 
def index():
    return render_template("index.html")