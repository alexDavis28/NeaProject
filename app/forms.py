from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField, EmailField, PasswordField
from wtforms.validators import NumberRange, DataRequired, Optional
from wtforms import ValidationError


class RecommenderForm(FlaskForm):
    ingredients = StringField("Ingredients", validators=[DataRequired()])
    max_time = IntegerField("Maximum Time", validators=[Optional(), NumberRange(min=1)])
    sort_mode = SelectField("Sort by",
                            choices=[('relevancy', 'Relevancy'), ('title', 'Title'), ('total_time', 'Time to cook')])
    limit = IntegerField("Limit number of results", validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField("Find Recipes")


class CreateProfileForm(FlaskForm):
    first_name = StringField("First name", validators=[DataRequired()])
    last_name = StringField("Last name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    repeat_password = PasswordField("Repeat Password", validators=[DataRequired()])
    submit = SubmitField("Create profile")
    # Check if password fields equal


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class SaveRecipeForm(FlaskForm):
    # Provides a csrf token to the save recipe button
    pass
