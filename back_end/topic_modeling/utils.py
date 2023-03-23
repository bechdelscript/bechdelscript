import json
import os


def import_masculine_words(config):
    path_masculine_words = os.path.join(
        config["paths"]["topic_modeling_folder"],
        config["names"]["list_of_words_about_men"],
    )
    masculine_words = json.load(open(path_masculine_words))
    return masculine_words


def clean_text(string, strip=True, add_spaces_to_extremities=False):
    if strip:
        string = string.strip()

    if add_spaces_to_extremities:
        string = " " + string + " "

    clean_string = string.replace(".", " ")
    clean_string = clean_string.replace(",", " ")
    clean_string = clean_string.replace(";", " ")
    clean_string = clean_string.replace("?", " ")
    clean_string = clean_string.replace("!", " ")
    clean_string = clean_string.replace("(", " ")
    clean_string = clean_string.replace(")", " ")
    clean_string = clean_string.replace(":", " ")
    clean_string = clean_string.replace("'", " ")

    clean_string = clean_string.lower()

    return clean_string
