import os
from typing import List, Tuple

import torch
from torch.utils.data import DataLoader
from typing import Union

from script_parsing.fine_tuning import (
    fine_tune_parsing_model,
    load_model_from_checkpoint,
)
from script_parsing.naive_parsing import clean_scenes, label
from script_parsing.parsing_model import (
    BertClassifier,
    SentenceTransformerClassifier,
    get_model,
)


def tag_script_with_ml(
    config: dict, script_path: str
) -> Tuple[List[List[str]], List[List[label]]]:
    """Using predictions from a trained model, assign a label to each line of a script.

    Args:
        script_path (str): path of the script
        config (dict) :

    Returns:
        Tuple[List[List[str]], List[List[label]] ]: First element of the
            tuple is a list of scenes, each scene being a list of lines.
            The second element returned is the list of labels for each line.
    """
    with open(script_path, "r") as f:
        script_text = f.read()

    model = get_trained_model(config)

    list_lines = script_text.split("\n")
    list_tags = predict_tag_of_lines(config, model, list_lines)

    scenes_lines, scenes_tags = find_scenes(list_lines, list_tags)

    return scenes_lines, scenes_tags


def predict_tag_of_lines(
    config: dict,
    model: Union[BertClassifier, SentenceTransformerClassifier],
    list_lines: List[str],
) -> List[label]:
    """Given a list of lines and a trained model, assign a label to each line.

    Args:
        config (dict): config yaml file imported as a dict
        model (Union[BertClassifier, SentenceTransformerClassifier]): model trained to
            classify a line of text into the six available labels.
        list_lines (List[str]): list of string, each element being a line from a script

    Returns:
        List[label]: _description_
    """
    list_tags = []
    dataloader = DataLoader(
        dataset=list_lines, batch_size=config["script_parsing_model"]["batch_size"]
    )
    for lines_batch in dataloader:
        list_tags += model.predict_rough_batch(lines_batch)
    return list_tags


def find_scenes(
    lines: List[str],
    tags: List[label],
) -> Tuple[List[List[str]], List[List[str]]]:
    """Divides a list of lines and labels into sublists corresponding to each
    scene. The beginning of the scenes is determined by the presence of the
    SCENES_BOUNDARY label.

    Args:
        lines (List[str]): list of string representing the lines in a script
        tags (List[label]): list of labels associated to each line in the script

    Returns:
        Tuple[List[List[str]], List[List[str]]]: First element of the
            tuple is a list of scenes, each scene being a list of lines.
            The second element returned is the list of labels for each line.
    """
    scenes_lines = []
    current_scene_lines = []
    scenes_tags = []
    current_scene_tags = []
    for i in range(len(tags)):
        if tags[i] != label.SCENES_BOUNDARY:
            current_scene_lines.append(lines[i])
            current_scene_tags.append(tags[i])
        else:
            scenes_lines.append(current_scene_lines)
            scenes_tags.append(current_scene_tags)
            current_scene_lines = [lines[i]]
            current_scene_tags = [tags[i]]
    return scenes_lines, scenes_tags


def get_trained_model(
    config: dict,
) -> Union[BertClassifier, SentenceTransformerClassifier]:
    """Returns a classification model trained to find the label of a line
    in a script. If the weights of the model are already saved as a .pth file,
    they are loaded as is, else the model is trained according to the conditions
    found in the config file, and its weights are savec as a .pth file for further
    use.

    Args:
        config (dict): config yaml file imported as a dict

    Returns:
        Union[BertClassifier, SentenceTransformerClassifier] : the trained model
    """
    checkpoint_path = os.path.join(
        config["paths"]["input_folder_name"], config["names"]["parsing_model"]
    )
    if os.path.exists(checkpoint_path):
        if torch.cuda.is_available():
            device = torch.device(f"cuda:{torch.cuda.current_device()}")
        else:
            device = torch.device("cpu")

        model = get_model(config, device)
        model = load_model_from_checkpoint(model, checkpoint_path=checkpoint_path)
        return model
    else:
        model = fine_tune_parsing_model(config)
        torch.save(model.state_dict(), checkpoint_path)
        return model


if __name__ == "__main__":
    from random import choice
    import pandas as pd
    import configue

    config = configue.load("parameters.yaml")
    scripts = pd.read_csv("script_parsing/coherent_parsing.csv")
    incoherent_scripts = scripts[~scripts["coherent parsing"]]
    script_path = choice(incoherent_scripts["path"].tolist())

    scenes, tags = tag_script_with_ml(config, script_path)
    print(scenes, tags)
