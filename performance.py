import os

import pandas as pd
import yaml
from tqdm import tqdm
from sklearn.metrics import confusion_matrix
from screenplay_classes import Script
import json
from datetime import datetime
import git


def get_git_info():
    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    message = repo.head.object.message
    return sha, message


def load_scripts():
    config = yaml.safe_load(open("parameters.yaml"))

    dataset = pd.read_csv(
        os.path.join(config["paths"]["input_folder_name"], config["names"]["db_name"])
    )
    bechdel_approved_truths = []
    bechdel_approved_predictions = []
    for path in tqdm(list(dataset["path"])[:20]):
        ground_truth = dataset[dataset["path"] == path].iloc[0]["rating"]
        script = Script(path, ground_truth=ground_truth)
        bechdel_approved, _ = script.passes_bechdel_test()
        bechdel_approved_truths.append(ground_truth == 3)
        bechdel_approved_predictions.append(bechdel_approved)

    bechdel_approved_predictions_df = pd.Series(bechdel_approved_predictions)
    bechdel_approved_predictions_df.name = "prediction_bechdel_approved"
    dataset_with_predictions = pd.concat(
        [dataset, bechdel_approved_predictions_df], axis=1
    )

    return (
        bechdel_approved_truths,
        bechdel_approved_predictions,
        dataset_with_predictions,
    )


def compute_confusion_matrix(bechdel_truths, bechdel_approved_predictions):

    conf_matrix = confusion_matrix(bechdel_truths, bechdel_approved_predictions)

    conf_matrix_percents = conf_matrix / len(bechdel_truths)

    return conf_matrix, conf_matrix_percents


def compute_accuracy(conf_matrix):
    if conf_matrix.dtype == "int64":
        true_pos = int(conf_matrix[1, 1])
        true_neg = int(conf_matrix[0, 0])
        false_pos = int(conf_matrix[0, 1])
        false_neg = int(conf_matrix[1, 0])
    else:
        true_pos = conf_matrix[1, 1]
        true_neg = conf_matrix[0, 0]
        false_pos = conf_matrix[0, 1]
        false_neg = conf_matrix[1, 0]

    dict_conf_matrix = {
        "true_pos": true_pos,
        "false_pos": false_pos,
        "false_neg": false_neg,
        "true_neg": true_neg,
    }

    accuracy = true_pos + true_neg

    return dict_conf_matrix, accuracy


def create_results_folder(
    dict_conf_matrix,
    dict_conf_matrix_percents,
    accuracy,
    nb_of_scripts,
    dataset_with_predictions,
):

    results = {}
    date = format_date(datetime.now())
    results["date"] = date
    sha, message = get_git_info()
    results["commit_sha"] = sha
    results["commit_message"] = message
    results["metrics"] = {}
    results["metrics"]["number_of_scripts"] = nb_of_scripts
    results["metrics"]["confusion_matrix"] = dict_conf_matrix
    results["metrics"]["confusion_matrix_percents"] = dict_conf_matrix_percents
    results["metrics"]["accuracy"] = accuracy
    results["metrics"]["accuracy_percents"] = accuracy / nb_of_scripts

    config = yaml.safe_load(open("parameters.yaml"))

    path_new_directory = os.path.join(config["paths"]["output_folder_name"], date)
    os.mkdir(path_new_directory)
    path_json = os.path.join(path_new_directory, "results.json")
    path_dataset = os.path.join(path_new_directory, "dataset_preds.csv")

    dataset_with_predictions.to_csv(path_dataset, index=False)

    with open(path_json, "w+") as f:
        json.dump(results, f)

    return results


def format_date(date):
    formatted_date = date.strftime("%Y-%m-%d_%H%M%S")
    return formatted_date


if __name__ == "__main__":

    bechdel_truths, bechdel_predictions, dataset_with_predictions = load_scripts()

    # print("len ground_truth :", len(bechdel_truths))
    # print("len preds", len(bechdel_predictions))
    # print(
    #     "len dataset (preds)",
    #     len(dataset_with_predictions["prediction_bechdel_approved"]),
    # )

    conf_matrix, conf_matrix_percents = compute_confusion_matrix(
        bechdel_truths, bechdel_predictions
    )
    dict_cm, accuracy = compute_accuracy(conf_matrix)
    dict_cm_p, accuracy_percents = compute_accuracy(conf_matrix_percents)

    #
    #     "Faux positifs : nous prédisons que le film passe le test, alors qu'il ne passe pas"
    #
    #     "Faux négatifs : nous prédisons que le film rate le test, alors qu'il le passe"
    #

    create_results_folder(
        dict_cm, dict_cm_p, accuracy, len(bechdel_truths), dataset_with_predictions
    )
