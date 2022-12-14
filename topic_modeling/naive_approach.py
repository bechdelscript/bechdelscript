import json
import os
import yaml

import pandas as pd
import random as rd


def import_masculine_words():
    config = yaml.safe_load(open("parameters.yaml"))

    path_masculine_words = os.path.join(
        config["paths"]["topic_modeling_folder"],
        config["names"]["list_of_words_about_men"],
    )
    masculine_words = json.load(open(path_masculine_words))
    return masculine_words


def clean_punctuation(word):
    if word[-1] in [".", ",", ";", "?", "!"]:
        word = word[:-1]
    return word


# masculine_words = import_masculine_words
# print(masculine_words)
# print()


def dialogue_is_mentionning_men_naive(
    dialogue, male_characters
):  # dialogue: liste de str, male_characters : liste de str,  noms des personnages masculins du film
    masculine_words = import_masculine_words()
    masculine_words += male_characters

    lines_stripped = [line.strip() for line in dialogue if line.strip() != ""]

    lines_mentionning_men = []
    lines_not_mentionning_men = []
    processed = False

    for line in lines_stripped:
        words = line.split(" ")
        for keyword in masculine_words:
            if keyword in words:
                lines_mentionning_men.append(line)
                processed = True
                break
        if not processed:
            lines_not_mentionning_men.append(line)
        else:
            processed = False

    bool = len(lines_mentionning_men) > 0
    return bool, lines_mentionning_men, lines_not_mentionning_men


# lines = [
#     line.strip() for line in script.readlines() if line.strip() != ""
# ]  ## frankestein and frankenweenie ne sont pas des scripts

# lines_mentionning_men = []
# lines_not_mentionning_men = []
# processed = False
# for line in lines:
#     words = line.split(" ")
#     for keyword in masculine_words:
#         if keyword in words:
#             lines_mentionning_men.append(line)
#             processed = True
#             break
#     if not processed:
#         lines_not_mentionning_men.append(line)
#     else:
#         processed = False


if __name__ == "__main__":

    config = yaml.safe_load(open("parameters.yaml"))

    path_dataset = os.path.join(
        config["paths"]["input_folder_name"], config["names"]["db_name"]
    )

    df = pd.read_csv(path_dataset)

    path_scripts = list(df["path"])

    script = open(
        path_scripts[0], "r"
    )  # itérer sur les scripts  (for path in path_scripts :)

    (
        bool,
        lines_mentionning_men,
        lines_not_mentionning_men,
    ) = dialogue_is_mentionning_men_naive(script.readlines(), [])

    # print("nombre de lignes au total :", len(lines))
    # print()
    print(bool)
    print("nombre de lignes contenant mention masculine :", len(lines_mentionning_men))
    print(rd.choice(lines_mentionning_men))
    print()

    print(
        "nombre de lignes ne contenant pas de mention masculine :",
        len(lines_not_mentionning_men),
    )
    print(rd.choice(lines_not_mentionning_men))
    print()

    test = [
        "coucou je suis un texte qui ne parle pas d'hommes",
        "la banane est pourrie",
        "la vie est belle",
        "donald trump s'est présenté à nouveaux aux élections des US",
    ]
    (
        bool,
        lines_mentionning_men,
        lines_not_mentionning_men,
    ) = dialogue_is_mentionning_men_naive(test, ["donald"])

    print(bool)
    print("nombre de lignes contenant mention masculine :", len(lines_mentionning_men))
    if bool:
        print(rd.choice(lines_mentionning_men))
    print()
    print(
        "nombre de lignes ne contenant pas de mention masculine :",
        len(lines_not_mentionning_men),
    )
    print(rd.choice(lines_not_mentionning_men))
    print()
