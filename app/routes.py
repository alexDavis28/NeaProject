from app import app, recommender
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
    results = recommender.score_recipes_by_relevancy_from_query(query, limit=20)
    results.sort(key=lambda x: x.relevancy)
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
    # Route for api info page
    return render_template("api.html")


@app.route("/api/search")
def api_search():
    # API search function
    if "ingredients" not in request.args:
        return "400: Ingredients string not found", 400
    raw_ingredients = request.args["ingredients"]

    if "max_time" in request.args:
        max_time = request.args["max_time"]
    else:
        max_time = None

    query = Query(raw_ingredients, max_time)
    results = recommender.find_results(query, sort_mode="relevancy")
    data = {"results": [r.as_dict() for r in results]}
    return data