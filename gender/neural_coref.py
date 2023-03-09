from tqdm import tqdm_notebook
from typing import List

MODEL_URL = "https://github.com/huggingface/neuralcoref-models/releases/download/en_coref_md-3.0.0/en_coref_md-3.0.0.tar.gz"


def list_pronouns_coref(list_text: List[str], nlp) -> dict:
    "Given a list of strings, returns a dictionary with names as keyrs and coreferences as values."
    dico = {}
    for text in list_text:
        doc = nlp(text)
        if doc._.has_coref:
            clusters = doc._.coref_clusters
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
