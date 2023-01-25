import string
from abc import ABC, abstractmethod
from typing import List
import requests
from bs4 import BeautifulSoup
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize


class Ingredient:
    def __init__(self, name: str, dietary_information: str = None):
        self.name = name


class Recipe:
    def __init__(self, title: str, ingredients: list[Ingredient], total_time: int, url: str, website: str):
        self.title = title
        self.ingredients = ingredients
        self.total_time = total_time
        self.url = url
        self.website = website

    @property
    def formatted_time(self) -> str:
        if self.total_time == -1:
            return "N/A"
        else:
            hours = self.total_time // 60
            minutes = self.total_time % 60

            if hours == 0:
                return f"{minutes} minutes"
            elif hours == 1:
                return f"1 hr {minutes} mins"
            else:
                return f"{hours} hrs {minutes} mins"


class Result(Recipe):
    def __init__(self, title: str, ingredients: list[Ingredient], total_time: int, url: str, website: str,
                 relevancy: float):
        super().__init__(title, ingredients, total_time, url, website)
        self.relevancy = relevancy


class User:
    def __init__(self, first_name: str, last_name: str, email: str, password_hash: str, recipes: list[Recipe]):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = password_hash
        self.recipes = recipes


class Query:
    def __init__(self, raw_ingredients: str, max_time: int = -1):
        self.raw_ingredients = raw_ingredients
        self.cleaned_tokens = self.clean_and_tokenize_text(raw_ingredients)
        self.max_time = max_time
        self.results: list[Result] = []

    @staticmethod
    def clean_and_tokenize_text(text: str) -> list[str]:
        wnl = WordNetLemmatizer()
        text = text.lower()
        tokens = word_tokenize(text)
        lemmatized_tokens = [wnl.lemmatize(token) for token in tokens]
        return lemmatized_tokens


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
