from flask import Flask
from app import db
from app.models import Query, Recipe, Ingredient


def select_recipes_with_query(query: Query, limit: int = 5) -> list[Recipe]:
    """Find all recipes matching the query"""
    # open database connection
    cursor = db.connection.cursor()

    # Create pattern to match ingredient names. Join by | allows any ingredient token to match
    ingredients_regex = "|".join([f"(\s|-|^)+{ingredient}(\s|-|$)+" for ingredient in query.cleaned_tokens])

    # need to find a cleaner way to do this
    if query.max_time is None:
        find_recipes_sql = f"SELECT recipes.*, GROUP_CONCAT(ingredients.name SEPARATOR ',') AS ingredients FROM recipes, " \
                           f"ingredients, has_ingredient WHERE recipes.recipe_id=has_ingredient.recipe_id AND " \
                           f"ingredients.ingredient_id=has_ingredient.ingredient_id AND recipes.recipe_id IN (SELECT " \
                           f"has_ingredient.recipe_id FROM ingredients, has_ingredient WHERE " \
                           f"has_ingredient.ingredient_id=ingredients.ingredient_id AND ingredients.ingredient_id = ANY(" \
                           f"SELECT ingredient_id FROM ingredients WHERE name REGEXP \"{ingredients_regex}\")) GROUP BY " \
                           f"recipes.recipe_id, recipes.title LIMIT {limit};"
    else:
        find_recipes_sql = f"SELECT recipes.*, GROUP_CONCAT(ingredients.name SEPARATOR ',') AS ingredients FROM recipes, " \
                           f"ingredients, has_ingredient WHERE recipes.recipe_id=has_ingredient.recipe_id AND " \
                           f"ingredients.ingredient_id=has_ingredient.ingredient_id AND recipes.recipe_id IN (SELECT " \
                           f"has_ingredient.recipe_id FROM ingredients, has_ingredient WHERE " \
                           f"has_ingredient.ingredient_id=ingredients.ingredient_id AND ingredients.ingredient_id = ANY(" \
                           f"SELECT ingredient_id FROM ingredients WHERE name REGEXP \"{ingredients_regex}\")) AND recipes.time <=" \
                           f"{query.max_time} GROUP BY recipes.recipe_id, recipes.title LIMIT {limit};"

    cursor.execute(find_recipes_sql)
    results = cursor.fetchall()
    recipes = []
    for result in results:
        ingredients = []
        for ingredient in result[5].split(","):  # Check this against the character in the sql maybe?
            ingredients.append(Ingredient(ingredient))
        recipes.append(Recipe(result[1], ingredients, result[2], result[3], result[4]))
    return recipes
