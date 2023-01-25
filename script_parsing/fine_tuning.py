import os
from datetime import datetime
from typing import List, Tuple

import matplotlib.pyplot as plt
import torch
import yaml
from torch.utils.data import DataLoader, random_split

from script_parsing.parsed_script_dataset import TaggedLines, get_dataset
from script_parsing.parsing_model import get_model


class AverageMeter(object):
    """Computes and stores the average and current value"""

    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


class Monitor:
    def __init__(self, data_names, folder_name):
        self.all_data: List[List[float]] = None
        self.data_names = data_names
        self.folder_name = folder_name

    def update_data(self, new_data: List[float]):
        if self.all_data is None:
            if len(new_data) != len(self.data_names):
                raise ValueError("There must be as many plot names as data lists.")
            self.all_data = [[value] for value in new_data]
        else:
            if len(self.all_data) != len(new_data):
                raise ValueError(
                    "New data to be monitored should have the same size as previously given data"
                )
            for i, value in enumerate(new_data):
                self.all_data[i].append(value)

    def plot_data(self):
        for i, data in enumerate(self.all_data):
            plt.figure()
            plt.plot([j for j in range(len(data))], data)
            plt.xlabel("Epochs")
            plt.savefig(os.path.join(self.folder_name, f"{self.data_names[i]}.png"))

    def log_data(self, file_name="log.txt"):
        text = ""
        for j in range(len(self.all_data[0])):
            text += f"Epoch: {j} \t"
            for i in range(len(self.all_data)):
                text += f"{self.data_names[i]}: {self.all_data[i][j]:.3f} \t"
            text += "\n"

        with open(os.path.join(self.folder_name, file_name), "w+") as f:
            f.write(text)


def fine_tune_parsing_model(config):

    experiment_folder_path = get_experiment_folder_name(config)

    train_loader, validation_loader, test_loader = get_dataloaders(config)

    if torch.cuda.is_available():
        device = torch.device(f"cuda:{torch.cuda.current_device()}")
    else:
        device = torch.device("cpu")

    model = get_model(config, device)
    model.to(device)
    nb_epochs = config["script_parsing_model"]["nb_epochs"]

    optimizer = torch.optim.SGD(
        model.parameters(), config["script_parsing_model"]["learning_rate"]
    )

    criterion = torch.nn.CrossEntropyLoss()
    criterion = criterion.to(device)

    monitor = Monitor(
        ["train_loss", "train_top1", "val_loss", "val_top1"], experiment_folder_path
    )

    for epoch in range(nb_epochs):
        train_loss, train_top1 = train_one_epoch(
            model, train_loader, optimizer, criterion, device
        )
        val_loss, val_top1 = validate(model, validation_loader, criterion, device)
        monitor.update_data(
            [train_loss.avg, train_top1.avg, val_loss.avg, val_top1.avg]
        )
        monitor.plot_data()
        monitor.log_data()
        if val_top1.avg == max(monitor.all_data[3]):
            torch.save(
                model.state_dict(),
                os.path.join(experiment_folder_path, "best_model.pth"),
            )
        torch.save(
            model.state_dict(), os.path.join(experiment_folder_path, "last_model.pth")
        )


def get_experiment_folder_name(config):
    results_folder = config["paths"]["script_parsing_experiments_folder"]
    os.makedirs(results_folder, exist_ok=True)
    for subfolder in os.listdir(results_folder):
        if os.path.isdir(subfolder):
            for filename in os.listdir(os.path.join(results_folder, subfolder)):
                if filename[-5:] == ".yaml":
                    previous_config = yaml.safe_load(
                        open(os.path.join(results_folder, subfolder, filename), "r")
                    )
                    if previous_config == config:
                        print(
                            f"Warning : same experiment was already launched in folder {subfolder}"
                        )
                        break
    new_folder_path = os.path.join(
        results_folder, datetime.now().strftime("%y-%m-%d_%H:%M:%S")
    )
    os.makedirs(new_folder_path)
    yaml.dump(config, open(os.path.join(new_folder_path, "parameters.yaml"), "w+"))
    return new_folder_path


