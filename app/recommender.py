import pandas

import config
import mysql.connector
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

    recipe_matrix = database.recipe_dataframe_from_query(query)

    # Copy the dataframe and turn the "ingredients" column into a list of tokens
    recipe_matrix_split_ingredients = recipe_matrix.copy()
    recipe_matrix_split_ingredients["ingredients"] = recipe_matrix_split_ingredients["ingredients"].apply(
        lambda x: " ".join(x.split(","))).apply(nltk.word_tokenize)

    # Create a list of all ingredients
    all_ingredients = []
    for recipe_ingredients in recipe_matrix_split_ingredients["ingredients"].tolist():
        all_ingredients += recipe_ingredients
    unique_ingredients = list(set(all_ingredients))
    print(len(unique_ingredients))
    recipe_ingredient_counts = recipe_matrix_split_ingredients["ingredients"].apply(
        lambda x: {i: list(set(x)).count(i) for i in set(x)})
    # print(ingredient_counts.head())
    print("rtf")
    recipes_term_frequency_matrix = recipe_ingredient_counts.apply(pd.Series)
    recipes_term_frequency_matrix.fillna(0, inplace=True)
    # print(term_frequency_df)
    print("idf")
    number_of_recipes = len(recipe_matrix.index)
    print(number_of_recipes)
    inverse_document_frequency = {}
    for i in recipes_term_frequency_matrix:
        # Find the document frequency of the term i
        # Find the length of the series of the term column where the cell > 0
        document_frequency_i = len(recipes_term_frequency_matrix[recipes_term_frequency_matrix[i] > 0])
        inverse_document_frequency_i = math.log(number_of_recipes / document_frequency_i, 2)
        inverse_document_frequency[i] = inverse_document_frequency_i

    # print(inverse_document_frequency)
    print("r-tfidf")
    recipe_tf_idf_matrix = recipes_term_frequency_matrix.mul(inverse_document_frequency)
    # print(recipe_tf_idf_matrix)
    # query_matrix = pd.DataFrame([query.cleaned_tokens], columns=["ingredients"])
    print("qc")
    query_counts = {i: list(set(query.cleaned_tokens)).count(i) for i in set(query.cleaned_tokens)}
    print("qtf")
    query_term_frequency = pd.DataFrame(query_counts, columns=unique_ingredients, index=[0])
    query_term_frequency.fillna(0, inplace=True)
    # print(query_term_frequency)
    print("qtfidf")
    query_tf_idf = query_term_frequency.mul(inverse_document_frequency)
    # print(query_tf_idf)
    query_series = query_tf_idf.iloc[0]
    # print(query_series)

    print("magnitudes")
    recipe_magnitudes = recipe_tf_idf_matrix.apply(lambda x: magnitude(x), axis=1)
    # print(recipe_magnitudes)
    query_magnitude = magnitude(query_series)
    # print(query_magnitude)
    equation_denominator = recipe_magnitudes * query_magnitude  # need a better name for this
    # print(equation_denominator)
    dot_products = recipes_term_frequency_matrix.dot(query_series)
    dot_products = dot_products.divide(equation_denominator)
    # print(dot_products)
    vector_similarities = dot_products.apply(lambda x: 1 - (math.acos(x) / math.pi))
    vector_similarities.fillna(0, inplace=True)
    vector_similarities.sort_values(inplace=True, ascending=False)
    # print(vector_similarities)
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
