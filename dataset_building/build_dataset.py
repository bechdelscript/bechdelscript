import os

import configue
import pandas as pd

from dataset_building.download_imsdb_scripts import main_imsdb
from dataset_building.get_kaggle_scripts import main_kaggle


def create_bechdel_db(config):
    bechdel_df = pd.read_json(config["urls"]["bechdel_test_api"])
    os.makedirs(config["paths"]["input_folder_name"], exist_ok=True)
    bechdel_df.to_csv(
        os.path.join(
            config["paths"]["input_folder_name"], config["names"]["bechdel_db_name"]
        ),
        index=False,
    )


def merge_datasets(config):
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
    elif config["merge_dataset"]["keep"] == "kaggle":
        keep = "last"
    else:
        raise ValueError(
            f"The merge_dataset.keep parameters can only be \
'imsdb' or 'kaggle', got {config['merge_dataset']['keep']}"
        )

    duplicate_scripts_to_delete = df_dataset[
        df_dataset.duplicated(subset=["imdbid"], keep=keep)
    ]
    df_dataset = df_dataset.drop_duplicates(subset=["imdbid"], keep=keep)

    # this list of unparsable script was formed manually (empty file, one line only etc.)
    list_unparsable_scripts = configue.load(config["names"]["unparsable_scripts"])[
        "unparsable_scripts"
    ]
    df_dataset = df_dataset[~df_dataset["path"].isin(list_unparsable_scripts)]
    for script_path in (
        duplicate_scripts_to_delete["path"].tolist() + list_unparsable_scripts
    ):
        if os.path.exists(script_path) and not df_dataset["path"].tolist():
            os.remove(script_path)

    df_dataset.to_csv(
        config["paths"]["input_folder_name"] + config["names"]["db_name"],
        index=False,
    )


def build_dataset(config):
    create_bechdel_db(config)
    main_imsdb(config)
    main_kaggle(config)
    merge_datasets(config)


if __name__ == "__main__":
    config = configue.load("parameters.yaml")
    build_dataset(config)
