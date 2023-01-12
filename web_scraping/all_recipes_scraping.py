import json
from scrapers import AllRecipes
import time

scraper = AllRecipes()


def find_links_to_scrape():
    links_file_path = "allrecipes_data\allrecipeslinks.txt"
    soup = scraper.make_soup("https://www.allrecipes.com/")
    links = soup.find(id="header-nav_1-0").findAll("a")
    links = [l.get("href") for l in links]

    links_to_scrape = []
    for link in links:
        try:
            recipe_links = scraper.find_recipe_links(link)
            for recipe_link in recipe_links:
                print(recipe_link)
                links_to_scrape.append(recipe_link)
        except Exception as e:
            print(e)

    print(len(links_to_scrape))
    input()

    # 3908
    print("part 2")
    soup = scraper.make_soup("https://www.allrecipes.com/recipes-a-z-6735880")
    links = soup.find(id="alphabetical-list_1-0").findAll("a")
    links = [l.get("href") for l in links]
    for link in links:
        try:
            recipe_links = scraper.find_recipe_links(link)
            for recipe_link in recipe_links:
                print(recipe_link)
                links_to_scrape.append(recipe_link)
        except Exception as e:
            print(e)
    print(len(links_to_scrape))
    input()
    # 23308

    soup = scraper.make_soup("https://www.allrecipes.com/ingredients-a-z-6740416")
    links = soup.find(id="alphabetical-list_1-0").findAll("a")
    links = [l.get("href") for l in links]
    for link in links:
        try:
            recipe_links = scraper.find_recipe_links(link)
            for recipe_link in recipe_links:
                print(recipe_link)
                links_to_scrape.append(recipe_link)
        except Exception as e:
            print(e)
    print(len(links_to_scrape))
    input()
    # 27254

    unique_links = set(links_to_scrape)
    print(len(unique_links))
    with open(links_file_path, "w+") as file:
        file.write("\n".join(unique_links))
        print("file written")
    # 16,639


def batch_scrape_pages(start: int, end: int):
    recipe_file_path = f"allrecipes_data\\allrecipes_recipes_{start}_{end - 1}.json"
    ingredients_file_path = f"allrecipes_data\\allrecipes_ingredients_{start}_{end - 1}.json"

    with open("allrecipes_data\\allrecipeslinks.txt", "r") as file:
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
        except Exception as e:
            print(e, link)

    for recipe in recipes:
        recipe.ingredients = [i.__dict__ for i in recipe.ingredients]

    recipe_data = [recipe.__dict__ for recipe in recipes]

    with open(recipe_file_path, "w+") as file:
        json.dump({"allrecipes": recipe_data}, file)
    with open(ingredients_file_path, "w+") as file:
        json.dump({"allrecipes": ingredients_data}, file)


batch_scrape_pages(0, 1000)

'''
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
