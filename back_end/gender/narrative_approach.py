import pandas as pd
import nltk
import os

"""Given a list of narrative passages, this function identifies the most frequently used gendered pronouns included in 
paragraphs where the character's name appears. Then, we use the most frequent gender associated with narrative passages as our
prediction."""


def import_gender_tokens(config: dict) -> pd.DataFrame:
    """
    Given a config file, this creates the gendered tokens dataframe."""

    path = os.path.join(
        config["paths"]["pronoun_folder"],
        config["names"]["list_pronoun_tokens"],
    )

    tokens = pd.read_csv(path, header=None, sep=";")
    return tokens


def pronoun_id(paragraphs: list, name: str, tokens: pd.DataFrame) -> str:
    """
    Given a list of paragraphs, a character name, and a gendered tokens dataframe,
    this function returns the gender associated with the most frequent pronouns present in
    paragraphs where the character is named."""
    freq_gender = {"M": 0, "F": 0, "NB": 0}
    paragraphs = [para for para in paragraphs if name in para]
    for para in paragraphs:
        freq_tokens = {}
        for word in nltk.word_tokenize(para):
            for token in tokens[0]:
                if token == word.lower():
                    try:
                        freq_tokens[token] += 1
                    except:
                        freq_tokens[token] = 1
        freq_tokens = {
            tokens.loc[tokens[0] == key][1].values[0]: freq_tokens[key]
            for key in freq_tokens.keys()
        }
        freq_gender[max(freq_tokens, key=lambda k: freq_tokens[k])] += 1
    res = max(freq_gender, key=lambda k: freq_gender[k])
    return res
