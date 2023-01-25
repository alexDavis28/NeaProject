from app import app
from app.forms import RecommenderForm
from flask import render_template, session, redirect, url_for


@app.route('/', methods=["GET", "POST"])
def index():
    """Home page of the site, displaying the recommender form"""
    form = RecommenderForm()
    if form.validate_on_submit():
        data = {
            "Ingredient": form.ingredients.data,
            "MaxTime": form.max_time.data,
        }
        session["recommenderFormData"] = data
        return redirect(url_for("recommend"))
    return render_template("index.html", form=form)


@app.route("/recommend")
def recommend():
    return session["recommenderFormData"]


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
