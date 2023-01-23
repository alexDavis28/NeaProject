import mysql.connector
import json
import config


def batch_insert_recipes(recipe_site: str, start: int, end: int):
    """Insert recipes from json (sliced from start to end) into the database"""
    json_path = f"{recipe_site}_data\\{recipe_site}_recipes_combined.json"
    with open(json_path) as file:
        recipe_data = json.load(file)[recipe_site][start: end]
    db = mysql.connector.connect(host=config.DATABASE_HOST,
                                 username=config.DATABASE_USERNAME,
                                 password=config.DATABASE_PASSWORD,
                                 database=config.DATABASE_NAME)
    for recipe in recipe_data:
        cursor = db.cursor()
        # Insert the recipe
        recipe_values = (recipe["title"], recipe["total_time"], recipe["url"], recipe["website"])
        recipe_insert_sql = "INSERT INTO recipes (title, time, url, website) VALUES (%s, %s, %s, %s)"
        cursor.execute(recipe_insert_sql, recipe_values)
        recipe_id = cursor.lastrowid

        ingredient_names = [i["name"] for i in recipe["ingredients"]]
        for ingredient in ingredient_names:
            ingredient_sql = f"INSERT IGNORE INTO ingredients (name) VALUES (\"{ingredient}\")"
            cursor.execute(ingredient_sql)

            # If ingredient already exists, find its ID
            # Otherwise get id of last insert
            if cursor.lastrowid == 0:
                ingredient_select = f"SELECT * FROM ingredients WHERE name=\"{ingredient}\""
                cursor.execute(ingredient_select)
                result = cursor.fetchone()
                ingredient_id = result[0]
            else:
                ingredient_id = cursor.lastrowid

            link_insert_sql = "INSERT IGNORE INTO has_ingredient (recipe_id, ingredient_id) VALUES (%s, %s)"
            link_values = (recipe_id, ingredient_id)
            cursor.execute(link_insert_sql, link_values)

    db.commit()


batch_insert_recipes("allrecipes", 0, 16639)
