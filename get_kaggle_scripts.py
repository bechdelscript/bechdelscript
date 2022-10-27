"""Objectif du script : renommer tous les scripts de la base de donnée trouvée sur kaggle au lien suivant :
https://www.kaggle.com/datasets/parthplc/movie-scripts?resource=download
Utilisation du script sur ce git :
https://github.com/Umairican/The-Bechdel-Test/blob/main/data/Scripts/script_namer.ipynb
Et de créer la base de données de films répertoriés dans la db Bechdel :
https://bechdeltest.com/api/v1/doc#getMovieByImdbId
Ensuite, il s'agit de nettoyer les noms de fichiers scripts et bechdel et de merge les deux
bases de données sur le titre."""

import pandas as pd
import os
import yaml
import warnings
warnings.filterwarnings("ignore")

config = yaml.safe_load(open("parameters.yaml"))


def rename():
    file_names = os.listdir(config["paths"]["path_to_kaggle_scripts"])

    for file in file_names:
        if not file.startswith("."):
            try:
                with open(file) as f:
                    first_line = f.readline().strip()
                    os.rename(
                        config["path_to_kaggle_scripts"] + file,
                        (str(first_line) + ".txt").upper(),
                    )
            except:
                print(f"{file} could not be renamed. Please check manually")


def create_db():
    bechdel_df = pd.read_json("http://bechdeltest.com/api/v1/getAllMovies")
    print(bechdel_df.head())
    print(bechdel_df.shape)
    bechdel_df.to_csv(
        config["paths"]["input_folder_name"] + config["names"]["bechdel_db_name"]
    )

def title_cleanup(df):
    # removing &amp
    df.replace("&amp;", "", regex=True, inplace=True)
    # removing HTML gutter
    df.replace(
        to_replace=["<b>", "</b>", "<!--", ".href", "!="],
        value="",
        regex=True,
        inplace=True,
    )
    # remove new line characters
    df.replace(
        to_replace=[
            r"\\t|\\n|\\r",
            "\t|\n|\r",
            "if (window top)top.location=location// -->",
        ],
        value="",
        regex=True,
        inplace=True,
    )
    # removing other items from titles for merging
    df["title"].replace("THE|the", "", regex=True, inplace=True)
    # change all letters to lowercase
    df["title"] = [name.lower() for name in df["title"]]
    # Replace the &#39 values
    df.replace("&#39;", "'", regex=True, inplace=True)
    # remove the commas
    df["title"].replace(",", "", regex=True, inplace=True)
    return df

# Transform filename field into path to file, for easier access in the future
def fpath(filename):
    return config["paths"]["path_to_kaggle_scripts"] + filename


def main_kaggle():
    #rename()
    #create_db()
    bechdel_df = pd.read_csv(
    config["paths"]["input_folder_name"] + config["names"]["bechdel_db_name"],
    index_col="id",
    )
    bechdel_df.drop(columns="Unnamed: 0", axis=1, inplace=True)

    file_names = os.listdir(config["paths"]["path_to_kaggle_scripts"])

    # Create Dictionary for File Name and Text
    file_name_and_text = {}
    for file in file_names:
        if not file.startswith("."):
            with open(
                config["paths"]["path_to_kaggle_scripts"] + file, "r", encoding="utf8"
            ) as target_file:
                # This reads everything from the directory and aliases it as the the target file
                file_name_and_text[file] = target_file.read().split(sep="\n\n")
                file_name_and_text[file] = " ".join(file_name_and_text[file])
    script_df = (
        pd.DataFrame.from_dict(file_name_and_text, orient="index")
        .reset_index()
        .rename(index=str, columns={"index": "file_name", 0: "script"})
    )
    file_name_and_text = {}
    for file in file_names:
        if not file.startswith("."):
            with open(
                config["paths"]["path_to_kaggle_scripts"] + file, "r", encoding="utf8"
            ) as target_file:
                # This reads everything from the directory and aliases it as the the target file
                file_name_and_text[file] = target_file.readline().strip()
    title_df = (
        pd.DataFrame.from_dict(file_name_and_text, orient="index")
        .reset_index()
        .rename(index=str, columns={"index": "file_name", 0: "title"})
    )

    script_title_df = pd.merge(title_df, script_df, on="file_name", how="outer")

    # Cleanup the film titles in both dataframes for an easier merge
    script_title_df = title_cleanup(script_title_df)
    bechdel_df = title_cleanup(bechdel_df)

    # Merge the script title dataframe and the bechdel dataframe on 'title' field
    bechdel_script_df = pd.merge(
        script_title_df, bechdel_df, left_on="title", right_on="title"
    )
    bechdel_script_df["file_name"] = bechdel_script_df["file_name"].apply(fpath)

    # Drop duplicates on title field
    bechdel_script_df.drop_duplicates(subset="title", keep="first", inplace=True)

    # Drop the script column from this dataframe
    bechdel_script_df.drop(columns="script", inplace=True)

    # Save dataframe to csv file.
    bechdel_script_df.to_csv(
        config["paths"]["input_folder_name"] + config["names"]["kaggle_db_name"]
    )


if __name__ == '__main__':
    main_kaggle()