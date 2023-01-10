from app import app
from flask import render_template, url_for


@app.route('/')
def index():
    # Route for home page
    return render_template("index.html")


@app.route('/info')
def info():
    # Route for info page
    return render_template("info.html")


@app.route('/profile')
def profile():
    # Route for profile page
    return render_template("info.html")


@app.route('/api')
def api():
    # Route for info page
    return render_template("api.html")