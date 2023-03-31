# Bechdel Script Tester

## Introduction :wave:
Have you ever wondered how many of your favorite movies pass the Bechdel Test ? Or maybe you don't know what the Bechdel Test is all about !

The Bechdel-Wallace Test is a tool aiming to estimate how much space and importance we give to female protagonists in the media, and more specifically in movies. It was first introduced in one of Alison Bechdel's comics, *Dykes to Watch Out For*. More information can be found [here](https://bechdeltest.com).

We consider that a movie passes the Bechdel Test if it matches the following criteria :
- It has at least two named women characters (resulting in a score of 1),
- They speak at least once with one another (resulting in a score of 2),
- About something different than a man (resulting in a score of 3).

This git repository, and associated website : ... bring to light part of the answer. This work, given a movie script file, returns a Bechdel score prediction, along with the different characters and scenes in the movie that pass - or refute - the test.

## Name
Bechdel Script Tester

## Disclaimers

This work is imperfect and has flaws we might not have in mind. We still considered that it was worth sharing, since it can be useful to most, and help make the Bechdel test more accessible.

Please note that, in order to promote inclusivity, the module can gender a character as a Woman, a Man or a Non-Binary individual. However, we have not implemented Bechdel rules that allow a conversation between two gender minorities (a woman and a non-binary person, for instance) to validate the second criteria. That is because we felt it was out of our scope to swerve away from the original test that much. However, we feel that as Non-binary folk representation in movies is increasing, it would be ideal to update the test rules and implement our module accordingly.

## Description :writing_hand:
If you are just looking to test your favorite movie, check out the front-end side of this project : ....
If you are curious to see how it works, or if you would like to improve this tool, this repository is the way to go. The structure is as follows :
- The [front_end](front_end/) folder is at the root of the website.
- The [back_end](back_end/) folder is where the magic happens !


## Back end code structure and files :file_folder:

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

### Installation
The [requirements.txt](requirements.txt) file, run with `pip3 install -r requirements.txt`, allows you to download most of the needed modules to use this code.
However, two other models need to be imported :
- If you choose to use the Co-reference gender prediction method, the `neuralcoref` module requires a python version lower than 3.7. Then, it can be downloaded using `python -m spacy download en` and `nltk.download('punkt')` in a terminal.
- The parsing model can be found [here](https://drive.google.com/file/d/1u8tJT1nlmsQJQ0fA1OW0AUlCjfi9Bdzm/view?usp=share_link) and can be downloaded by running [this script](to/create).

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


## Contributing :open_hands:
If you would like to improve on this project, feel free to do so, while ensuring you respect the license below. Please remember to credit the project authors.

## Authors and acknowledgment :handshake:
The three authors of this project are listed as contributors on this repository : Lucie Clemot [(@osnapitzlu)](https://github.com/osnapitzlu), Sacha Muller [(@sachamuller)](https://github.com/sachamuller), Guilhem Prince [(@guilhemprince)](https://github.com/guilhemprince).
This open source contribution and project is the result of an academic project which took place in the French engineering school CentraleSupélec.
We would like to give a shoutout to the school, along with the company that helped us build this tool : Illuin Technology. More specifically, thank you to Theo Rubenach for your help and guidance.

## License
[See license here.](LICENSE.txt)

## Project status
This project, along with the front-end website, will not be worked on further by our team. Any potential updates would have to be done by the open source community.
