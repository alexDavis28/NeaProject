from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField, BooleanField
from wtforms.validators import NumberRange, DataRequired, Optional


class RecommenderForm(FlaskForm):
    ingredients = StringField("Ingredients", validators=[DataRequired()])
    max_time = IntegerField("Maximum Time", validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField("Find Recipes")
