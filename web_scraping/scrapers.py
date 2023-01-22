from app.models import WebScraper, Ingredient, Recipe
from natural_language_processing import identify_ingredient
import re


class AllRecipes(WebScraper):
    def scrape_page(self, url: str) -> Recipe:
        soup = self.make_soup(url)

        # Find title
        title = soup.find(id="article-heading_2-0").text.strip()

        # Find ingredients
        raw_ingredients = [i.text.strip() for i in soup.select('span[data-ingredient-name="true"]')]
        identified_ingredients = [identify_ingredient(i) for i in raw_ingredients]
        ingredients = [i for i in identified_ingredients if i]  # Remove None values returned by identify_ingredient

        # Find total time:
        total_time_regex = r"(?<=Total Time:\n)( *\d+ (hr(s)?|min(s)?) *)+"
        hours_regex = r"\d+(?= hr(s)?)"
        minutes_regex = r"\d+(?= min(s)?)"

        time_text = soup.find(id="recipe-details_1-0").text

        prep_time_results = re.search(total_time_regex, time_text)
        prep_time = prep_time_results[0] if prep_time_results else None
        if prep_time:
            prep_minutes_results = re.search(minutes_regex, prep_time)
            prep_minutes = int(prep_minutes_results[0]) if prep_minutes_results else 0

            prep_hours_results = re.search(hours_regex, prep_time)
            prep_hours_in_minutes = int(re.search(hours_regex, prep_time)[0]) * 60 if prep_hours_results else 0

            total_time = prep_minutes + prep_hours_in_minutes
        else:
            # Default value if no total time is defined in the recipe, so will always be included regardless of max time
            total_time = -1

        # Create recipe object
        recipe = Recipe(title, ingredients, total_time, url, "allrecipes")

        return recipe

    def find_recipe_links(self, url: str) -> list[str]:
        soup = self.make_soup(url)
        links = [element.get("href") for element in soup.findAll("a", class_="mntl-card-list-items")]
        return links

    def find_links_to_scrape(self, recipe_site: str):
        links_file_path = f"{recipe_site}_data\\{recipe_site}links.txt"

        # Searching for recipes on the navbar, the page of a-z of recipes and the a-z of ingredients
        pages_to_search = [["https://www.allrecipes.com/", "header-nav_1-0"],
                           ["https://www.allrecipes.com/recipes-a-z-6735880", "alphabetical-list_1-0"],
                           ["https://www.allrecipes.com/ingredients-a-z-6740416", "alphabetical-list_1-0"]]

        links = []
        for page, element_id in pages_to_search:
            soup = self.make_soup(page)
            links += [link.get("href") for link in soup.find(id=element_id).findAll("a")]

        links_to_scrape = []
        for link in links:
            try:
                recipe_links = self.find_recipe_links(link)
                for recipe_link in recipe_links:
                    links_to_scrape.append(recipe_link)
            except Exception as e:
                # Handle invalid links
                print(e)
                print(f"Invalid link: {link, recipe_link}")

        unique_links = set(links_to_scrape)
        with open(links_file_path, "w+") as file:
            file.write("\n".join(unique_links))
            print("File Written")
