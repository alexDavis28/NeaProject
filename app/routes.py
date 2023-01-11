from app import app
from app.forms import RecommenderForm
from flask import render_template, session, redirect, url_for


@app.route('/', methods=["GET", "POST"])
def index():
    form = RecommenderForm()
    if form.validate_on_submit():
        data = {
            "Ingredient": form.ingredients.data,
            "Diet": form.diet.data,
            "MaxTime": form.max_time.data,
            "excludeCelery": form.exclude_celery.data,
            "excludeDairy": form.exclude_dairy.data,
            "excludeEggs": form.exclude_eggs.data,
            "excludeGluten": form.exclude_gluten.data,
            "excludeMustard": form.exclude_mustard.data,
            "excludeNuts": form.exclude_nuts.data,
            "excludeSesame": form.exclude_sesame.data,
            "excludeSoya": form.exclude_soya.data
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
