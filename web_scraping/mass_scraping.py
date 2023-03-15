import json
import scrapers
import time
import os


def batch_scrape_pages(recipe_site: str, scraper: scrapers.WebScraper, start: int, end: int):
    """Scrape recipe links from the relevant recipe links file from a start index to the end index and store the result
    in a json file"""
    recipe_file_path = f"{recipe_site}_data\\{recipe_site}_recipes_{start}_{end - 1}.json"
    ingredients_file_path = f"{recipe_site}_data\\{recipe_site}_ingredients_{start}_{end - 1}.json"
    links_file_path = f"{recipe_site}_data\\{recipe_site}links.txt"

    with open(links_file_path, "r") as file:
        links = file.read().split("\n")[start:end]

    recipes = []
    ingredients_data = []

    for link in links:
        try:
            time.sleep(0.05)  # Reduces risk of requests being blocked and raising a Connection Error
            recipe = scraper.scrape_page(link)
            # Get dictionary representations of Ingredient objects from Recipe object
            recipe_ingredient_data = [ingredient.__dict__ for ingredient in recipe.ingredients]
            ingredients_data += recipe_ingredient_data
            # Replace ingredient objects in recipe with dictionary representations
            # So that ingredients are stored as dictionaries inside the dictionary representation of the recipe object
            recipe.ingredients = recipe_ingredient_data

            recipes.append(scraper.scrape_page(link))
        except AttributeError as e:
            # Handle invalid page
            print("Invalid page " + link)
            print(e)
        except Exception as e:
            # General error catching, mainly Connection Errors caused by sending too many requests
            print(e, link)

    recipe_data = [recipe.__dict__ for recipe in recipes]

    with open(recipe_file_path, "w+") as file:
        json.dump({recipe_site: recipe_data}, file)
    with open(ingredients_file_path, "w+") as file:
        json.dump({recipe_site: ingredients_data}, file)


def combine_json(recipe_site: str, ingredients_or_recipes: str):
    """Combine all json files into one, ingredients_or_recipes should be one of _ingredients_ or _recipes_"""
    data_path = f"{recipe_site}_data\\"
    out_path = data_path + f"{recipe_site}{ingredients_or_recipes}combined.json"
    file_paths = [file for file in os.listdir(data_path) if ingredients_or_recipes in file and file.endswith("json")]
    data_list = []
    for path in file_paths:
        with open(data_path + path, "r") as file:
            data = json.load(file)
            data_list += data[recipe_site]
    data = {recipe_site: data_list}
    with open(out_path, "w+") as file:
        json.dump(data, file)


# combine_json("allrecipes", "_ingredients_")
# print(combine_json("allrecipes", "_recipes_")[-1])
# NOTE: combined recipe file has 8 duplicates

# all_recipes_scraper = scrapers.AllRecipes()
# all_recipes_scraper.find_links_to_scrape("allrecipes")
# batch_scrape_pages("allrecipes", all_recipes_scraper, 8000, 9000)
# batch_scrape_pages("allrecipes", all_recipes_scraper, 9000, 10000)
# batch_scrape_pages("allrecipes", all_recipes_scraper, 10000, 11000)
# batch_scrape_pages("allrecipes", all_recipes_scraper, 11000, 12000)
# batch_scrape_pages("allrecipes", all_recipes_scraper, 12000, 13000)
# batch_scrape_pages("allrecipes", all_recipes_scraper, 13000, 14000)
# batch_scrape_pages("allrecipes", all_recipes_scraper, 14000, 15000)
# batch_scrape_pages("allrecipes", all_recipes_scraper, 15000, 16000)
# batch_scrape_pages("allrecipes", all_recipes_scraper, 16000, 16639)

simply_recipes_scraper = scrapers.SimplyRecipes()
simply_recipes_scraper.find_links_to_scrape("Simply Recipes")
batch_scrape_pages("Simply Recipes", simply_recipes_scraper, 0, 1153)

'''
AllRecipes
Batch 0_999
run with no sleep
894 recipes
8625 ingredients
1861 unique ingredients

Batch 0_999
run with 0.05 sleep
899 recipes
8635 ingredients
1865 unique ingredients

Batch 1000_1999
run with 0.05 sleep
921 recipes
8927 ingredients
1937 unique ingredients
'''
