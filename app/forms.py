from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import NumberRange, DataRequired, Optional


class RecommenderForm(FlaskForm):
    ingredients = StringField("Ingredients", validators=[DataRequired()])
    max_time = IntegerField("Maximum Time", validators=[Optional(), NumberRange(min=1)])
    sort_mode = SelectField("Sort by", choices=[('relevancy', 'Relevancy'), ('title', 'Title'), ('total_time', 'Time to cook')])
    limit = IntegerField("Limit number of results", validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField("Find Recipes")
