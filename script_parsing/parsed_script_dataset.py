import os
from typing import List, Tuple, Union

import pandas as pd
import torch
from torch.utils.data import DataLoader, random_split
from tqdm import tqdm

from screenplay_classes import Script
from script_parsing.naive_parsing import label, tag_script


def get_df_coherent_scripts(
    config: dict,
) -> Tuple[pd.DataFrame, Union[List[Script], None]]:
    """Returns a dataframe containing the script's path and whether its parsing
    seems coherent or not (according to the check_parsing_is_coherent method of Script).
    If the dataframe already exists, it is loaded and returned alone.
    Else it is built and returned along with the list of Script objects that was used to build
    the dataframe.

    Args:
        config (dict): config (dict): config yaml file imported as a dict

    Returns:
        Tuple[pd.DataFrame, Union[List[Script], None]]: the first element of the tuple is
            the dataframe, the second element is optional and is a list of Scripts (or a None).
    """
    coherent_scripts_path = os.path.join(
        config["paths"]["script_parsing_folder"],
        config["names"]["coherently_parsed_scripts"],
    )
    if os.path.exists(coherent_scripts_path):
        return pd.read_csv(coherent_scripts_path, index_col=0), None
    else:
        dataset = pd.read_csv(
            os.path.join(
                config["paths"]["input_folder_name"], config["names"]["db_name"]
            )
        )
        return create_df_coherent_scripts(coherent_scripts_path, dataset)


def create_df_coherent_scripts(
    coherent_scripts_path: str, dataset: pd.DataFrame
) -> Tuple[pd.DataFrame, List[Script]]:
    """Builds a dataframe containing whether each script was parsed
    coherently or not by the naive method. Returns the dataframe
    along with a list of Script objects used to build the dataframe.

    Args:
        coherent_scripts_path (str): path to save the dataframe
        dataset (pd.DataFrame): bechdel dataset containing the path of the scripts
            for which we know the bechdel test value

    Returns:
        Tuple[pd.DataFrame, List[Script]]: the first element of the tuple is
            the dataframe, the second element a list of Scripts.
    """
    scripts = []
    for path in tqdm(list(dataset["path"])):
        script = Script(path)
        scripts.append(script)

    dataset["coherent parsing"] = [script.coherent_parsing for script in scripts]
    dataset.to_csv(coherent_scripts_path, index=True)
    return dataset, scripts


def create_lines_and_tags_df(config: dict) -> pd.DataFrame:
    """Builds, saves and returns a dataset of lines extracted from the scripts
    coherently parsed bu the naive method, along with their labels.
    The lines are lstripped (left whitespaces removed), and the empty lines are
    removed.

    Args:
        config (dict): config yaml file imported as a dict

    Returns:
        pd.DataFrame: dataframe with two columns, a 'lines' column containing the text
            and a 'tags' column containing the label (as a string).
    """
    df_coherent_scripts, scripts_eventually = get_df_coherent_scripts(config)

    coherent_scripts_only = df_coherent_scripts[df_coherent_scripts["coherent parsing"]]

    if scripts_eventually is None:
        coherent_scripts_only["lines and tags"] = coherent_scripts_only["path"].apply(
            tag_script
        )
        coherent_scripts_only[["lines", "tags"]] = pd.DataFrame(
            coherent_scripts_only["lines and tags"].tolist(),
            index=coherent_scripts_only.index,
        )
    else:
        coherent_scripts_only["lines"] = [
            [scene.list_lines for scene in script.list_scenes]
            for script in scripts_eventually
            if script.coherent_parsing
        ]
        coherent_scripts_only["tags"] = [
            script.list_list_tags
            for script in scripts_eventually
            if script.coherent_parsing
        ]

    # explode list of scenes
    coherent_scripts_only = coherent_scripts_only.explode(["lines", "tags"])
    # explode lines in scene
    coherent_scripts_only = coherent_scripts_only.explode(["lines", "tags"])
    lines_and_tags = coherent_scripts_only[["lines", "tags"]]
    # removing empty lines
    lines_and_tags = lines_and_tags[~(lines_and_tags["tags"] == label.EMPTY_LINE)]

    lines_and_tags["lines"] = lines_and_tags["lines"].apply(lambda x: x.lstrip())

    lines_and_tags["tags"] = lines_and_tags["tags"].apply(lambda x: x.name)

    lines_and_tags.to_csv(
        os.path.join(
            config["paths"]["script_parsing_folder"], config["names"]["tagged_lines"]
        ),
        index=False,
    )

    return lines_and_tags


