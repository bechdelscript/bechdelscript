import os
from random import choice

import pandas as pd
import argparse
import configue


from screenplay_classes import Script
from dataset_building.build_dataset import build_dataset


def main(args):
    config = configue.load(args.parameters_path)

    path_dataset = os.path.join(
        config["paths"]["input_folder_name"], config["names"]["db_name"]
    )
    if not os.path.exists(path_dataset):
        build_dataset()
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

    script = Script(script_path, config)

    print("Nom du script :", script_path.split("/")[-1])

    print("Nombres de scènes :", len(script.list_scenes))
    print("Nombres de personnages :", len(script.list_characters))
    print(
        "Score d'après le dataset :",
        dataset[dataset["path"] == script_path].iloc[0]["rating"],
    )

    script.display_results(args.nb_scenes)


parser = argparse.ArgumentParser()
parser.add_argument("--parameters_path", type=str, default="parameters.yaml")
parser.add_argument("--movie_name", type=str, default="")
parser.add_argument("--script_filename", type=str, default="")
parser.add_argument("--nb_scenes", type=int, default=1)

parser.set_defaults(predict=True)
if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
