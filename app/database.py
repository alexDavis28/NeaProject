from flask import Flask
from app import db
from app.models import Query, Recipe, Ingredient
import pandas as pd


def select_recipes_with_query(query: Query, limit: int = 5) -> list[Recipe]:
    """Find all recipes with at least one ingredient that matches a token in the query"""
    # open database connection
    cursor = db.connection.cursor()
    find_recipes_sql = create_recipe_select_sql(query)

    cursor.execute(find_recipes_sql)
    results = cursor.fetchall()
    recipes = []
    for result in results:
        ingredients = []
        for ingredient in result[5].split(","):  # Check this against the character in the sql maybe?
            ingredients.append(Ingredient(ingredient))
        recipes.append(Recipe(result[1], ingredients, result[2], result[3], result[4]))
    return recipes


def recipe_dataframe_from_query(query: Query) -> pd.DataFrame:
    sql = create_recipe_select_sql(query)
    connection = db.connect
    dataframe = pd.read_sql(sql, connection).set_index("recipe_id")
    return dataframe


def create_recipe_select_sql(query: Query) -> str:
    """Creates a sql query to select recipes that contain any ingredient that matches any given in the user query"""
    # Create pattern to match ingredient names. Join by | allows any ingredient token to match
    ingredients_regex = "|".join(query.cleaned_tokens)

    # need to find a cleaner way to do this
    if query.max_time is None:
        find_recipes_sql = f"SELECT recipes.*, GROUP_CONCAT(ingredients.name SEPARATOR ',') AS ingredients FROM recipes, " \
                           f"ingredients, has_ingredient WHERE recipes.recipe_id=has_ingredient.recipe_id AND " \
                           f"ingredients.ingredient_id=has_ingredient.ingredient_id AND recipes.recipe_id IN (SELECT " \
                           f"has_ingredient.recipe_id FROM ingredients, has_ingredient WHERE " \
                           f"has_ingredient.ingredient_id=ingredients.ingredient_id AND ingredients.ingredient_id = ANY(" \
                           f"SELECT ingredient_id FROM ingredients WHERE name REGEXP \"{ingredients_regex}\")) GROUP BY " \
                           f"recipes.recipe_id, recipes.title;"
    else:
        find_recipes_sql = f"SELECT recipes.*, GROUP_CONCAT(ingredients.name SEPARATOR ',') AS ingredients FROM recipes, " \
                           f"ingredients, has_ingredient WHERE recipes.recipe_id=has_ingredient.recipe_id AND " \
                           f"ingredients.ingredient_id=has_ingredient.ingredient_id AND recipes.recipe_id IN (SELECT " \
                           f"has_ingredient.recipe_id FROM ingredients, has_ingredient WHERE " \
                           f"has_ingredient.ingredient_id=ingredients.ingredient_id AND ingredients.ingredient_id = ANY(" \
                           f"SELECT ingredient_id FROM ingredients WHERE name REGEXP \"{ingredients_regex}\")) AND recipes.time <=" \
                           f"{query.max_time} GROUP BY recipes.recipe_id, recipes.title;"
    return find_recipes_sql
