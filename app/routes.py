from app import app, recommender
from app.forms import RecommenderForm
from flask import render_template, session, redirect, url_for, request
from app.models import Query


@app.route('/', methods=["GET", "POST"])
def index():
    """Home page of the site, displaying the recommender form"""
    form = RecommenderForm()
    if form.validate_on_submit():
        query = Query(raw_ingredients=form.ingredients.data, sort_mode=form.sort_mode.data, max_time=form.max_time.data,
                      limit=form.limit.data)

        session["query"] = query.__dict__
        return redirect(url_for("recommend"))
    return render_template("index.html", form=form)


@app.route("/recommend")
def recommend():
    query_data = session["query"]
    query = Query(raw_ingredients=query_data["raw_ingredients"], sort_mode=query_data["sort_mode"], max_time=query_data[
        "max_time"], limit=query_data["limit"])
    query.results = recommender.find_results(query)
    # Limit number returned
    query.results = query.results[:query.limit]
    return render_template("recommend.html", results=query.results, query_ingredients=query.cleaned_tokens)


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
    if "sort_mode" in request.args:
        sort_mode = request.args["sort_mode"]
    else:
        sort_mode = "relevancy"

    query = Query(raw_ingredients, sort_mode, max_time)
    if "limit" in request.args:
        query.limit = int(request.args["limit"])

    query.results = recommender.find_results(query)
    if query.limit:
        query.results = query.results[:query.limit]
    data = {"results": [r.as_dict() for r in query.results]}
    return data