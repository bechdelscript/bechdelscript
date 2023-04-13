# Bechdel Script Tester

## :wave: Introduction 
Have you ever wondered how many of your favorite movies pass the Bechdel Test ? Or maybe you don't know what the Bechdel Test is all about !

The Bechdel-Wallace Test is a tool aiming to estimate how much space and importance we give to female protagonists in the media, and more specifically in movies. It was first introduced in one of Alison Bechdel's comics, *Dykes to Watch Out For*. More information can be found [here](https://bechdeltest.com).

We consider that a movie passes the Bechdel Test if it matches the following criteria :
- It has at least two named women characters (resulting in a score of 1),
- They speak at least once with one another (resulting in a score of 2),
- About something different than a man (resulting in a score of 3).

This git repository, and associated website [here](http://34.105.15.131/) bring to light part of the answer. This work, given a movie script file, returns a Bechdel score prediction, along with the different characters and scenes in the movie that pass - or refute - the test.

## Disclaimers

This work is imperfect and has flaws we might not have in mind. We still considered that it was worth sharing, since it can be useful to most, and help make the Bechdel test more accessible.

Please note that, in order to promote inclusivity, the module can gender a character as a Woman, a Man or a Non-Binary individual. However, we have not implemented Bechdel rules that allow a conversation between two gender minorities (a woman and a non-binary person, for instance) to validate the second criteria. That is because we felt it was out of our scope to swerve away from the original test that much. However, we feel that as Non-binary folk representation in movies is increasing, it would be ideal to update the test rules and implement our module accordingly.

## :writing_hand: Description 
If you are just looking to test your favorite movie, check out our website for the front-end side of this project : [http://34.105.15.131/](http://34.105.15.131/)
If you are curious to see how it works, or if you would like to improve this tool, this repository is the way to go. The structure is as follows :
- The [front_end](front_end/) folder is at the root of the website.
- The [back_end](back_end/) folder is where the magic happens !


## :file_folder: Back end code structure and files

### File and folders
Within the back end files, you'll find the following structure :
- A [data](back_end/data) folder, filled with both input and output data (more on that below).
- The [dataset_building](back_end/dataset_building) folder, necessary to create a script dataset used to train our models and quantify the project's performance.
- The [gender](back_end/gender), [script_parsing](back_end/script_parsing) and [topic_modeling](back_end/topic_modeling) folders, which respectively focus on one third of the criteria a movie must match to pass the test.
- The [api](back_end/api) folder which creates the API the website relies on.
- The [parameters.yaml](back_end/parameters.yaml) file, used to choose the parameters you want to run the main script on. This includes the different methods used to estimate the different criteria, as well as the harshness of the criteria (see Parameter choice below).
- The [performance.py](back_end/performance.py) script computes the confusion matrix of our work, based on the official Bechdel website scores.
- The [screenplay_classes.py](back_end/screenplay_classes.py) file is the heart of this project. In it, we create the Script object, and with it the different methods needed to properly parse a text file into a script, and to evaluate which criteria the script validates.
- Finally, the [main.py](back_end/main.py) file, which you can run to test a random movie from the database, or that you can run on a specific movie using arguments.

### Parameter choice
There are two ways to personalize the code's performance and the approach.
1. The first focuses on the test itself : how flexible are we willing to be regarding the criteria ? If two women have a conversation that also involves a man, but they exchange a couple of lines without his intervention, does it count as a score 2 ? If two women have a conversation and they exchange only a few lines about something else than a man, does it count as a score 3 ? To allow the user to answer these questions however they please, we introduced the concept of *Bechdel Test Rules*. In the [parameters file](back_end/parameters.yaml), the `bechdel_test_rules` section allows the user to choose the boolean values of `only_women_in_whole_scene` and `whole_conversation_not_about_men`, as well as `lines_of_dialogues_in_a_row` the number of successive lines from female characters needed to validate score 2 or 3, respectively without being interrupted by a man or without speaking about men.

2. The second focuses on how the code will implement these rules. There are three main steps applied to a script file before returning results :
    - The script parsing, which enables the code to identify the dialogues, the characters, the narrative passages...
    - The gender prediction, which, given a character, predicts what their gender is,
    - The topic modeling aspect, which given a dialogue, predicts if it does or doesn't concern men.

For these three steps, we have iterated from basic to elaborate methods to improve their performance. By default, the more elaborate methods are applied when running the code. The user can however choose to downgrade to the naive methods by updating the `used_methods`parameters in the [parameters file](back_end/parameters.yaml). More specifically, the user can :
- Choose a gender prediction method, between :
    - Name classification (`classify`): using a Machine Learning Classification approach (Naïve Bayes), this method predicts the character's gender based on their name.
    - Naive narrative (`narrative`): this method counts the pronouns used in narrative paragraphs the character is quoted in, and predicts their gender based on the most frequent pronouns.
    - Neural Co-reference (`coref`): this method used the [neuralcoref](https://github.com/huggingface/neuralcoref) module, which uses the NLP Library [SpaCy](https://spacy.io) to apply co-reference method to associate pronouns with the person they are referring to.
- Choose the parsing method, between :
    - The indentation based method (`reparse_with_ml= False`) which is based on decision rules and indentation frequency,
    - The Deep Learning method (to be used exclusively on script the indentation based method couldn't parse) (`reparse_with_ml = True`).

### Installation and Downloading of the dataset 
The [requirements.txt](requirements.txt) file, run with `pip3 install -r requirements.txt`, allows you to download most of the needed modules to use this code.
However, some other models and data need to be imported manually:
- If you choose to use the Co-reference gender prediction method, the `neuralcoref` module requires a python version lower than 3.7. Then, it can be downloaded using `python -m spacy download en` and `python -m nltk.downloader 'punkt'` in a terminal.

- The data folder is composed of different things : 
    - A lot of scripts, coming of different sources : `scripts_imsdb` or `scripts_kaggle`. Special mention to [The Internet Movie Script Database](https://imsdb.com/), that provides a gigantic amount of movie scripts. 
    - A CSV file `bechdel_db.csv`, containing all bechdel scores for the movies rated on the [Bechdel Test website](https://bechdeltest.com/). This data will be used as the ground truth to measures our performances later on. 
    - Another CSV file, `dataset.csv`, which corresponds to the merge of the movies for which :  
        1. We found a script, on IMSDb or Kaggle. 
        2. We have a gound truth score, available on the Bechdel Test website. 
    This file thus groups the movies on which our algorithm’s results can be compared to a certain truth. 

    First, you need to download the Kaggle scripts, that can be found [here](https://drive.google.com/drive/folders/16Ae_Dqz7RjFTXc7reiNvnHpXZ3jfkQhg?usp=share_link) and stored inside `data/input/scripts_kaggle`. Or you can run [this script](https://github.com/bechdelscript/bechdelscript/blob/main/download_kaggle_scripts.sh) with the following command (at the root):
    ``` 
    bash download_kaggle_scripts.sh
    ``` 

    Then, to download the IMSDb scripts and create the CSVs, you’ll have have to execute, from the root of the repository : 
    ``` 
    cd ./back_end/ 
    python -m dataset_building.build_dataset 
    ``` 

- You also need to download our parsing model, that can be found [here](https://drive.google.com/file/d/1u8tJT1nlmsQJQ0fA1OW0AUlCjfi9Bdzm/view?usp=share_link) and can be downloaded by running [this script](https://github.com/bechdelscript/bechdelscript/blob/main/download_model.sh), with the command :
``` 
bash download_model.sh 
``` 


### Usage
As specified above, you can run two scripts to test our algorithm : [main.py](back_end/main.py) and [performance.py](back_end/performance.py). You must be conscious that these scripts will use the parameters in the `parameters.yaml` file to run, so make sure you are using the ones you want.

The `main.py` script allows you to test a random movie. To execute the script, from the root of the repository, run the following commands :  
```
cd ./back_end/
python main.py
```
You might want to test our model on a precise movie, you can do that by specifying the `movie_name` or `script_filename` argument:
```
python main.py --movie_name "Cars 2"
python main.py --script_filename "Cars-2.txt"
```
You can also modify the number of validating scenes returned by the script, with the argument `nb_scenes`, of type `int`.

Running the `performance.py` without arguments will basically run the `main.py` script on each movie of your dataset, located at `back_end/data/input/dataset.csv`. That is to say, it will compute a score for each movie, compare it to the official score, and keep track of metrics such as the confusion matrix, accuracy, precision, recall and f1-score of our model. Results will be stored in `back_end/data/output/YYYY-MM-DD_HHmmSS`. It might run for a little while, depending on the chosen parameters. You can do this by running, from the root of the repository:  
```
cd ./back_end/
python performance.py
```
You might not want to test our performances on the whole dataset, but on a fraction of it : you can use the `nb_movies` argument. `random = False` means you would be mesuring performance on the `nb_movies` first rows of the dataset.
```
python performance.py --nb_movies 100 --random True
```
You can also measure performance on a subset of film of your choice, specifying the argument `script_filenames`, a string containing the filenames of your choice (with .txt), separated by commas, no spaces :
```
python performance.py --script_filenames "Jaws-2.txt,Alien.txt,Apocalypse-Now.txt"
```

### Run the webapp locally
To launch the website on localhost, nothing simpler : you just have to run the following commands in two distincts terminals.
```
cd ./front_end/
npm start
```
```
cd ./back_end/
uvicorn api.main:app --reload
```

## :chart_with_upwards_trend: Our Results 

The results were computed on our 694 movies of our dataset. Here is a summary of it all : 

| --- |Strict rules (True, True)| Intermediate rules (True, False)| Soft rules (False, False)|
|:----:|:----:|:----:|:----:|
|Definition Reminder| Women have to be alone and not mention a man the whole discussion. | Women have to be alone and should exchange 2 replicas without mentionning a man. | Women should exchange 2 replicas without mentionning a man. |
|**Accuracy**| **62%** | **65%** | **69%** | 
|Precision| 79% | 81% | 72% |
|Recall| 37% | 45% | 67% |
|**F1-score**| **50%** | **58%** | **69%** |
|True Positive| 137 | 164 | 248 |
|False Positive | 35 | 38 | 95 |
|True Negative | 292 | 289 | 232 |
|False Negative | 230 | 203 | 119 |

As we can see, the results are better with the 'soft configuration' of the Bechdel test, in terms of accuracy as well as F1-score. Please keep in mind that our goal was to help understand if a movie passes the Bechdel test or not by providing the needed information. On our web-app, these performances would be much greater with user's common sense and correction of characters' genders. 

You can find a more complete description of our results in the [backend/data/output](back_end/data/output) folder, where we ran are performances on the 694 movies of our dataset in each parameters' configurations.


## :open_hands: Contributing 
If you would like to improve on this project, feel free to do so, while ensuring you respect the license below. Please remember to credit the project authors.

## :handshake: Authors and acknowledgment 
The three authors of this project are listed as contributors on this repository : Lucie Clemot [(@osnapitzlu)](https://github.com/osnapitzlu), Sacha Muller [(@sachamuller)](https://github.com/sachamuller), Guilhem Prince [(@guilhemprince)](https://github.com/guilhemprince).
This open source contribution and project is the result of an academic project which took place in the French engineering school CentraleSupélec.
We would like to give a shoutout to the school, along with the company that helped us build this tool : [Illuin Technology](https://www.illuin.tech). More specifically, thank you to Theo Rubenach [(@Toz3wm)](https://github.com/Toz3wm) for your help and guidance.

## License
[See license here.](LICENSE.txt)

## Project status
This project, along with the front-end website, will not be worked on further by our team. Any potential updates would have to be done by the open source community.
