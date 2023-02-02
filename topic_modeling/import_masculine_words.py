import json
import os
import yaml


def import_masculine_words(config):

    path_masculine_words = os.path.join(
        config["paths"]["topic_modeling_folder"],
        config["names"]["list_of_words_about_men"],
    )
    masculine_words = json.load(open(path_masculine_words))
    return masculine_words
