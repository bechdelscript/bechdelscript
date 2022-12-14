from dataset_building.download_imsdb_scripts import main_imsdb
from dataset_building.get_kaggle_scripts import main_kaggle
import pandas as pd
import os
import yaml

config = yaml.safe_load(open("parameters.yaml"))


def create_bechdel_db():
    bechdel_df = pd.read_json(config["urls"]["bechdel_test_api"])
    bechdel_df.to_csv(
        os.path.join(
            config["paths"]["input_folder_name"], config["names"]["bechdel_db_name"]
        ),
        index=False,
    )


def merge_datasets():

    df_kaggle = pd.read_csv(
        os.path.join(
            config["paths"]["input_folder_name"], config["names"]["kaggle_db_name"]
        ),
    )

    df_imsdb = pd.read_csv(
        os.path.join(
            config["paths"]["input_folder_name"], config["names"]["imsdb_db_name"]
        ),
    ).drop(columns="id")

    df_kaggle["imdbid"] = df_kaggle["imdbid"].apply(lambda x: int(x))
    df_imsdb["imdbid"] = df_imsdb["imdbid"].apply(lambda x: int(x))

    df_dataset = pd.concat([df_imsdb, df_kaggle], ignore_index=True)
    df_dataset = df_dataset.sort_values(["imdbid", "path"])

    if config["merge_dataset"]["keep"] == "imsdb":
        keep = "first"
    if config["merge_dataset"]["keep"] == "kaggle":
        keep = "last"

    df_dataset = df_dataset.drop_duplicates(subset=["imdbid"], keep=keep)

    df_dataset.to_csv(
        config["paths"]["input_folder_name"] + config["names"]["db_name"],
        index=False,
    )


def build_dataset():
    create_bechdel_db()
    main_imsdb()
    main_kaggle()
    merge_datasets()


if __name__ == "__main__":
    build_dataset()
