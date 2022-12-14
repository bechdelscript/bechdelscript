import os
from random import choice

import pandas as pd
import argparse
import yaml


from screenplay_classes import Script


def main(args):
    config = yaml.safe_load(open(args.parameters_path))

    path_dataset = os.path.join(
        config["paths"]["input_folder_name"], config["names"]["db_name"]
    )
    dataset = pd.read_csv(path_dataset)
    if args.movie_name != "":
        if args.movie_name in dataset["title"].unique():
            script_path = dataset[dataset["title"] == args.movie_name].iloc[0]["path"]
            if args.script_filename != "" and not script_path.endswith(
                args.script_filename
            ):
                raise ValueError(
                    "Movie name and script filename don't match. We recommend \
                    using only one of the two arguments."
                )
        else:
            raise ValueError(f"The movie '{args.movie_name}' is not in the dataset.")
    elif args.script_filename != "":
        corresponding_movies = dataset[
            dataset["path"].apply(lambda x: x.endswith(args.script_filename))
        ]
        if len(corresponding_movies.index) > 0:
            script_path = corresponding_movies.iloc[0]["path"]
        else:
            raise ValueError(
                f"No movie path ending in '{args.script_filename}' was found in the dataset."
            )
    else:
        script_path = choice(dataset["path"])

    script = Script(script_path)

    print("Nom du script :", script_path.split("/")[-1])

    print("Nombres de scènes :", len(script.list_scenes))
    print("Nombres de personnages :", len(script.list_characters))
    print(
        "Score d'après le dataset :",
        dataset[dataset["path"] == script_path].iloc[0]["rating"],
    )
    print("Score d'après notre code :", script.computed_score)

    bechdel_approved, approved_scenes = script.passes_bechdel_test()

    if bechdel_approved:
        print("\nLe film passe le test !! <3")
        print("Nombre de scènes passant le test :", len(approved_scenes))
        for i in range(1, min(args.nb_scenes, len(approved_scenes)) + 1):
            print(
                f"\n******* {str(i) + 'ère' if i == 1 else str(i) + 'ème'} scène *******"
            )
            print(approved_scenes[i - 1])
            # print(
            #     "Personnages présents dans la scène : ",
            #     [
            #         f"{char.name} ({char.gender})"
            #         for char in approved_scenes[0].list_characters_in_scene
            #     ],
            # )
    else:
        print("\nLe film passe pas :(")


parser = argparse.ArgumentParser()
parser.add_argument("--parameters_path", type=str, default="parameters.yaml")
parser.add_argument("--movie_name", type=str, default="")
parser.add_argument("--script_filename", type=str, default="")
parser.add_argument("--nb_scenes", type=int, default=1)

parser.set_defaults(predict=True)
if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
