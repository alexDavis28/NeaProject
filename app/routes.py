from app import app, recommender
from app.forms import RecommenderForm, CreateProfileForm, LoginForm
from flask import render_template, session, redirect, url_for, request, flash
from app.models import Query, User
from app.database import add_profile_to_database, find_user_by_email


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


@app.route('/register', methods=["GET", "POST"])
def register():
    # Route for register page
    form = CreateProfileForm()
    if form.validate_on_submit():
        # Create profile
        user = User(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
        profile_added_successfully = add_profile_to_database(user)
        if not profile_added_successfully:
            flash("Email already in use", "form")
        else:
            redirect("login")
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Find profile with given email
        email = form.email.data
        password = form.password.data
        stored_user = find_user_by_email(email)
        login_user = User(first_name=stored_user.first_name, last_name=stored_user.last_name, email=email,
                          plaintext_password=password)
        login_user.password_hash = login_user.calculate_password_hash(password)
        if login_user.password_hash == stored_user.password_hash:
            session["active_user"] = email
            return redirect("profile")
        else:
            flash("Invalid email or password", "form")
    return render_template("login.html", form=form)


@app.route("/profile")
def profile():
    return render_template("profile.html")

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