def get_dataloaders(config):
    dataset: TaggedLines = get_dataset(config)
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
        shuffle=True,
    )
    validation_loader = DataLoader(
        dataset=validation_dataset,
        batch_size=batch_size,
        shuffle=True,
    )
    test_loader = DataLoader(
        dataset=test_dataset,
        batch_size=batch_size,
        shuffle=True,
    )
    return train_loader, validation_loader, test_loader


def train_one_epoch(
    model: torch.nn.Module,
    train_loader: DataLoader,
    optimizer: torch.optim.SGD,
    criterion: torch.nn.CrossEntropyLoss,
    device: torch.device,
    print_freq: int = 10,
) -> Tuple[AverageMeter, AverageMeter]:

    losses = AverageMeter()
    top1 = AverageMeter()
    top3 = AverageMeter()

    model.train()  # switch to train mode

    for batch_idx, batch in enumerate(train_loader):
        sentences, labels = batch
        labels = labels.to(device)
        # sentences = sentences.to(device)
        batch_size = len(sentences)

        # compute output
        predictions = model(sentences)
        loss = criterion(predictions, labels)

        # compute accuracy
        prec1, prec3 = accuracy(predictions.data, labels, topk=(1, 3))
        losses.update(loss.data.item(), batch_size)
        top1.update(prec1.item(), batch_size)
        top3.update(prec3.item(), batch_size)

        # compute gradient and do SGD step
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if batch_idx % print_freq == 0:
            print(
                "Train: [{0}/{1}]\t"
                "Loss {loss.avg:.4f}\t"
                "Prec@1 {top1.avg:.3f}\t"
                "Prec@3 {top3.avg:.3f}".format(
                    batch_idx,
                    len(train_loader),
                    loss=losses,
                    top1=top1,
                    top3=top3,
                )
            )

    return losses, top1


def validate(
    model: torch.nn.Module,
    validation_loader: DataLoader,
    criterion: torch.optim.SGD,
    device: torch.device,
    print_freq: int = 10,
) -> Tuple[AverageMeter, AverageMeter]:

    losses = AverageMeter()
    top1 = AverageMeter()
    top3 = AverageMeter()

    model.eval()  # switch to eval mode

    for batch_idx, batch in enumerate(validation_loader):
        sentences, labels = batch
        labels = labels.to(device)
        # sentences = sentences.to(device)
        batch_size = len(sentences)

        # compute output
        predictions = model(sentences)
        loss = criterion(predictions, labels)

        # compute accuracy
        prec1, prec3 = accuracy(predictions.data, labels, topk=(1, 3))
        losses.update(loss.data.item(), batch_size)
        top1.update(prec1.item(), batch_size)
        top3.update(prec3.item(), batch_size)

        if batch_idx % print_freq == 0:
            print(
                "Validation: [{0}/{1}]\t"
                "Loss {loss.avg:.4f}\t"
                "Prec@1 {top1.avg:.3f}\t"
                "Prec@3 {top3.avg:.3f}".format(
                    batch_idx,
                    len(validation_loader),
                    loss=losses,
                    top1=top1,
                    top3=top3,
                )
            )

    return losses, top1


def accuracy(output, target, topk=(1,)) -> List[float]:
    """Computes the precision@k for the specified values of k"""
    maxk = max(topk)
    batch_size = target.size(0)

    _, y_pred = output.topk(k=maxk, dim=1, largest=True, sorted=True)
    y_pred = y_pred.t()

    _, label = target.topk(k=1, dim=1, largest=True, sorted=True)
    label = label.squeeze(-1)
    label_reshaped = label.view(1, -1).expand_as(y_pred)
    correct = y_pred == label_reshaped

    res = []
    for k in topk:
        correct_k = correct[:k].reshape(k * batch_size).float().sum(0)
        res.append(correct_k.mul_(100.0 / batch_size))
    return res


if __name__ == "__main__":
    config = yaml.safe_load(open("parameters.yaml", "r"))

    fine_tune_parsing_model(config)

    print("Done")
