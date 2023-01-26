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
    bechdel_computed_scores = []
    bechdel_true_scores = []
    bechdel_approved_predictions = []
    bechdel_approved_truths = []
    for path in tqdm(list(dataset["path"])[:10]):
        ground_truth = dataset[dataset["path"] == path].iloc[0]["rating"]
        script = Script(path, ground_truth=ground_truth)
        score = int(script.computed_score)
        bechdel_computed_scores.append(score)
        bechdel_true_scores.append(ground_truth)
        bechdel_approved_predictions.append(score == 3)
        bechdel_approved_truths.append(ground_truth == 3)

    bechdel_approved_predictions_df = pd.Series(bechdel_approved_predictions)
    bechdel_approved_predictions_df.name = "prediction_bechdel_approved"
    bechdel_computed_scores_df = pd.Series(bechdel_computed_scores)
    bechdel_computed_scores_df.name = "predicted_rating"
    dataset_with_predictions = pd.concat(
        [dataset, bechdel_approved_predictions_df, bechdel_computed_scores_df], axis=1
    )

    return (
        bechdel_computed_scores,
        bechdel_true_scores,
        bechdel_approved_predictions,
        bechdel_approved_truths,
        dataset_with_predictions,
    )


def compute_confusion_matrix(bechdel_truths, bechdel_approved_predictions):

    conf_matrix = confusion_matrix(bechdel_truths, bechdel_approved_predictions)

    conf_matrix_percents = conf_matrix * 100 / len(bechdel_truths)

    return conf_matrix, conf_matrix_percents


def compute_accuracy_binary(conf_matrix):
    if conf_matrix.dtype == "int64":
        true_pos = int(conf_matrix[1, 1])
        true_neg = int(conf_matrix[0, 0])
        false_pos = int(conf_matrix[0, 1])
        false_neg = int(conf_matrix[1, 0])
    else:
        true_pos = round(conf_matrix[1, 1], 2)
        true_neg = round(conf_matrix[0, 0], 2)
        false_pos = round(conf_matrix[0, 1], 2)
        false_neg = round(conf_matrix[1, 0], 2)

    dict_conf_matrix = {
        "true_pos": true_pos,
        "false_pos": false_pos,
        "false_neg": false_neg,
        "true_neg": true_neg,
    }

    nb_correctly_classified_scripts = true_pos + true_neg

    return dict_conf_matrix, nb_correctly_classified_scripts


def compute_accuracy_scores(conf_matrix):
    if conf_matrix.dtype == "int64":
        true_score_0 = [int(el) for el in conf_matrix[0]]
        true_score_1 = [int(el) for el in conf_matrix[1]]
        true_score_2 = [int(el) for el in conf_matrix[2]]
        true_score_3 = [int(el) for el in conf_matrix[3]]
    else:
        true_score_0 = [round(el, 2) for el in conf_matrix[0]]
        true_score_1 = [round(el, 2) for el in conf_matrix[1]]
        true_score_2 = [round(el, 2) for el in conf_matrix[2]]
        true_score_3 = [round(el, 2) for el in conf_matrix[3]]

    dict_conf_matrix = {
        "true_score_0": true_score_0,
        "true_score_1": true_score_1,
        "true_score_2": true_score_2,
        "true_score_3": true_score_3,
    }

    nb_correctly_classified_scripts = sum(
        [int(conf_matrix[i, i]) for i in range(len(conf_matrix))]
    )

    return dict_conf_matrix, nb_correctly_classified_scripts


def create_results(
    date,
    dict_conf_matrix_b,
    dict_conf_matrix_percents_b,
    accuracy_b,
    dict_conf_matrix_s,
    dict_conf_matrix_percents_s,
    accuracy_s,
    nb_of_scripts,
    config,
):
    results = {}

    results["date"] = date
    sha, message = get_git_info()
    results["commit_sha"] = sha
    results["commit_message"] = message

    config = yaml.safe_load(open("parameters.yaml"))
    results["config"] = {}
    # Register in results.config the appropriate categories
    results["config"]["bechdel_test_rules"] = config["bechdel_test_rules"]
    results["config"]["used_methods"] = config["used_methods"]

    results["metrics"] = {}
    results["metrics"]["number_of_scripts"] = nb_of_scripts

    results["metrics"]["binary_performance"] = {}
    results["metrics"]["binary_performance"]["confusion_matrix"] = dict_conf_matrix_b
    results["metrics"]["binary_performance"][
        "confusion_matrix_percents"
    ] = dict_conf_matrix_percents_b
    results["metrics"]["binary_performance"][
        "nb_correctly_classified_scripts"
    ] = accuracy_b
    results["metrics"]["binary_performance"]["accuracy"] = round(
        accuracy_b / nb_of_scripts, 4
    )

    results["metrics"]["score_metrics"] = {}
    results["metrics"]["score_metrics"]["confusion_matrix"] = dict_conf_matrix_s
    results["metrics"]["score_metrics"][
        "confusion_matrix_percents"
    ] = dict_conf_matrix_percents_s
    results["metrics"]["score_metrics"]["nb_correctly_classified_scripts"] = accuracy_s
    results["metrics"]["score_metrics"]["accuracy"] = round(
        accuracy_s / nb_of_scripts, 4
    )

    return results


def create_results_folder(
    dict_conf_matrix_b,
    dict_conf_matrix_percents_b,
    accuracy_b,
    dict_conf_matrix_s,
    dict_conf_matrix_percents_s,
    accuracy_s,
    nb_of_scripts,
    dataset_with_predictions,
):
    date = format_date(datetime.now())

    config = yaml.safe_load(open("parameters.yaml"))

    results = create_results(
        date,
        dict_conf_matrix_b,
        dict_conf_matrix_percents_b,
        accuracy_b,
        dict_conf_matrix_s,
        dict_conf_matrix_percents_s,
        accuracy_s,
        nb_of_scripts,
        config,
    )

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


def main():
    (
        bechdel_predicted_scores,
        bechdel_true_scores,
        bechdel_predictions,
        bechdel_truths,
        dataset_with_predictions,
    ) = load_scripts()

    print(bechdel_predicted_scores, "predicted")
    print(bechdel_true_scores, "truth")

    conf_matrix_binary, conf_matrix_percents_binary = compute_confusion_matrix(
        bechdel_truths, bechdel_predictions
    )

    conf_matrix_scores, conf_matrix_percents_scores = compute_confusion_matrix(
        bechdel_true_scores, bechdel_predicted_scores
    )

    print(conf_matrix_scores)

    dict_cm_b, accuracy_b = compute_accuracy_binary(conf_matrix_binary)
    dict_cm_p_b, accuracy_percents_b = compute_accuracy_binary(
        conf_matrix_percents_binary
    )

    dict_cm_s, accuracy_s = compute_accuracy_scores(conf_matrix_scores)
    dict_cm_p_s, accuracy_percents_s = compute_accuracy_scores(
        conf_matrix_percents_scores
    )

    #
    #     False positive : we predict the movie passes the test, while it doesn't.
    #
    #     False negative : we predict the movie fails the test, while it passes.
    #

    create_results_folder(
        dict_cm_b,
        dict_cm_p_b,
        accuracy_b,
        dict_cm_s,
        dict_cm_p_s,
        accuracy_s,
        len(bechdel_truths),
        dataset_with_predictions,
    )


if __name__ == "__main__":
    main()
