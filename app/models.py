from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup


class Ingredient:
    def __init__(self, name: str, dietary_information: str = None):
        self.name = name
        self.dietary_information = dietary_information


class Recipe:
    def __init__(self, title: str, ingredients: list[Ingredient], total_time: int, url: str, website: str):
        self.title = title
        self.ingredients = ingredients
        self.total_time = total_time
        self.url = url
        self.website = website

    @property
    def formatted_time(self) -> str:
        hours = self.total_time // 60
        minutes = self.total_time % 60

        if hours == 0:
            return f"{minutes} minutes"
        elif hours == 1:
            return f"1 hr {minutes} mins"
        else:
            return f"{hours} hrs {minutes} mins"


class User:
    def __init__(self, first_name: str, last_name: str, email: str, password: str):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password


class WebScraper(ABC):
    @staticmethod
    def make_soup(url: str) -> BeautifulSoup:
        """Creates a BeautifulSoup Soup from a given url"""
        page = requests.get(url).text
        soup = BeautifulSoup(page, "html.parser")
        return soup

    @staticmethod
    @abstractmethod
    def scrape_page(url: str) -> Recipe:
        """Scrape a specific page and return a recipe object"""
        pass

    @staticmethod
    @abstractmethod
    def find_recipe_links(url: str) -> list[str]:
        """Find links to recipe pages on a given page"""
        pass

    @staticmethod
    @abstractmethod
    def find_links_to_scrape(recipe_site: str):
        """Create a text file of links to recipe pages"""
        pass