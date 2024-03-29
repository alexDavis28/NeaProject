from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize, pos_tag


class Ingredient:
    def __init__(self, name: str):
        self.name = name

    def as_dict(self):
        return {"name": self.name}


class Recipe:
    def __init__(self, title: str, ingredients: list[Ingredient], total_time: int, url: str, website: str):
        self.title = title
        self.ingredients = ingredients
        self.total_time = total_time
        self.url = url
        self.website = website

    def as_dict(self):
        return {
            "title": self.title,
            "ingredients": [i.as_dict() for i in self.ingredients],
            "total_time": self.total_time,
            "url": self.url,
            "website": self.website
        }

    @property
    def formatted_time(self) -> str:
        """Returns the recipe's total time formatted in hours and minutes"""
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
                 relevancy: float = None):
        super().__init__(title, ingredients, total_time, url, website)
        self.relevancy = relevancy

    def as_dict(self):
        return {
            "title": self.title,
            "ingredients": [i.as_dict() for i in self.ingredients],
            "total_time": self.total_time,
            "url": self.url,
            "website": self.website,
            "relevancy": self.relevancy
        }


class User:
    def __init__(self, first_name: str, last_name: str, email: str, plaintext_password: str = None,
                 password_hash: str = None, user_id: int = None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.plaintext_password = plaintext_password
        self.password_hash = password_hash
        self.user_id = user_id

    @staticmethod
    def calculate_password_hash(password: str = None) -> str:
        total = 0
        for i, character in enumerate(password):
            total += ord(character) ** (i + 1)
        product = 1
        for character in password:
            product *= ord(character)
        value = total * product
        hash = str(value % 2147483647)
        return hash


class Query:
    def __init__(self, raw_ingredients: str, sort_mode: str = "relevancy", max_time: int = None, limit: int = None):
        self.raw_ingredients = raw_ingredients
        self.cleaned_tokens = self.clean_and_tokenize_text(raw_ingredients)
        self.sort_mode = sort_mode
        self.max_time = max_time
        self.results: list[Result] = []
        self.limit = limit

    @staticmethod
    def clean_and_tokenize_text(text: str) -> list[str]:
        """Return a list of cleaned tokens"""
        # TODO replace this with a function in the NLP module
        wnl = WordNetLemmatizer()
        text = text.lower()
        tokens = word_tokenize(text)
        lemmatized_tokens = [wnl.lemmatize(token) for token in tokens]
        tagged_tokens = pos_tag(lemmatized_tokens)
        clean_tokens = [token[0] for token in tagged_tokens if token[1] in ["NN", "NNP", "JJ"]]
        return clean_tokens


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
