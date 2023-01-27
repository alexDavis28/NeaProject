import pandas as pd
import nltk
import math
from app import database
from app.models import Query, Result, Ingredient

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


def magnitude(vector: list[float]) -> float:
    # TODO make this faster
    return math.sqrt(sum([math.pow(i, 2) for i in vector]))


def score_recipes_by_relevancy_from_query(query: Query, limit: int = 20) -> list[Result]:
    # TODO better comments
    # Create a recipe dataframe from the query using the database

    # Read the recipe data from the database
    recipe_matrix = database.recipe_dataframe_from_query(query)

    # Copy the dataframe and turn the "ingredients" column into a list of tokens
    recipe_matrix_split_ingredients = recipe_matrix.copy()
    recipe_matrix_split_ingredients["ingredients"] = recipe_matrix_split_ingredients["ingredients"].apply(
        lambda x: " ".join(x.split(","))).apply(nltk.word_tokenize)

    # Create a list of all unique ingredients
    all_ingredients = []
    for recipe_ingredients in recipe_matrix_split_ingredients["ingredients"].tolist():
        all_ingredients += recipe_ingredients
    unique_ingredients = list(set(all_ingredients))

    # Turn each list of tokens in the dataframe into a dictionary of tokens and how many times they appear in the list
    recipe_ingredient_counts = recipe_matrix_split_ingredients["ingredients"].apply(
        lambda x: {i: x.count(i) for i in set(x)})

    # Turn each of the dictionaries in the dataframe into a series
    # Each recipe row has a column for every token, with the value being the count of that token in the recipe
    recipes_term_frequency_matrix = recipe_ingredient_counts.apply(pd.Series)
    recipes_term_frequency_matrix.fillna(0, inplace=True)  # Replace NaNs with 0

    # Calculate the inverse document frequency for each term i
    number_of_recipes = len(recipe_matrix.index)
    inverse_document_frequency = {}
    for i in recipes_term_frequency_matrix:
        # Find the document frequency of the term i
        # df = the length of the series of the term column where the cell > 0
        document_frequency_i = len(recipes_term_frequency_matrix[recipes_term_frequency_matrix[i] > 0])
        # Calculate the idf for i
        inverse_document_frequency_i = math.log(number_of_recipes / document_frequency_i, 2)
        inverse_document_frequency[i] = inverse_document_frequency_i

    # Calculate the tf-idf matrix by multiplying each row of the term frequency matrix by the idf values
    # This produces the dataframe of recipe vectors
    recipe_tf_idf_matrix = recipes_term_frequency_matrix.mul(inverse_document_frequency)

    # Count each of the terms in the query text
    query_counts = {i: query.cleaned_tokens.count(i) for i in set(query.cleaned_tokens)}
    # Create a term frequency table using the term counts of the query and the set of terms that appear in the recipes
    query_term_frequency = pd.DataFrame(query_counts, columns=unique_ingredients, index=[0])
    query_term_frequency.fillna(0, inplace=True)

    # Create the query tf-idf matrix by multiplying the query term frequency matrix by the idf values created earlier
    # This is the vectorized query
    query_tf_idf = query_term_frequency.mul(inverse_document_frequency)
    query_tf_idf_series = query_tf_idf.iloc[0]  # The query tf-idf needs to be stored as a series for the dot product

    print("magnitudes")
    # Calculate the magnitude of each recipe vector
    recipe_magnitudes = recipe_tf_idf_matrix.apply(lambda x: magnitude(x), axis=1)
    # Calculate the magnitude of the query vector
    query_magnitude = magnitude(query_tf_idf_series)
    # Multiply the magnitudes of each recipe vector by the query vector to produce the denominator of the angle equation
    equation_denominator = recipe_magnitudes * query_magnitude  # need a better name for this

    # Calculate the dot products of each recipe vector and the query vector
    dot_products = recipes_term_frequency_matrix.dot(query_tf_idf_series)
    # Divide the dot products by the product of the magnitudes to find the cosine of the angle between the vectors
    vector_angles = dot_products.divide(equation_denominator)

    # Calculate the angle between the vectors and bound it within positive space (0.5 to 1)
    vector_similarities = vector_angles.apply(lambda x: 1 - (math.acos(x) / math.pi))
    vector_similarities.fillna(0, inplace=True)
    # Sort the recipe ids by the relevancy score
    vector_similarities.sort_values(inplace=True, ascending=False)
    recipes = []
    for i in range(limit if limit <= number_of_recipes else number_of_recipes):
        relevancy = vector_similarities.iloc[0]
        recipe_data = recipe_matrix.loc[vector_similarities.index[i]]
        ingredients = [Ingredient(ingredient) for ingredient in recipe_data["ingredients"].split(",")]
        recipe = Result(recipe_data["title"],
                        ingredients,
                        recipe_data["time"],
                        recipe_data["url"],
                        recipe_data["website"],
                        relevancy
                        )
        recipes.append(recipe)
    return recipes
