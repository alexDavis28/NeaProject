import requests
from scrapers import AllRecipes
url = "https://www.allrecipes.com/"
scraper = AllRecipes()

soup = scraper.make_soup(url)

links = soup.find(id="header-nav_1-0").findAll("a")
links = [l.get("href") for l in links]

links_to_scrape = []
for link in links:
    try:
        recipe_links = scraper.find_recipe_links(link)
        for recipe_link in recipe_links:
            links_to_scrape.append(recipe_link)
    except Exception as e:
        print(e)

# 3908

# TODO https://www.allrecipes.com/recipes-a-z-6735880
# TODO https://www.allrecipes.com/ingredients-a-z-6740416