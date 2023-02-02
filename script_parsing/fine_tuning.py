import os
from datetime import datetime
from typing import List, Tuple

import torch
import yaml
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import ReduceLROnPlateau

from script_parsing.intermediate_forward import (
    LinesEmbeddingsDataset,
    freeze_pretrained_model_part,
    get_intermediate_dataset,
)
from script_parsing.monitoring import AverageMeter, Monitor
from script_parsing.parsed_script_dataset import (
    TaggedLines,
    get_dataloaders,
    get_dataset,
)
from script_parsing.parsing_model import get_model


def fine_tune_parsing_model(config):

    if torch.cuda.is_available():
        device = torch.device(f"cuda:{torch.cuda.current_device()}")
    else:
        device = torch.device("cpu")

    intermediate_forward = config["script_parsing_model"]["intermediate_forward"]

    model = get_model(config, device)
    model.to(device)
    if config["script_parsing_model"]["load_checkpoint"]:
        model = load_model_from_checkpoint(config, model)
    if intermediate_forward:
        freeze_pretrained_model_part(model)

    if intermediate_forward:
        dataset: LinesEmbeddingsDataset = get_intermediate_dataset(
            config, model, device
        )
    else:
        dataset: TaggedLines = get_dataset(config)

    train_loader, validation_loader, _ = get_dataloaders(config, dataset)

    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=config["script_parsing_model"]["learning_rate"]["initial_value"],
        weight_decay=config["script_parsing_model"]["weight_decay"],
    )
    if config["script_parsing_model"]["learning_rate"]["decrease_on_plateau"]:
        scheduler = ReduceLROnPlateau(optimizer, "min", patience=config["script_parsing_model"]["learning_rate"]["patience"])

    criterion = torch.nn.CrossEntropyLoss()
    criterion = criterion.to(device)

    experiment_folder_path = get_experiment_folder_name(config)
    monitor = Monitor(
        ["train_loss", "train_top1", "val_loss", "val_top1", "learning_rate"],
        experiment_folder_path,
    )

    nb_epochs = config["script_parsing_model"]["nb_epochs"]

    for epoch in range(nb_epochs):

        train_loss, train_top1 = train_one_epoch(
            model,
            train_loader,
            optimizer,
            criterion,
            device,
            intermediate_forward,
            epoch,
        )
        val_loss, val_top1 = validate(
            model,
            validation_loader,
            criterion,
            device,
            intermediate_forward,
            epoch,
        )
        if config["script_parsing_model"]["learning_rate"]["decrease_on_plateau"]:
            scheduler.step(val_loss.avg)

        monitor.update_data(
            [
                train_loss.avg,
                train_top1.avg,
                val_loss.avg,
                val_top1.avg,
                optimizer.param_groups[0]["lr"],
            ]
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


def train_one_epoch(
    model: torch.nn.Module,
    train_loader: DataLoader,
    optimizer: torch.optim.SGD,
    criterion: torch.nn.CrossEntropyLoss,
    device: torch.device,
    intermediate_forward: bool,
    epoch: int,
    print_freq: int = 10,
) -> Tuple[AverageMeter, AverageMeter]:

    losses = AverageMeter()
    top1 = AverageMeter()
    top3 = AverageMeter()

    model.train()  # switch to train mode

    for batch_idx, batch in enumerate(train_loader):
        if not intermediate_forward:
            sentences, labels = batch
            labels = labels.to(device)
            batch_size = len(sentences)

            # compute output
            predictions = model(sentences)
        else:
            embeddings, labels = batch
            labels = labels.to(device)
            embeddings = embeddings.to(device)
            batch_size = embeddings.shape[0]

            # compute output
            predictions = model.fully_connected_forward(embeddings)

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
                "[{epoch}]\t"
                "Train: [{0}/{1}]\t"
                "Loss {loss.avg:.4f}\t"
                "Prec@1 {top1.avg:.3f}\t"
                "Prec@3 {top3.avg:.3f}".format(
                    batch_idx,
                    len(train_loader),
                    epoch=epoch,
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
    intermediate_forward: bool,
    epoch: int,
    print_freq: int = 10,
) -> Tuple[AverageMeter, AverageMeter]:

    losses = AverageMeter()
    top1 = AverageMeter()
    top3 = AverageMeter()

    model.eval()  # switch to eval mode

    for batch_idx, batch in enumerate(validation_loader):
        if not intermediate_forward:
            sentences, labels = batch
            labels = labels.to(device)
            batch_size = len(sentences)

            # compute output
            predictions = model(sentences)
        else:
            embeddings, labels = batch
            labels = labels.to(device)
            embeddings = embeddings.to(device)
            batch_size = embeddings.shape[0]

            # compute output
            predictions = model.fully_connected_forward(embeddings)

        loss = criterion(predictions, labels)

        # compute accuracy
        prec1, prec3 = accuracy(predictions.data, labels, topk=(1, 3))
        losses.update(loss.data.item(), batch_size)
        top1.update(prec1.item(), batch_size)
        top3.update(prec3.item(), batch_size)

        if batch_idx % print_freq == 0:
            print(
                "[{epoch}]\t"
                "Validation: [{0}/{1}]\t"
                "Loss {loss.avg:.4f}\t"
                "Prec@1 {top1.avg:.3f}\t"
                "Prec@3 {top3.avg:.3f}".format(
                    batch_idx,
                    len(validation_loader),
                    epoch=epoch,
                    loss=losses,
                    top1=top1,
                    top3=top3,
                )
            )

    return losses, top1


def load_model_from_checkpoint(config, model):
    checkpoint_path = config["script_parsing_model"]["checkpoint_path"]
    if not os.path.exists(checkpoint_path):
        raise ValueError(f"Given checkpoint path does not exist : {checkpoint_path}")
    if checkpoint_path[-4:] == ".pth":
        model.load_state_dict(torch.load(checkpoint_path))
        return model
    elif checkpoint_path[-3:] == ".pt":
        loaded_model = torch.load(checkpoint_path)
        if type(model) != type(loaded_model):
            raise ValueError(
                f"Checkpoint model is not the same as the model indicated \
                in the parameters ({type(loaded_model)} vs. {type(model)}))"
            )
        return loaded_model
    else:
        raise ValueError(
            f"Checkpoint path is not a valid .pth or .pt file : {checkpoint_path}"
        )


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
    import time

    config = yaml.safe_load(open("parameters.yaml", "r"))

    start = time.time()

    fine_tune_parsing_model(config)

    print("Done. Time :", time.time() - start)
