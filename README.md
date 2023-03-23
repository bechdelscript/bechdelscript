# Bechdel Script Tester

## Introduction
Have you ever wondered how many of your favorite movies pass the Bechdel Test ? Or maybe you don't know what the Bechdel Test is all about !

The Bechdel-Wallace Test is a tool aiming to estimate how much space and importance we give to female protagonists in the media, and more specifically in movies. It was first introduced in one of Alison Bechdel's comics, *Dykes to Watch Out For*. More information can be found [here](https://bechdeltest.com).

We consider that a movie passes the Bechdel Test if it matches the following criteria :
- It has at least two named women characters,
- They speak at least once with one another,
- About something different than a man.

This git repository, and associated website : ... bring to light part of the answer. This work, given a movie script file, returns a Bechdel score prediction, along with the different characters and scenes in the movie that pass - or refute - the test.

## Name
Bechdel Script Tester

## Description
If you are just looking to test your favorite movie, check out the front-end side of this project : ....
If you are curious to see how it works, or if you would like to improve this tool, this repository is the way to go. The structure is as follows :
- The [front_end](front_end/) folder is at the root of the website.
- The [back_end](back_end/) folder is where the magic happens !
Within the back end files, you'll find the following structure :
- A [data](back_end/data) folder, filled with both input and output data (more on that below).
- The [dataset_building](back_end/dataset_building) folder, necessary to create a script dataset used to train our models and quantify the project's performance.
- The [gender](back_end/gender), [script_parsing](back_end/script_parsing) and [topic_modeling](back_end/topic_modeling) folders, which respectively focus on one third of the criteria a movie must match to pass the test.
- The [api](back_end/api) folder which creates the API the website relies on.
- The [parameters.yaml](back_end/parameters.yaml) file, used to choose the parameters you want to run the main script on. This includes the different methods used to estimate the different criteria, as well as the harshness of the criteria. (ajouter trucs)
- The [performance.py](back_end/performance.py) script computes the confusion matrix of our work, based on the official Bechdel website scores.
- The [screenplay_classes.py](back_end/screenplay_classes.py) file is the heart of this project. In it, we create the Script object, and with it the different methods needed to properly parse a text file into a script, and to evaluate which criteria the script validates.
- Finally, the [main.py](back_end/main.py) file, which you can run to test a random movie from the database, or that you can run on a specific movie using  arguments.

## Visuals
?

## Installation
The [requirements.txt](requirements.txt) file, run with 'pip3 install -r requirements.txt', allows you to download most of the needed modules to use this code. However, two other models need to be imported :
- neuralcoref
- le modèle de parsing?

## Contributing
If you would like to improve on this project, feel free to do so, while ensuring you respect the license below. Please remember to credit the project authors.

## Authors and acknowledgment
The three authors of this project are listed as contributors on this repository : Lucie Clemot, Sacha Muller, Guilhem Prince.
This open source contribution and project is the result of an academic project which took place in the French engineering school CentraleSupélec.
We would like to give a shoutout to the school, along with the company that helped us build this tool : Illuin Technology. More specifically, thank you to Theo Rubenach for your help and guidance.

## License
MIT License

Copyright (c) 2020 Illuin Technology

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Project status
fini?


- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/index.html)