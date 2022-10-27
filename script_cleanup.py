
"""L'objectif de ce script est de nettoyer les noms de fichiers scripts et bechdel et de merge les deux
bases de données sur le titre."""

import pandas as pd
import os
import re
import warnings
warnings.filterwarnings("ignore")

bechdel_df = pd.read_csv('data/input/Bechdel_db.csv', index_col='id')
bechdel_df.drop(columns='Unnamed: 0', axis=1, inplace=True)

file_names = os.listdir('data/input/scripts/')
# Create Dictionary for File Name and Text
file_name_and_text = {}
for file in file_names: 
    if not file.startswith('.'): 
        with open('data/input/scripts/' + file, "r", encoding="utf8") as target_file:
    #This reads everything from the directory and aliases it as the the target file 
            file_name_and_text[file] = target_file.read().split(sep='\n\n')
            file_name_and_text[file] = ' '.join(file_name_and_text[file])
script_df = (pd.DataFrame.from_dict(file_name_and_text, orient='index')
             .reset_index().rename(index = str, columns = {'index': 'file_name', 0: 'script'}))

# Create Dictionary for File Name and Text
file_name_and_text = {}
for file in file_names:
    #UnicodeDecodeError: 'charmap' codec can't decode byte 0x90 in position 2907500: character maps to `<undefined> 
    #This means you need to change to a UTF- encoding`  
    if not file.startswith('.'): 
        with open('data/input/scripts/' + file, "r", encoding="utf8") as target_file:
    #This reads everything from the directory and aliases it as the the target file 
            file_name_and_text[file] = target_file.readline().strip()
title_df = (pd.DataFrame.from_dict(file_name_and_text, orient='index')
             .reset_index().rename(index = str, columns = {'index': 'file_name', 0: 'title'}))

script_title_df = pd.merge(title_df, script_df, on='file_name', how ='outer')
#print(script_title_df.head())

def title_cleanup(df):
    #removing &amp
    df.replace('&amp;', '', regex=True, inplace=True)
    #removing HTML gutter
    df.replace(to_replace=['<b>', '</b>', '<!--', '.href', '!='],   value= '', regex=True, inplace=True)
    # remove new line characters
    df.replace(to_replace=[r'\\t|\\n|\\r', '\t|\n|\r', 'if (window top)top.location=location// -->'], value='', regex=True, inplace=True)
    #removing other items from titles for merging
    df['title'].replace('THE|the', '', regex=True, inplace=True)
    # change all letters to lowercase
    df['title'] = [name.lower() for name in df['title']]
    # Replace the &#39 values
    df.replace('&#39;', "'", regex=True, inplace=True)
    # remove the commas
    df['title'].replace(',', '', regex=True, inplace=True)
    return df

# Cleanup the film titles in both dataframes for an easier merge
script_title_df = title_cleanup(script_title_df)
bechdel_df = title_cleanup(bechdel_df)

# Merge the script title dataframe and the bechdel dataframe on 'title' field
bechdel_script_df = pd.merge(script_title_df, bechdel_df, left_on='title', right_on='title')

# Transform filename field into path to file, for easier access in the future
def fpath(filename):
    return ('data/input/scripts/'+filename)
bechdel_script_df['file_name'] = bechdel_script_df['file_name'].apply(fpath)

# Drop duplicates on title field
bechdel_script_df.drop_duplicates(subset = 'title', keep = 'first', inplace=True)

# Drop the script column from this dataframe
bechdel_script_df.drop(columns = 'script', inplace = True)

# Save dataframe to csv file.
bechdel_script_df.to_csv('data/input/bechdel_script_kaggle.csv')


# For further exploration :

print(bechdel_script_df.shape)
print(bechdel_script_df['rating'].value_counts())
#print(bechdel_script_df['file_name'].head())
