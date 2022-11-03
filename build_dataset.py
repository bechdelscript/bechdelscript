from download_imsdb_scripts import main_imsdb
from get_kaggle_scripts import main_kaggle
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


def build_dataset():
    create_bechdel_db()
    main_imsdb()
    main_kaggle()


if __name__ == "__main__":
    build_dataset()
