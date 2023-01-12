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
        ingredients = [i for i in identified_ingredients if i]

        # Find total prep time:
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
        soup = self.make_soup("https://www.allrecipes.com/")
        links = soup.find(id="header-nav_1-0").findAll("a")
        links = [l.get("href") for l in links]

        links_to_scrape = []
        for link in links:
            try:
                recipe_links = self.find_recipe_links(link)
                for recipe_link in recipe_links:
                    print(recipe_link)
                    links_to_scrape.append(recipe_link)
            except Exception as e:
                print(e)

        print(len(links_to_scrape))
        input()

        # 3908
        print("part 2")
        soup = self.make_soup("https://www.allrecipes.com/recipes-a-z-6735880")
        links = soup.find(id="alphabetical-list_1-0").findAll("a")
        links = [l.get("href") for l in links]
        for link in links:
            try:
                recipe_links = self.find_recipe_links(link)
                for recipe_link in recipe_links:
                    print(recipe_link)
                    links_to_scrape.append(recipe_link)
            except Exception as e:
                print(e)
        print(len(links_to_scrape))
        input()
        # 23308

        soup = self.make_soup("https://www.allrecipes.com/ingredients-a-z-6740416")
        links = soup.find(id="alphabetical-list_1-0").findAll("a")
        links = [l.get("href") for l in links]
        for link in links:
            try:
                recipe_links = self.find_recipe_links(link)
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