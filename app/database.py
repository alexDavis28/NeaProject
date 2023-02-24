from flask import Flask
from app import db
from app.models import Query, Result, Ingredient, User
import pandas as pd
import MySQLdb
from typing import Optional


def select_recipes_with_query(query: Query) -> list[Result]:
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
        recipes.append(Result(result[1], ingredients, result[2], result[3], result[4]))
    return recipes


def recipe_dataframe_from_query(query: Query) -> pd.DataFrame:
    """Pandas dataframe from results of query"""
    sql = create_recipe_select_sql(query)
    connection = db.connect
    dataframe = pd.read_sql(sql, connection).set_index("recipe_id")
    return dataframe


def create_recipe_select_sql(query: Query) -> str:
    """Creates a sql query to select recipes that contain any ingredient that matches any given in the user query"""
    # TODO: use vals instead of interpolation
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


def add_profile_to_database(profile: User) -> bool:
    cursor = db.connection.cursor()
    values = (profile.first_name, profile.last_name, profile.email, profile.password_hash)
    sql = "INSERT INTO users (first_name, last_name, email, password) VALUES (%s, %s, %s, %s);"
    # cursor.execute(sql, values)
    try:
        cursor.execute(sql, values)
    except MySQLdb.IntegrityError:
        # Throws when trying to create a profile with an already used email
        return False
    db.connection.commit()
    return True


def find_user_by_email(email: str) -> Optional[User]:
    cursor = db.connection.cursor()
    sql = f'SELECT * FROM users WHERE email="{email}";'
    cursor.execute(sql)
    if cursor.rowcount == 0:
        # no results found
        return None
    else:
        result = cursor.fetchone()
        user = User(user_id=result[0], first_name=result[1], last_name=result[2], email=result[3],
                    password_hash=result[4])
        return user
    pass


def user_save_recipe(recipe_title: str, user: User):
    # Get recipe id by title
    cursor = db.connection.cursor()
    recipe_select = f"SELECT recipe_id FROM recipes WHERE title='{recipe_title}';"
    cursor.execute(recipe_select)
    recipe_id = cursor.fetchone()[0]

    insert_sql = f"INSERT INTO saved_recipe (user_id, recipe_id) VALUES (%s, %s);"
    values = (user.user_id, recipe_id)
    cursor.execute(insert_sql, values)
    db.connection.commit()
