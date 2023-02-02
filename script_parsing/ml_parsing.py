import os
import torch

from typing import List, Tuple
from torch.utils.data import DataLoader

from script_parsing.fine_tuning import (
    load_model_from_checkpoint,
    fine_tune_parsing_model,
)
from script_parsing.parsing_model import get_model
from script_parsing.naive_parsing import label, clean_scenes


def tag_script_with_ml(config, script_path):

    with open(script_path, "r") as f:
        script_text = f.read()

    model = get_trained_model(config)

    list_lines = script_text.split("\n")
    list_tags = predict_tag_of_lines(config, model, list_lines)

    scenes_lines, scenes_tags = find_scenes(list_lines, list_tags)

    return scenes_lines, scenes_tags


def predict_tag_of_lines(config, model, list_lines):
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
    """Splits the list of lines into sublists corresponding to the different scenes.
    The delimitation between the scenes is found thanks to specific keywords marking
    the beginning and the end of the keywords.

    Args:
        lines (List[str]): _description_
        beginning_scenes_keywords (List[str], optional): list of keywords usually found
            to mark the beginning of a scene. Defaults to BEGINNING_SCENES_KEYWORDS.
        end_scenes_keywords (List[str], optional): list of keywords usually found
            to mark the end of a scene. Defaults to ENDING_SCENES_KEYWORDS.

    Returns:
        List[List[str]]: List of scenes, each scene being a list of lines.
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


def get_trained_model(config):
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
    import yaml
    import pandas as pd
    from random import choice

    config = yaml.safe_load(open("parameters.yaml", "r"))
    scripts = pd.read_csv("script_parsing/coherent_parsing.csv")
    incoherent_scripts = scripts[~scripts["coherent parsing"]]
    script_path = choice(incoherent_scripts["path"].tolist())

    scenes, tags = tag_script_with_ml(config, script_path)
    print(scenes, tags)
