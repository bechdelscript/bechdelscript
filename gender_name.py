import csv
import string
import unicodedata
import nltk
from nltk.corpus import names
import nltk.classify
import pandas as pd
from sklearn.model_selection import train_test_split

#https://github.com/ellisbrown/name2gender/tree/master/naive_bayes

def save_gender_data():
    # name-gen dict
    name_gender = {}

    # helper cleaning function (lowercase, unicode->ascii)
    def clean(s):
        uncoded = ''.join(
            c for c in unicodedata.normalize('NFD', s)
            if unicodedata.category(c) != 'Mn'
            and c in string.ascii_letters
        )
        return uncoded.lower()

    def to_csv(data, filename):
        with open(filename, 'w', newline='') as out:
            writer = csv.writer(out, delimiter=',')
            for k,v in data:
                writer.writerow([k,v])

    # download names corpus
    nltk.download("names")

    # add nltk names
    male_names = names.words('male.txt')
    female_names = names.words('female.txt')
    labeled_names = ([(name, 'male') for name in male_names] + [(name, 'female') for name in female_names])

    for name,gender in labeled_names:
        name = clean(name)
        name_gender[name] = gender
    #     print(name)
    print(len(name_gender))

    to_csv(name_gender.items(), "data/input/name_gender.csv")

#save_gender_data()

# Read the original gender database
gender_data = pd.read_csv("data/input/name_gender.csv", header=None, names=['name', 'gender'])

# Clean this database by dropping na values.
gender_data.dropna(inplace=True)

# Inspect values in gender_data
print(gender_data['gender'].value_counts())

def undersample():
    male  = gender_data.loc[gender_data['gender'] == 'male']
    n = len(male)
    female = gender_data.loc[gender_data['gender'] == 'female']
    female = female.sample(n)
    test_under = pd.concat([female, male], axis=0)
    return(test_under)

def oversample():
    male  = gender_data.loc[gender_data['gender'] == 'male']
    female = gender_data.loc[gender_data['gender'] == 'female']
    n = len(female)
    male = male.sample(n, replace=True)
    test_over = pd.concat([female, male], axis=0)
    return(test_over)

# This function creates the trin and test set for the classifier
def create_test_train():
    gender_data = undersample()
    # Create the X and Y vectors, equal to the name and gender columns
    X = gender_data.iloc[:,:1]
    Y = gender_data.iloc[:,1:]

    # Create the train and test set
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=0)

    # Create the train dataframe, transform it into a list of tuples
    train = pd.merge(X_train, y_train, right_index = True, left_index =True)
    train = list(train.itertuples(index=False, name=None))
    # Apply _gender_features to the names in train
    train_features = nltk.classify.apply_features(_gender_features, train, labeled=True)

    # DO the same for the test set
    test = pd.merge(X_test, y_test, right_index = True, left_index =True)
    test = list(test.itertuples(index=False, name=None))
    test_features = nltk.classify.apply_features(_gender_features, test, labeled=True)

    return(train_features, test_features)

# This function creates features based on the name field (suffixes, first and last letter...)
def _gender_features(name):
    features = {}
    features["last_letter"] = name[-1].lower()
    features["first_letter"] = name[0].lower()
    for letter in string.ascii_lowercase:
        features["count(%s)" % letter] = name.lower().count(letter)
        features["has(%s)" % letter] = (letter in name.lower())
    # names ending in -yn are mostly female, names ending in -ch ar mostly male, so add 2 more features
    features["suffix2"] = name[-2:]
    features["suffix3"] = name[-3:]
    features["suffix4"] = name[-4:]
    return features

# Given a name and a classifier, this prints out the name, the predicted ouput, and the probability.
def _classify(name, classifier):
    _name = _gender_features(name)
    dist = classifier.prob_classify(_name)
    m, f = dist.prob("male"), dist.prob("female")
    d = {m: "male", f: "female"}
    prob = max(m,f)
    guess = d[prob]
    print("%s -> %s (%.2f%%)" % (name, guess, prob * 100))
    return guess, prob

# Given a list of names and a classifier, this prints out _classify for each of the names.
def classify(names, classifier):
    for name in names:
         _classify(name, classifier)
    print("\nClassified %d names" % (len(names)))


# Create the train and test features sets, and train a Naive bayes classifier on the training set.
train_features, test_features = create_test_train()
classifier = nltk.NaiveBayesClassifier.train(train_features)
# Print the accuracy computed with the test_features set.
print("Classifier accuracy percent:",(nltk.classify.accuracy(classifier, test_features))*100)

# Show the most informative features of our classifier.
classifier.show_most_informative_features(15)

# définir une fonction qui classifie sur de nouveaux noms
name_test = ['marie', 'jack', 'andre', 'bill', 'paul', 'mike', 'sara', 'joan', 'elaine', 'willie']
print(classify(name_test, classifier))