import json
import scrapers
import time
import os


def batch_scrape_pages(recipe_site: str, scraper: scrapers.WebScraper, start: int, end: int):
    recipe_file_path = f"{recipe_site}_data\\{recipe_site}_recipes_{start}_{end - 1}.json"
    ingredients_file_path = f"{recipe_site}_data\\{recipe_site}_ingredients_{start}_{end - 1}.json"

    with open(f"{recipe_site}_data\\{recipe_site}links.txt", "r") as file:
        links = file.read().split("\n")[start:end]

    recipes = []
    ingredients_data = []

    l = len(links)
    for i, link in enumerate(links):
        print(f"{round((i / l) * 100, 5)}%")
        try:
            time.sleep(0.05)
            recipe = scraper.scrape_page(link)
            ingredients_data += [ingredient.__dict__ for ingredient in recipe.ingredients]
            recipes.append(scraper.scrape_page(link))
        except AttributeError as e:
            print("Invalid page " + link)
            print(e)
        except Exception as e:
            print(e, link)

    for recipe in recipes:
        recipe.ingredients = [i.__dict__ for i in recipe.ingredients]

    recipe_data = [recipe.__dict__ for recipe in recipes]

    with open(recipe_file_path, "w+") as file:
        json.dump({recipe_site: recipe_data}, file)
    with open(ingredients_file_path, "w+") as file:
        json.dump({recipe_site: ingredients_data}, file)


def combine_json(recipe_site: str, ingredients_or_recipes: str):
    """Combine all json files into one, ingredients_or_recipes should be one of _ingredients_ or _recipes_"""
    data_path = f"{recipe_site}_data\\"
    out_path = data_path + f"{recipe_site}{ingredients_or_recipes}combined.json"
    files = [file for file in os.listdir(data_path) if ingredients_or_recipes in file and file.endswith("json")]
    data_list = []
    for file in files:
        print(file)
        with open(data_path + file, "r") as file:
            data = json.load(file)
            data_list += data[recipe_site]
    data = {recipe_site: data_list}
    with open(out_path, "w+") as file:
        json.dump(data, file)


combine_json("allrecipes", "_ingredients_")
# print(combine_json("allrecipes", "_recipes_")[-1])
# NOTE: combined recipe file has 8 duplicates

# all_recipes_scraper = scrapers.AllRecipes()
# # scraper.find_links_to_scrape("allrecipes")
# batch_scrape_pages("allrecipes", all_recipes_scraper, 8000, 9000)
# batch_scrape_pages("allrecipes", all_recipes_scraper, 9000, 10000)
# batch_scrape_pages("allrecipes", all_recipes_scraper, 10000, 11000)
# batch_scrape_pages("allrecipes", all_recipes_scraper, 11000, 12000)
# batch_scrape_pages("allrecipes", all_recipes_scraper, 12000, 13000)
# batch_scrape_pages("allrecipes", all_recipes_scraper, 13000, 14000)
# batch_scrape_pages("allrecipes", all_recipes_scraper, 14000, 15000)
# batch_scrape_pages("allrecipes", all_recipes_scraper, 15000, 16000)
# batch_scrape_pages("allrecipes", all_recipes_scraper, 16000, 16639)


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
