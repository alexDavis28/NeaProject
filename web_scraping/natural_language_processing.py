import nltk
from nltk import word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
from app.models import Ingredient
from typing import Optional

nltk.download("popular")
wnl = WordNetLemmatizer()


def find_phrases(tagged_tokens: list) -> list:
    # print(tagged_tokens)
    tags = ["NN", "NNP", "JJ"]
    phrases = []
    current_phrase_tokens = []
    i = 0

    # Clean tokens of commonly mistaken words
    with open("ignore_words.txt", "r") as file:
        ignore_words = file.read().splitlines()
    tagged_tokens = [token for token in tagged_tokens if token[0] not in ignore_words]

    for tagged_token in tagged_tokens:
        if tagged_token[1] in tags and tagged_token[0].isalpha():
            current_phrase_tokens.append(tagged_token)
        elif current_phrase_tokens:
            phrases.append(" ".join([token[0] for token in current_phrase_tokens]))
            current_phrase_tokens.clear()
        i += 1
    else:
        if current_phrase_tokens:
            phrases.append(" ".join([token[0] for token in current_phrase_tokens]))

    return phrases


def identify_ingredient(text: str) -> Optional[Ingredient]:
    text = text.lower()
    tokens = word_tokenize(text)
    lemmatized_tokens = [wnl.lemmatize(t) for t in tokens]
    tagged_tokens = pos_tag(lemmatized_tokens)

    # Identify sequences of nouns
    phrases = find_phrases(tagged_tokens)
    ingredient = " ".join(phrases) if phrases else None
    if ingredient:
        return Ingredient(ingredient)
    return None
