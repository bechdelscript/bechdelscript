import os
from random import choice

import pandas as pd
import yaml

from screenplay_classes import Script


def main():
    config = yaml.safe_load(open("parameters.yaml"))

    path_dataset = os.path.join(
        config["paths"]["input_folder_name"], config["names"]["db_name"]
    )
    dataset = pd.read_csv(path_dataset)
    script_path = choice(dataset["path"])
    # script_path = "data/input/scripts_imsdb/[name of your film].txt"

    script = Script(script_path)

    print("Nom du script :", script_path.split("/")[-1])

    print("Nombres de scènes :", len(script.list_scenes))
    print("Nombres de personnages :", len(script.list_characters))

    bechdel_approved, approved_scenes = script.passes_bechdel_test()

    if bechdel_approved:
        print("Le film passe le test !! <3")
        print("Nombre de scènes passant le test :", len(approved_scenes))
        print("Première scène :")
        print(approved_scenes[0])
        print(
            "Personnages présents dans la scène : ",
            [
                [char.name, char.gender]
                for char in approved_scenes[0].list_characters_in_scene
            ],
        )
    else:
        print("Le film passe pas :(")


if __name__ == "__main__":

    main()
