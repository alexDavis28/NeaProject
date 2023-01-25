from app import app, database
from app.forms import RecommenderForm
from flask import render_template, session, redirect, url_for
from app.models import Query


@app.route('/', methods=["GET", "POST"])
def index():
    """Home page of the site, displaying the recommender form"""
    form = RecommenderForm()
    if form.validate_on_submit():
        query = Query(form.ingredients.data, form.max_time.data)

        session["query"] = query.__dict__
        return redirect(url_for("recommend"))
    return render_template("index.html", form=form)


@app.route("/recommend")
def recommend():
    query_data = session["query"]
    query = Query(query_data["raw_ingredients"], query_data["max_time"])
    results = database.select_recipes_with_query(query)
    return render_template("recommend.html", results=results)


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
