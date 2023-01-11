from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField, BooleanField
from wtforms.validators import NumberRange


class RecommenderForm(FlaskForm):
    ingredients = (StringField("Ingredient"))
    diet = SelectField("Veg, pesc, etc", choices=[
        (None, 'None'),
        ('vgn', 'Vegan'),
        ('veg', 'Vegetarian'),
        ('psc', 'Pescetarian')
    ])
    max_time = IntegerField("Maximum Cooking Time", validators=[NumberRange(min=1)])

    exclude_celery = BooleanField("Celery")
    exclude_dairy = BooleanField("Dairy")
    exclude_eggs = BooleanField("Eggs")
    exclude_gluten = BooleanField("Gluten")
    exclude_mustard = BooleanField("Mustard")
    exclude_nuts = BooleanField("Nuts")
    exclude_sesame = BooleanField("Sesame")
    exclude_soya = BooleanField("Soya")

    submit = SubmitField("Find Recipes")
