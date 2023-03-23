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


def naive_narrative_gender(paragraphs: list, name: str, tokens: pd.DataFrame) -> str:
    """
    Given a list of paragraphs, a character name, and a gendered tokens dataframe,
    this function returns the gender associated with the most frequent pronouns present in
    paragraphs where the character is named."""
    freq_gender = {"m": 0, "f": 0, "nb": 0}
    paragraphs = [para for para in paragraphs if name in para]
    for para in paragraphs:
        freq_tokens = dict.fromkeys(tokens[0], 0)
        freq = {}
        for word in nltk.word_tokenize(para):
            for token in tokens[0]:
                if token == word.lower():
                    freq_tokens[token] += 1
        for key in freq_tokens.keys():
            gen = tokens.loc[tokens[0] == key][1].values[0]
            value = freq_tokens[key]
            try:
                freq[gen] += value
            except:
                freq[gen] = value
        freq_gender[max(freq, key=lambda k: freq[k])] += 1
    res = max(freq_gender, key=lambda k: freq_gender[k])
    return res
