import torch
import torch.nn as nn
from transformers import BertModel, BertTokenizer
from collections import OrderedDict


class BertClassifier(nn.Module):
    def __init__(self, config):
        super(BertClassifier, self).__init__()

        pretrained_model_name = config["script_parsing_model"]["pretrained_model_name"]

        self.bert = BertModel.from_pretrained(pretrained_model_name)
        self.pretrained_tokenizer = BertTokenizer.from_pretrained(pretrained_model_name)
        self.output_embeddings_dim = self.bert.config.hidden_size  # base bert output

        self.fully_connected = None
        self.build_fully_connected(
            config,
            self.output_embeddings_dim,
            config["script_parsing_model"]["nb_output_classes"],
        )

    def build_fully_connected(self, config, input_dim, output_dim):
        dimension_list = (
            [input_dim]
            + config["script_parsing_model"]["fully_connected_hidden_layers"]
            + [output_dim]
        )
        layers = OrderedDict()
        for i in range(len(dimension_list) - 1):
            layers[f"fc{i}"] = nn.Linear(dimension_list[i], dimension_list[i + 1])
        self.fully_connected = nn.Sequential(layers)

    def tokenizer(self, list_sentences):
        return self.pretrained_tokenizer(
            list_sentences, return_tensors="pt", padding=True, truncation=True
        )

    def forward(self, list_sentences):
        tokenized_sentences = self.tokenizer(list_sentences)
        # model_output dimensions : batch_size * nb tokens * bert_output_dim (=768)
        model_output = self.bert(**tokenized_sentences).last_hidden_state.detach()

        # to give the embeddings to a fully connected layer we need them all to have the same
        # dimension : we apply a mean over the dimension that has the size of nb tokens (~= nb of words)
        model_output = torch.mean(model_output, dim=1)

        model_output = self.fully_connected(model_output)

        return model_output


if __name__ == "__main__":
    import yaml

    config = yaml.safe_load(open("parameters.yaml", "r"))
    bert_classifier = BertClassifier(config)
    output = bert_classifier(["Ceci est une phrase de test."])
    print(output)
