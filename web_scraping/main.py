from app import models
import scrapers

scraper = scrapers.AllRecipes()
url = "https://www.allrecipes.com/recipe/57783/emilys-famous-hash-browns/"
recipe = scraper.scrape_page(url)
print(recipe.__dict__)
