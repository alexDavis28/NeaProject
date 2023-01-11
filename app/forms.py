from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField, FieldList
from wtforms.validators import NumberRange


class RecommenderForm(FlaskForm):
    ingredients = (StringField("Ingredient"))
    diet = SelectField("Dietary Requirements", choices=[
        ('vgn', 'Vegan'),
        ('veg', 'Vegetarian'),
        ('psc', 'Pescetarian')
    ])
    max_time = IntegerField("Maximum Cooking Time", validators=[NumberRange(min=1)])
    meal_type = StringField("Meal Type")
    submit = SubmitField("Find Recipes")
