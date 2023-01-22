import nltk
from nltk import word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
from app.models import Ingredient
from typing import Optional

# Download nltk packages and create the Lemmatizer model
# Outside of functions because these are very slow calls, so instead run when the module is imported
nltk.download("popular")
wnl = WordNetLemmatizer()


def find_phrases(tagged_tokens: list) -> list:
    """Find consecutive sequences of nouns and adjectives"""
    noun_adjective_tags = ["NN", "NNP", "JJ"]  # NLTK part-of-speech tags: Noun, Proper Noun, Adjective
    phrases = []
    current_phrase_tokens = []

    # Clean tokens of commonly mistaken words
    with open("ignore_words.txt", "r") as file:
        ignore_words = file.read().splitlines()
    tagged_tokens = [token for token in tagged_tokens if token[0] not in ignore_words]

    for tagged_token in tagged_tokens:
        if tagged_token[1] in noun_adjective_tags:
            current_phrase_tokens.append(tagged_token)
        elif current_phrase_tokens:
            phrases.append(" ".join([token[0] for token in current_phrase_tokens]))
            current_phrase_tokens.clear()
    else:
        # In case the last token is a noun or adjective, then the phrase needs to be added
        if current_phrase_tokens:
            phrases.append(" ".join([token[0] for token in current_phrase_tokens]))

    return phrases


def identify_ingredient(text: str) -> Optional[Ingredient]:
    """Identify the key components of a given ingredient string and return an Ingredient object"""
    text = text.lower()
    tokens = word_tokenize(text)
    # Turn every token into its lemma form, ie: tomatoes -> tomato
    # All inflections of the word are turned into the root lemma, reducing the risk of misclassifying an ingredient
    lemmatized_tokens = [wnl.lemmatize(t) for t in tokens]
    # Tag tokens by part of speech, ie: noun, adjective, verb
    tagged_tokens = pos_tag(lemmatized_tokens)

    # Identify sequences of nouns and adjectives
    phrases = find_phrases(tagged_tokens)
    # If no phrases are found then None is returned
    ingredient = Ingredient(" ".join(phrases)) if phrases else None
    return ingredient
