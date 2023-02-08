import os

import pandas as pd
import torch
from torch.utils.data import DataLoader
from typing import Union
from tqdm import tqdm

from script_parsing.parsed_script_dataset import TaggedLines, get_dataset
from script_parsing.parsing_model import BertClassifier, SentenceTransformerClassifier


def get_intermediate_dataset(
    config: dict,
    model: Union[SentenceTransformerClassifier, BertClassifier],
    device: torch.device,
    save_freq: int = 100,
):
    """Returns a dataset of embeddings. If the dataset is already saved, it
    is loaded and returned, else it is built by feeding the lines to the first
    half of the model (intermediate_forward), i.e. the bert/sentence bert part.
    Given the computing of this dataset can be quite long, it is regularly saved
    such as if for whatever reason the program is stopped while building this dataset,
    the computations will start from where it was stopped during the next launch.

    Args:
        config (dict): config yaml file imported as a dict
        model (Union[SentenceTransformerClassifier, BertClassifier]): model used to
            compute the embeddings
        device (torch.device): can be 'cpu' or 'cuda:i' according to gpus available
        save_freq (int, optional): Saves the results every save_freq embeddings. Defaults to 100.

    Returns:
        _type_: _description_
    """
    tagged_lines: TaggedLines = get_dataset(config)
    batch_size = config["script_parsing_model"]["batch_size"]

    embeddings_path = os.path.join(
        config["paths"]["script_parsing_folder"],
        f'{config["names"]["dataset_embeddings"].split(".pt")[0]}_seed_{config["script_parsing_model"]["seed"]}_sample_{config["script_parsing_model"]["dataset_percentage"]}.pt',
    )

    if os.path.exists(embeddings_path):
        all_embeddings = torch.load(embeddings_path)
        # to find where is the last computed embedding (in case program was stopped in the middle),
        # we suppose that if the sum of the composants of the embedding equals 0, it wasn't computed
        sum_of_embeddings_per_sentence = list(all_embeddings.sum(dim=1).numpy())
        if 0.0 not in sum_of_embeddings_per_sentence:
            # means the embeddings matrix is already completely computed
            return LinesEmbeddingsDataset(all_embeddings, tagged_lines.data)

        # If we need to continue from the middle :
        start_index = sum_of_embeddings_per_sentence.index(0.0)
        tagged_lines.truncate_beginning(start_index)

    else:
        all_embeddings = torch.zeros(len(tagged_lines), model.output_embeddings_dim)
        start_index = 0

    loader = DataLoader(
        dataset=tagged_lines,
        batch_size=batch_size,
        shuffle=False,
    )

    for batch_idx, batch in tqdm(
        enumerate(loader), total=len(tagged_lines) // batch_size
    ):
        sentences, labels = batch
        labels = labels.to(device)
        current_batch_size = len(sentences)

        # compute embeddings
        embeddings = model.intermediate_forward(sentences)

        all_embeddings[
            start_index
            + batch_idx * batch_size : start_index
            + batch_idx * batch_size
            + current_batch_size
        ] = embeddings

        if batch_idx % save_freq == 0:
            torch.save(all_embeddings, embeddings_path)

    torch.save(all_embeddings, embeddings_path)

    return LinesEmbeddingsDataset(all_embeddings, tagged_lines.data)


class LinesEmbeddingsDataset(torch.utils.data.Dataset):
    """Dataset containing the embeddings of the coherent script's lines and their labels."""

    def __init__(
        self,
        embeddings: torch.Tensor,
        labels: pd.DataFrame,
        labels_column_name: str = "labels",
    ):
        if labels_column_name not in labels.columns:
            raise ValueError(
                f"{labels_column_name} was passed as the name for the lines column \
                but is not a column of the passed dataframe which has the following columns : {labels.columns})."
            )
        if len(labels.index) != embeddings.shape[0]:
            raise ValueError(
                f"Lines and embeddings should have the same length but got length {len(labels.index)} and {embeddings.shape[0]}."
            )

        self.labels = labels
        self.embeddings = embeddings
        self.labels_column_name = labels_column_name
        self.labels = self.labels.reset_index()

    def __len__(self):
        return len(self.labels.index)

    def __getitem__(self, idx):
        return (
            self.embeddings[idx],
            self.labels.loc[idx][self.labels_column_name],
        )


def freeze_pretrained_model_part(
    model: Union[SentenceTransformerClassifier, BertClassifier],
) -> None:
    """Prevents the weights of the bert model contained in our model
    to be updated during the backpropagation.

    Args:
        model (Union[SentenceTransformerClassifier, BertClassifier]): model to freeze

    Raises:
        ValueError: model is not a SentenceTransformerClassifier or BertClassifier
    """
    if isinstance(model, BertClassifier):
        model.bert.requires_grad_(False)
    elif isinstance(model, SentenceTransformerClassifier):
        model.sentence_bert.requires_grad_(False)
    else:
        raise ValueError(
            "Model should be a BertClassifier or a SentenceTransformerClassifier."
        )


# Currently this function is unused as we never need to perform backprop
# after disabling it but it could be useful one day
def unfreeze_pretrained_model_part(
    model: Union[SentenceTransformerClassifier, BertClassifier],
) -> None:
    """Reauthotize the updating of the weights of the bert model
    contained in our model.

    Args:
        model (Union[SentenceTransformerClassifier, BertClassifier]): model to freeze

    Raises:
        ValueError: model is not a SentenceTransformerClassifier or BertClassifier
    """
    if isinstance(model, BertClassifier):
        model.bert.requires_grad_(True)
    elif isinstance(model, SentenceTransformerClassifier):
        model.sentence_bert.requires_grad_(True)
    else:
        raise ValueError(
            "Model should be a BertClassifier or a SentenceTransformerClassifier."
        )


if __name__ == "__main__":
    import time
    import configue

    config = configue.load("parameters.yaml")
    bert_classifier = SentenceTransformerClassifier(config)
    device = torch.device("cpu")
    start = time.time()
    print("Start :", start)
    get_intermediate_dataset(config, bert_classifier, device)
    print("Done. Time :", time.time() - start)
