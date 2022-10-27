"""Objectif du script : renommer tous les scripts de la base de donnée trouvée sur kaggle au lien suivant :
https://www.kaggle.com/datasets/parthplc/movie-scripts?resource=download
Utilisation du script sur ce git :
https://github.com/Umairican/The-Bechdel-Test/blob/main/data/Scripts/script_namer.ipynb
Et de créer la base de données de films répertoriés dans la db Bechdel :
https://bechdeltest.com/api/v1/doc#getMovieByImdbId"""

import pandas as pd
import os
import yaml

config = yaml.safe_load(open('parameters.yaml'))

def rename():
    file_names = os.listdir(config['paths']['path_to_kaggle_scripts'])

    for file in file_names:
        if not file.startswith('.'):
            try:
                with open(file) as f:
                    first_line = f.readline().strip()
                    os.rename(config['path_to_kaggle_scripts']+file, (str(first_line) + '.txt').upper())
            except:
                print(f'{file} could not be renamed. Please check manually')

#rename()

def create_db():
    bechdel_df = pd.read_json('http://bechdeltest.com/api/v1/getAllMovies')
    print(bechdel_df.head())
    print(bechdel_df.shape)
    bechdel_df.to_csv(config['paths']['input_folder_name']+config['names']['bechdel_db_name'])

#create_db()

