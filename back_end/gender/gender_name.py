import string
import nltk
import nltk.classify
import pandas as pd
from sklearn.model_selection import train_test_split
import requests
import os

"""This script creates a gender classifier based on character names.
It is heavily inspired from the following git repository."""
# https://github.com/ellisbrown/name2gender/tree/master/naive_bayes
"""The used dataset was found on data.gouv.fr, the french government open data resource."""

# The following dictionary represents gendered keywords for when characters are called by their last name.
keywords = {
    "f": ["Mrs.", "Mrs", "mrs.", "mrs", "MRS.", "MRS", "MOTHER"],
    "m": ["Mr.", "Mr", "mr.", "mr", "MR.", "MR", "FATHER"],
}


def load_database(config: dict) -> pd.DataFrame:
    """This function creates the name to gender database."""
    # If the database isn't in the data folder already, the following will download it.

    path = os.path.join(
        config["paths"]["input_folder_name"], config["names"]["list_prenoms"]
    )

    if config["names"]["list_prenoms"] not in config["paths"]["input_folder_name"]:
        url = "https://www.data.gouv.fr/fr/datasets/r/55cd803a-998d-4a5c-9741-4cd0ee0a7699"
        r = requests.get(url, allow_redirects=True)
        open(path, "wb").write(r.content)

    # Read the original gender database.
    gender_data = pd.read_csv(
        path,
        encoding="latin-1",
        header=0,
        names=["name", "gender", "language", "frequency"],
        delimiter=";",
    )

    # Clean this database by dropping na values and standardize the mixed names.
    gender_data.dropna(inplace=True)
    gender_data["gender"].replace("m,f", "f,m", inplace=True)

    return gender_data


def create_test_train(gender_data: pd.DataFrame):
    """This function creates the train and test set for the classifier."""
    # Create the X and Y vectors, equal to the name and gender columns
    X = gender_data.iloc[:, :1]
    Y = gender_data.iloc[:, 1:]

    # Create the train and test set.
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=0.3, random_state=0
    )

    # Create the train dataframe, transform it into a list of tuples.
    train = pd.merge(X_train, y_train, right_index=True, left_index=True)
    train = list(train.itertuples(index=False, name=None))
    # Apply _gender_features to the names in train.
    train_features = nltk.classify.apply_features(
        create_gender_features, train, labeled=True
    )

    # Do the same for the test set.
    test = pd.merge(X_test, y_test, right_index=True, left_index=True)
    test = list(test.itertuples(index=False, name=None))
    test_features = nltk.classify.apply_features(
        create_gender_features, test, labeled=True
    )

    return (train_features, test_features)


def create_gender_features(name: str) -> dict:
    """This function creates features based on the name field (suffixes, first and last letter...)."""
    features = {}
    features["last_letter"] = name[-1].lower()
    features["first_letter"] = name[0].lower()
    for letter in string.ascii_lowercase:
        features["count(%s)" % letter] = name.lower().count(letter)
        features["has(%s)" % letter] = letter in name.lower()
    # names ending in -yn are mostly female, names ending in -ch ar mostly male, so add 2 more features
    features["suffix2"] = name[-2:]
    features["suffix3"] = name[-3:]
    features["suffix4"] = name[-4:]
    return features


def load_classifier():
    """This loads the classifier"""
    gender_data = load_database()
    # Create the train and test features sets, and train a Naive bayes classifier on the training set.
    train_features, test_features = create_test_train(gender_data)
    classifier = nltk.NaiveBayesClassifier.train(train_features)
    return classifier


def _classify(name: str, classifier) -> tuple:
    """Given a name and a classifier, this returns the predicted ouput, and the probability"""
    # The following two conditions cover the instances where a character is called Mrs. something or Mr. something.
    if any(ele in name for ele in keywords["f"]):
        guess = "f"
        prob = 1
    elif any(ele in name for ele in keywords["m"]):
        guess = "m"
        prob = 1
    # The following statement covers all other instances, and uses the classifier.
    else:
        _name = create_gender_features(name.split()[0])
        dist = classifier.prob_classify(_name)
        m, f, b = dist.prob("m"), dist.prob("f"), dist.prob("f,m")
        d = {m: "m", f: "f", b: "f,m"}
        # If the name was most likely mixed, we select the next most likely gender.
        prob = max(m, f)
        guess = d[prob]
    return guess, prob


if __name__ == "__main__":
    classifier = load_classifier()
