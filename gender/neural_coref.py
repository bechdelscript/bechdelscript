import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
from tqdm import tqdm_notebook
from typing import List

# There are few out-of-the-box libraries that support or specifically built for coreference resolution. Most wide-known are [CoreNLP](https://stanfordnlp.github.io/CoreNLP/coref.html), [Apache OpenNLP](https://opennlp.apache.org/) and [neuralcoref](https://github.com/huggingface/neuralcoref). In this short notebook, we will explore neuralcoref 3.0, a coreference resolution library by Huggingface.
#
# First, let's install neuralcoref 3.0. To do this, we need to slightly downgrade spacy (neuralcoref is not compatible with the new cymem version used by the current version of spacy).

MODEL_URL = "https://github.com/huggingface/neuralcoref-models/releases/download/en_coref_md-3.0.0/en_coref_md-3.0.0.tar.gz"

# ## A small neuralcoref tutorial
#
# How does this lib work? Let's find out!
#
# First,we need to load the model:

import spacy
import neuralcoref

nlp = spacy.load("en")
neuralcoref.add_to_pipe(nlp)

# Now we need a sentence with coreference.
#
# A boring theoretical reminder: coreference happens when* two different words denote the same entity* in the real world. In this competition, we deal with pronomial coreference. It comes in two flavors:
# 1. *Anaphora*, when a pronoun follows a noun: "John looked at me. He was clearly angry".
# 2. *Cataphora*, when it is vice versa: "When she opened the door, Jane realized that it was cold outside"


# Using neuralcoref is not really different from using plain spacy.
def list_pronouns_coref(list_text: List[str]):
    dico = {}
    for text in list_text:
        doc = nlp(text)
        # To check if any kind of coreference was detected, `has_coref` attribute of the extension (referred to as `_`) is used:
        if doc._.has_coref:
            clusters = doc._.coref_clusters
            # You can get the entity and coreferring pronouns from these clusters by simple indexing. The objects returned are in fact ordinary spacy `span`s.
            for i in range(len(clusters)):
                if str(clusters[i].main) in dico.keys():
                    pronouns = clusters[i].mentions + list(dico[str(clusters[i].main)])
                    dico[str(clusters[i].main)] = pronouns
                else:
                    dico[str(clusters[i].main)] = clusters[i].mentions
    for k in dico.keys():
        dico[k] = map(str, dico[k])
        dico[k] = set(dico[k])
    return dico


# ## Deciding which entity the pronoun refers to
#
# In competition data, the position of the entities and the pronoun comes as an offset from the beginning. Let's write a small function that will resolve coreference in a string and decide whether any of detected coreferring entities correspond to given offsets.


def is_inside(offset, span):
    return offset >= span[0] and offset <= span[1]


def is_a_mention_of(sent, pron_offset, entity_offset_a, entity_offset_b):
    doc = nlp(sent)
    if doc._.has_coref:
        for cluster in doc._.coref_clusters:
            main = cluster.main
            main_span = main.start_char, main.end_char
            mentions_spans = [
                (m.start_char, m.end_char)
                for m in cluster.mentions
                if (m.start_char, m.end_char) != main_span
            ]
            if is_inside(entity_offset_a, main_span) and np.any(
                [is_inside(pron_offset, s) for s in mentions_spans]
            ):
                return "A"
            elif is_inside(entity_offset_b, main_span) and np.any(
                [is_inside(pron_offset, s) for s in mentions_spans]
            ):
                return "B"
            else:
                return "NEITHER"
    else:
        return "NEITHER"


# A small test:

# "The doctor came in. She held a paper in her hand."
# entity_offset_a = test_sent.index("Kat")
# entity_offset_b = test_sent.index("Pat")
# pron_offset = test_sent.index("her")

# print(is_a_mention_of(test_sent, pron_offset, entity_offset_a, entity_offset_b))

test = [
    "The strobe of the red light reveals a man floating at the helm, slowly spinning. He is dead, perfectly preserved in the cold vacuum of space. His eyes are empty black pits and his mouth hangs open in a scream: DR. WILLIAM WEIR.",
    "Weir opens his eyes, waking from dream. Sweat beads his ascetic, etched face. Many years a scientist.",
    "He turns on the bedside lamp, revealing a couple's apartment. Decorated by a woman, but Weir is alone, unless you count photographs. His nightstand looks like a shrine to a beautiful woman.",
    "Weir reaches to the stand. Picks up..."
    "Weir opens his eyes, waking from dream. Sweat beads his ascetic, etched face. Many years a scientist.",
    "Justin jerks his hands to his ears, closes his eyes...",
]

# print(list_pronouns_coref(test))
