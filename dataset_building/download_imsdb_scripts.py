"""Downloads all scripts from IMSDB."""
# Code adapted from https://github.com/j2kun/imsdb_download_all_scripts

import os
from typing import List, Tuple
from urllib.parse import quote
from venv import create

import yaml
import bs4
import pandas as pd
import requests
from bs4 import BeautifulSoup

config = yaml.safe_load(open("parameters.yaml"))

SAVE_EVERY = 10  # for each SAVE_EVRY scripts downloaded we update the csv file

BASE_URL = config["urls"]["imsdb_base_url"]


def clean_script(text: str) -> str:
    text = text.replace("Back to IMSDb", "")
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
        """          Scanned by http://freemoviescripts.com
          Formatting by http://simplyscripts.home.att.net
""",
        "",
    )
    return text.replace(r"\r", "")


def get_script(relative_link: str) -> Tuple[str, str]:
    tail = relative_link.split("/")[-1]
    print(f"fetching {tail}")

    # Get script link
    script_front_url = BASE_URL + quote(relative_link)
    front_page_response = requests.get(script_front_url)
    front_soup = BeautifulSoup(front_page_response.text, "html.parser")

    try:
        script_link = front_soup.find_all("p", align="center")[0].a["href"]
    except IndexError:
        print("%s has no script :(" % tail)
        return None, None

    # Get script
    if script_link.endswith(".html"):
        filename = script_link.split("/")[-1].split(" Script")[0]
        script_url = BASE_URL + script_link
        script_soup = BeautifulSoup(requests.get(script_url).text, "html.parser")
        script_text = script_soup.find_all("td", {"class": "scrtext"})[0].get_text()
        script_text = clean_script(script_text)
        return filename, script_text
    else:
        print("%s is a pdf :(" % tail)
        return None, None


def get_clean_title(paragraph: bs4.element.Tag) -> str:
    title = paragraph.a.text
    if title.endswith(", The"):
        # remove the , The" at the end
        title = title.replace(", The", "")
        # Add The at the beginning
        title = "The " + title
    return title


def begin_from_where_we_left(
    paragraphs: bs4.element.ResultSet, scripts_df_path: str
) -> Tuple[List[pd.DataFrame], int]:

    if not os.path.exists(scripts_df_path):
        # we begin at 1 because currently the first paragraph is an ad
        return [], 1
    else:
        # If the program was interrupted before, we begin from the last registered movie
        list_dfs = [pd.read_csv(scripts_df_path)]
        last_movie_name = list_dfs[0]["title"].iloc[-1]
        list_movies_names = [get_clean_title(p) for p in paragraphs]
        begin_from = list_movies_names.index(last_movie_name) + 1
        return list_dfs, begin_from


def retrieve_all_scripts():

    # Retrieving list of movies from main page
    response = requests.get(f"{BASE_URL}/all-scripts.html")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    paragraphs = soup.find_all("p")

    # Checking if we start from the first movie or not
    scripts_df_path = os.path.join(
        config["paths"]["input_folder_name"], config["names"]["imsdb_intermediate_name"]
    )
    list_dfs, begin_from_index = begin_from_where_we_left(paragraphs, scripts_df_path)

    # Creating result folder
    scripts_dir_path = config["paths"]["path_to_imsdb_scripts"]
    os.makedirs(scripts_dir_path, exist_ok=True)

    # Looping on all movies
    for i, p in enumerate(paragraphs[begin_from_index:]):
        relative_link = p.a["href"]
        title = get_clean_title(p)
        filename, script = get_script(relative_link)
        if not script:
            continue

        # Saving script as text file
        script_path = os.path.join(scripts_dir_path, filename.strip(".html") + ".txt")
        with open(script_path, "w+", encoding="utf-8") as outfile:
            outfile.write(script)

        # Adding movie name and path to a dataframe
        list_dfs.append(pd.DataFrame([[title, script_path]], columns=["title", "path"]))
        # We save the data frame every SAVE_EVERY scripts
        if (i + 1) % SAVE_EVERY == 0 or i == len(paragraphs[begin_from_index:]) - 1:
            df = pd.concat(list_dfs)
            df.to_csv(scripts_df_path, index=False)


def merge_imsdb_with_bechdel():
    bechdel_df_path = os.path.join(
        config["paths"]["input_folder_name"], config["names"]["bechdel_db_name"]
    )
    bechdel_df = pd.read_csv(bechdel_df_path)

    imsbd_df_path = os.path.join(
        config["paths"]["input_folder_name"], config["names"]["imsdb_intermediate_name"]
    )
    imsbd_df = pd.read_csv(imsbd_df_path)

    complete_df_path = os.path.join(
        config["paths"]["input_folder_name"], config["names"]["imsdb_db_name"]
    )
    complete_df = pd.merge(
        left=bechdel_df, right=imsbd_df, left_on="title", right_on="title"
    )

    complete_df.to_csv(complete_df_path, index=False)


def main_imsdb():
    retrieve_all_scripts()
    merge_imsdb_with_bechdel()


if __name__ == "__main__":
    main_imsdb()
