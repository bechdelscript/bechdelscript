import pandas as pd
import nltk

tokens = pd.read_csv("pronouns.csv", header=None)
tokens = [token[0] for token in tokens.values]

pronoun_to_gender = {
    "he": "M",
    "his": "M",
    "him": "M",
    "man": "M",
    "she": "F",
    "her": "F",
    "hers": "F",
    "woman": "F",
    "they": "NB",
    "them": "NB",
    "their": "NB",
    "theirs": "NB",
}

"""Given a list of narrative passages, this function identifies the most frequently used gendered pronouns included in 
paragraphs where the character's name appears. Then, we use the most frequent gender associated with narrative passages as our
prediction."""


def pronoun_id(paragraphs, name, tokens):
    freq_gender = {"M": 0, "F": 0, "NB": 0}
    paragraphs = [para for para in paragraphs if name in para]
    for para in paragraphs:
        freq_tokens = {}
        for word in nltk.word_tokenize(para):
            for token in tokens:
                if token == word.lower():
                    try:
                        freq_tokens[token] += 1
                    except:
                        freq_tokens[token] = 1
        freq_tokens = {
            pronoun_to_gender[key]: freq_tokens[key] for key in freq_tokens.keys()
        }
        freq_gender[max(freq_tokens, key=lambda k: freq_tokens[k])] += 1
    res = max(freq_gender, key=lambda k: freq_gender[k])
    return res


paragraphs = [
    "John is blabla. He is blabla. His hair. His daughter is also there. She is blabla.",
    "John is a man.",
    "Her hair falls down.",
    "John is a she. She used...",
]

print(pronoun_id(paragraphs, "John", tokens))
