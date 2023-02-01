from collections import OrderedDict

import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
from transformers import BertModel, BertTokenizer


def get_model(config, device=None):
    if config["script_parsing_model"]["model_architecture"]["use_sentence_transformer"]:
        return SentenceTransformerClassifier(config, device)
    else:
        return BertClassifier(config, device)


class BertClassifier(nn.Module):
    def __init__(self, config, device=None):
        super(BertClassifier, self).__init__()

        pretrained_model_name = config["script_parsing_model"]["model_architecture"][
            "bert_pretrained_model_name"
        ]

        self.bert = BertModel.from_pretrained(pretrained_model_name)
        self.pretrained_tokenizer = BertTokenizer.from_pretrained(pretrained_model_name)
        self.output_embeddings_dim = self.bert.config.hidden_size  # base bert output

        self.fully_connected = build_fully_connected(
            config["script_parsing_model"]["model_architecture"][
                "fully_connected_hidden_layers"
            ],
            self.output_embeddings_dim,
            config["script_parsing_model"]["model_architecture"]["nb_output_classes"],
        )
        self.device = device

    def tokenizer(self, list_sentences):
        return self.pretrained_tokenizer(
            list_sentences, return_tensors="pt", padding=True, truncation=True
        )

    def forward(self, list_sentences):
        tokenized_sentences = self.tokenizer(list_sentences)
        if self.device is not None:
            tokenized_sentences = tokenized_sentences.to(self.device)

        # model_output dimensions : batch_size * nb tokens * bert_output_dim (=768)
        model_output = self.bert(**tokenized_sentences).last_hidden_state.detach()

        # to give the embeddings to a fully connected layer we need them all to have the same
        # dimension : we apply a mean over the dimension that has the size of nb tokens (~= nb of words)
        model_output = torch.mean(model_output, dim=1)

        model_output = self.fully_connected(model_output)

        return model_output

    def intermediate_forward(self, list_sentences):
        tokenized_sentences = self.tokenizer(list_sentences)
        if self.device is not None:
            tokenized_sentences = tokenized_sentences.to(self.device)

        # model_output dimensions : batch_size * nb tokens * bert_output_dim (=768)
        model_output = self.bert(**tokenized_sentences).last_hidden_state.detach()

        # to give the embeddings to a fully connected layer we need them all to have the same
        # dimension : we apply a mean over the dimension that has the size of nb tokens (~= nb of words)
        return torch.mean(model_output, dim=1)

    def fully_connected_forward(self, embeddings):
        return self.fully_connected(embeddings)


class SentenceTransformerClassifier(nn.Module):
    def __init__(self, config, device=None):
        super(SentenceTransformerClassifier, self).__init__()

        pretrained_model_name = config["script_parsing_model"]["model_architecture"][
            "sentence_transformer_pretrained_model_name"
        ]

        self.sentence_bert = SentenceTransformer(pretrained_model_name, device=device)
        # SentenceTransformer[1] is the Pooling layer, its attribute word_embedding_dimension is the size of the embeddings
        self.output_embeddings_dim = self.sentence_bert[1].word_embedding_dimension

        self.fully_connected = build_fully_connected(
            config["script_parsing_model"]["model_architecture"][
                "fully_connected_hidden_layers"
            ],
            self.output_embeddings_dim,
            config["script_parsing_model"]["model_architecture"]["nb_output_classes"],
        )
        self.device = device

    def tokenizer(self, list_sentences):
        return self.pretrained_tokenizer(
            list_sentences, return_tensors="pt", padding=True, truncation=True
        )

    def forward(self, list_sentences):

        # model_output dimensions : batch_size * nb sentences * word_embedding_dimension (=384)
        model_output = self.sentence_bert.encode(list_sentences, convert_to_tensor=True)

        # we feed the embeddings to the fully connected layers
        model_output = self.fully_connected(model_output)

        return model_output

    def intermediate_forward(self, list_sentences):
        return self.sentence_bert.encode(list_sentences, convert_to_tensor=True)

    def fully_connected_forward(self, embeddings):
        return self.fully_connected(embeddings)


def build_fully_connected(fully_connected_hidden_layers, input_dim, output_dim):
    dimension_list = [input_dim] + fully_connected_hidden_layers + [output_dim]
    layers = OrderedDict()
    for i in range(len(dimension_list) - 1):
        if dimension_list[i] == "relu":
            layers[f"relu{i}"] = nn.ReLU()
        elif isinstance(dimension_list[i], int):
            j = 1
            while not isinstance(dimension_list[i + j], int):
                j += 1
            layers[f"fc{i}"] = nn.Linear(dimension_list[i], dimension_list[i + j])
        else:
            raise ValueError(
                f"Got invalid value in fully_connected_hidden_layers parameter : only ints \
                and 'relu' are accepted but got {dimension_list[i]} of type {type(dimension_list[i])}."
            )

    fully_connected = nn.Sequential(layers)
    return fully_connected


if __name__ == "__main__":
    import yaml

    config = yaml.safe_load(open("parameters.yaml", "r"))
    bert_classifier = SentenceTransformerClassifier(config)
    output = bert_classifier(["Ceci est une phrase de test."])
    print(output)
