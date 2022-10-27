
"""L'objectif de ce script est de nettoyer les noms de fichiers scripts et bechdel et de merge les deux
bases de données sur le titre."""

import pandas as pd
import os
import re
import warnings
warnings.filterwarnings("ignore")

bechdel_df = pd.read_csv('data/Bechdel_db.csv', index_col='id')
bechdel_df.drop(columns='Unnamed: 0', axis=1, inplace=True)

file_names = os.listdir('data/Scripts/')
# Create Dictionary for File Name and Text
file_name_and_text = {}
for file in file_names: 
    if not file.startswith('.'): 
        with open('data/Scripts/' + file, "r", encoding="utf8") as target_file:
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
        with open('data/Scripts/' + file, "r", encoding="utf8") as target_file:
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
    return df

script_title_df = title_cleanup(script_title_df)
#print(script_title_df.columns)


# Rename the film names in the ebchdel_df dataframe
bechdel_df['title'].replace('THE|the|,the', '', regex=True, inplace=True)
bechdel_df['title'].replace(',', '', regex=True, inplace=True)
bechdel_df.replace('&amp;', '', regex=True, inplace=True)
bechdel_df.replace('&#39;', "'", regex=True, inplace=True)
bechdel_df['title'] = [name.lower() for name in bechdel_df['title']]

#print(script_title_df['title'].sample(5))
#print(bechdel_df.sample(5))

bechdel_script_df = pd.merge(script_title_df, bechdel_df, left_on='title', right_on='title')

def fpath(filename):
    return ('data/Scripts/'+filename)

bechdel_script_df['file_name'] = bechdel_script_df['file_name'].apply(fpath)

bechdel_script_df.drop(columns = 'script', inplace = True)
#print(bechdel_script_df.columns)
#print(bechdel_script_df['rating'].value_counts())
#print(bechdel_script_df['file_name'].head())

bechdel_script_df.to_csv('data/bechdel_script_1.csv')