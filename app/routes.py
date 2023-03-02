from app import app, recommender
from app.forms import RecommenderForm, CreateProfileForm, LoginForm, SaveRecipeForm, ChangeEmailForm, ChangePasswordForm
from flask import render_template, session, redirect, url_for, request, flash
from app.models import Query, User
from app.database import add_profile_to_database, find_user_by_email, user_save_recipe, find_user_saved_recipes,\
    change_user_email, change_user_password


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


@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    if "query" in session:
        form = SaveRecipeForm()
        query_data = session["query"]
        query = Query(raw_ingredients=query_data["raw_ingredients"], sort_mode=query_data["sort_mode"],
                      max_time=query_data["max_time"], limit=query_data["limit"])
        query.results = recommender.find_results(query)
        # Limit number returned
        query.results = query.results[:query.limit]
        return render_template("recommend.html", results=query.results, query_ingredients=query.cleaned_tokens,
                               form=form)
    else:
        return redirect("/")


@app.route("/save_recipe", methods=["POST"])
def save_recipe():
    if "active_user_email" in session:
        if request.method == "POST":
            user = find_user_by_email(session["active_user_email"])
            user_save_recipe(request.form["recipe_title"], user)
        return redirect("/profile")
    else:
        flash("Please log in to save recipes", "info")
        return redirect("login")


@app.route('/info')
def info():
    # Route for info page
    return render_template("info.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    # Route for register page
    form = CreateProfileForm()
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            flash("Passwords do not match", "form")
        # Create profile
        else:
            user = User(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
            user.password_hash = user.calculate_password_hash(user.plaintext_password)
            profile_added_successfully = add_profile_to_database(user)
            if not profile_added_successfully:
                flash("Email already in use", "form")
            else:
                return redirect("/login")
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Find profile with given email
        email = form.email.data
        password = form.password.data
        stored_user = find_user_by_email(email)
        if not stored_user:
            flash("Invalid email", "form")
        else:
            login_user = User(first_name=stored_user.first_name, last_name=stored_user.last_name, email=email,
                              plaintext_password=password)
            login_user.password_hash = login_user.calculate_password_hash(login_user.plaintext_password)
            if login_user.password_hash == stored_user.password_hash:
                session["active_user_email"] = email
                return redirect("/profile")
            else:
                flash("Invalid password", "form")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    # Logout user
    if "active_user_email" in session:
        del session["active_user_email"]
    return redirect("/profile")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    change_email_form = ChangeEmailForm()
    change_password_form = ChangePasswordForm()
    if change_email_form.validate_on_submit() and change_email_form.data:
        user = find_user_by_email(change_email_form.current_email.data)
        form_password_hash = User.calculate_password_hash(change_email_form.password.data)
        if not user:
            # invalid email
            flash("Invalid email", "change-email-form")
        else:
            if form_password_hash == user.password_hash:
                has_changed_email = change_user_email(user, new_email=change_email_form.new_email.data)
                if has_changed_email:
                    return redirect("/logout")
                elif not has_changed_email:
                    flash("Email already in use", "change-email-form")
            else:
                flash("Incorrect password", "change-email-form")
    elif change_password_form.validate_on_submit() and change_password_form.data:
        user = find_user_by_email(change_password_form.email.data)
        current_password_hash = User.calculate_password_hash(change_password_form.current_password.data)
        new_password_hash = User.calculate_password_hash(change_password_form.new_password.data)
        if not user:
            flash("Invalid email", "change-password-form")
        else:
            if current_password_hash == user.password_hash:
                change_user_password(user, new_password_hash)
                return redirect("/logout")
            else:
                flash("Incorrect password", "change-password-form")
    if "active_user_email" in session:
        # find currently logged in account
        user = find_user_by_email(session["active_user_email"])
        saved_recipes = find_user_saved_recipes(user)
        return render_template("profile.html", user=user, recipes=saved_recipes, change_email_form=change_email_form,
                               change_password_form=change_password_form)
    else:
        return redirect("login")


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
