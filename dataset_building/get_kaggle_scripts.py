"""Objectif du script : renommer tous les scripts de la base de donnée trouvée sur kaggle au lien suivant :
https://www.kaggle.com/datasets/parthplc/movie-scripts?resource=download
Utilisation du script sur ce git :
https://github.com/Umairican/The-Bechdel-Test/blob/main/data/Scripts/script_namer.ipynb
Et de créer la base de données de films répertoriés dans la db Bechdel :
https://bechdeltest.com/api/v1/doc#getMovieByImdbId
Ensuite, il s'agit de nettoyer les noms de fichiers scripts et bechdel et de merge les deux
bases de données sur le titre."""

import os
import sys
import warnings

import pandas as pd

warnings.filterwarnings("ignore")


def clean_script(text: str) -> str:
    text = text.replace(
        """<b><!--
</b>if (window!= top)
top.location.href=location.href
<b>// -->
</b>

""",
        "",
    )

    text = text.replace(
        """<b><!--

</b>if (window!= top)

top.location.href=location.href

<b>// -->

</b>

""",
        "",
    )

    text = text.replace(
        """<b><!--

</b>

<b>/*

</b>Break-out-of-frames script

By Website Abstraction (http://wsabstract.com)

Over 400+ free scripts here!

Above notice MUST stay entact for use

<b>*/

</b>

if (window!= top)

top.location.href=location.href

<b>// -->

</b>
""",
        "",
    )

    return text.replace(r"\r", "")


def clean_file(path):
    with open(path, "r") as f:
        script = f.read()
        script = clean_script(script)
    with open(path, "w") as f:
        f.write(script)


def rename(config):
    if not os.path.exists(config["paths"]["path_to_kaggle_scripts"]):
        raise ValueError(
            f"The folder {config['paths']['path_to_kaggle_scripts']} does not exist. \
                         Please create the folder, download the kaggle scripts manually  at \
                         https://www.kaggle.com/datasets/parthplc/movie-scripts?resource=download&select=Scripts \
                         and place them in the folder."
        )
    file_names = os.listdir(config["paths"]["path_to_kaggle_scripts"])

    for file in file_names:
        if not file.startswith("."):
            try:
                old_path = os.path.join(config["paths"]["path_to_kaggle_scripts"], file)
                clean_file(old_path)
                with open(old_path) as f:
                    first_line = (
                        f.readline()
                        .strip()
                        .replace(":", "_")
                        .replace('"', "'")
                        .replace("/", "-")
                        .replace("*", "+")
                    )
                    while (
                        first_line == "" or first_line == "<script>"
                    ):  # if first_line empty or == "<script>", we take the next one
                        first_line = (
                            f.readline()
                            .strip()
                            .replace(":", "_")
                            .replace('"', "'")
                            .replace("/", "-")
                            .replace("*", "+")
                        )

                    new_path = os.path.join(
                        config["paths"]["path_to_kaggle_scripts"],
                        (str(first_line) + ".txt").upper(),
                    )
                os.rename(
                    old_path,
                    new_path,
                )
            except:
                print(f"{file} could not be renamed. Please check manually")
                print("Unexpected error:", sys.exc_info()[0])


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
    df["title"].replace("\bTHE|the\b", "", regex=True, inplace=True)
    # change all letters to lowercase
    df["title"] = [name.lower() for name in df["title"]]
    # Replace the &#39 values
    df.replace("&#39;", "'", regex=True, inplace=True)
    # remove the commas
    df["title"].replace(",", "", regex=True, inplace=True)
    return df


# Transform filename field into path to file, for easier access in the future
def fpath(config, filename):
    return config["paths"]["path_to_kaggle_scripts"] + filename


def main_kaggle(config):
    rename(config)
    bechdel_df = pd.read_csv(
        os.path.join(
            config["paths"]["input_folder_name"], config["names"]["bechdel_db_name"]
        ),
        index_col="id",
    )

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

    # Drop duplicates on title field
    bechdel_script_df.drop_duplicates(subset="title", keep="first", inplace=True)

    # Scripts that are not in the bechdel database are deleted
    scripts_to_delete = script_title_df[
        ~script_title_df["file_name"].isin(bechdel_script_df["file_name"].tolist())
    ]
    for filename in scripts_to_delete["file_name"].tolist():
        script_path = fpath(config, filename)
        if os.path.exists(script_path):
            os.remove(script_path)

    # Complete the path with folder names
    bechdel_script_df["file_name"] = bechdel_script_df["file_name"].apply(
        lambda x: fpath(config, x)
    )

    # Drop the script column from this dataframe
    bechdel_script_df.drop(columns="script", inplace=True)

    # Rename "file_name" column to "path"
    bechdel_script_df = bechdel_script_df.rename(columns={"file_name": "path"})

    # Save dataframe to csv file.
    bechdel_script_df.to_csv(
        config["paths"]["input_folder_name"] + config["names"]["kaggle_db_name"],
        index=False,
    )


if __name__ == "__main__":
    main_kaggle()