class TaggedLines(torch.utils.data.Dataset):
    """Dataset contaning the lines and their labels"""

    def __init__(
        self,
        lines_and_labels: pd.DataFrame,
        lines_column_name: str = "lines",
        labels_column_name: str = "labels",
    ):
        for i, column_name in enumerate([lines_column_name, labels_column_name]):
            if column_name not in lines_and_labels.columns:
                raise ValueError(
                    f"{column_name} was passed as the name for the {['lines', 'labels'][i]} column \
                    but is not a column of the passed dataframe which has the following columns : {lines_and_labels.columns})."
                )
        self.data = lines_and_labels
        self.lines_column_name = lines_column_name
        self.labels_column_name = labels_column_name
        self.data = self.data.reset_index()

    def __len__(self):
        return len(self.data.index)

    def __getitem__(self, idx):
        return (
            self.data.loc[idx][self.lines_column_name],
            self.data.loc[idx][self.labels_column_name],
        )

    def truncate_beginning(self, start_index: int):
        """Removes the beginning of the dataset, so that dataset[start index]
        is the new first element.

        Args:
            start_index (int): the index of the new first element
        """
        self.data = self.data[start_index:]
        self.data = self.data.reset_index()


def get_dataset(config: dict) -> TaggedLines:
    """Returns a TaggedLines dataset, i.e. a dataset containing the lines
    and their labels (as tensors of 0 and 1)
    First the dataframe containing the lines and their labels is loaded,
    then the labels are one hot encoded to compute the loss more easily. To
    finish, only a sample of the dataset is kept if the config file instructs
    to do so.

    Args:
        config (dict): config yaml file imported as a dict

    Returns:
        TaggedLines: dataset containing the lines and their labels
    """
    df_path = os.path.join(
        config["paths"]["script_parsing_folder"], config["names"]["tagged_lines"]
    )
    if os.path.exists(df_path):
        lines_and_tags = pd.read_csv(df_path, index_col=None)
    else:
        lines_and_tags = create_lines_and_tags_df(config)

    # one hot encoding of tags
    label_to_tensor_dict = {e.name: e.tensor for e in label}
    lines_and_tags["labels"] = lines_and_tags["tags"].apply(lambda x: label_to_tensor_dict[x])
    lines_and_labels = lines_and_tags.drop(columns="tags")
    lines_and_labels["labels"] = lines_and_labels["labels"].apply(torch.Tensor)

    # keep only a percentage of the dataset
    sample_lines_and_labels = lines_and_labels.sample(
        frac=config["script_parsing_model"]["dataset_percentage"],
        random_state=config["script_parsing_model"]["seed"],
    )

    return TaggedLines(sample_lines_and_labels)


def get_dataloaders(
    config: dict, dataset: torch.utils.data.Dataset, shuffle: bool = True
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """Divides the dataset into a train/val/test set and builds
    tree dataloaders accordingly.

    Args:
        config (dict): config yaml file imported as a dict
        dataset (torch.utils.data.Dataset): currently, should be a TaggedLines dataset or
            a LinesEmbeddingsDataset
        shuffle (bool, optional): whether to shuffle the dataset or not. Defaults to True.

    Raises:
        ValueError: the dataset is too small to be splitted.

    Returns:
        Tuple[DataLoader, DataLoader, DataLoader]: the train, validation and test dataloaders
    """
    val_prop = config["script_parsing_model"]["validation_dataset_proportion"]
    test_prop = config["script_parsing_model"]["test_dataset_proportion"]
    train_dataset, validation_dataset, test_dataset = random_split(
        dataset,
        [1 - val_prop - test_prop, val_prop, test_prop],
        generator=torch.Generator().manual_seed(config["script_parsing_model"]["seed"]),
    )

    batch_size = config["script_parsing_model"]["batch_size"]

    if (
        len(train_dataset) == 0
        or len(validation_dataset) == 0
        or len(test_dataset) == 0
    ):
        raise ValueError(
            "The dataset is too small to be split correctly in a training, validation and test \
            dataset. Please consider increasing the value of the script_parsing_model.dataset_percentage parameter."
        )
    train_loader = DataLoader(
        dataset=train_dataset,
        batch_size=batch_size,
        shuffle=shuffle,
    )
    validation_loader = DataLoader(
        dataset=validation_dataset,
        batch_size=batch_size,
        shuffle=shuffle,
    )
    test_loader = DataLoader(
        dataset=test_dataset,
        batch_size=batch_size,
        shuffle=shuffle,
    )
    return train_loader, validation_loader, test_loader


if __name__ == "__main__":
    import time

    import yaml

    config = yaml.safe_load(open("parameters.yaml"))
    tic = time.time()
    dataset = get_dataset(config)
    print("TIME :", time.time() - tic)
