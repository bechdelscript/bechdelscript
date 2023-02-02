import os
from typing import List

import matplotlib.pyplot as plt


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
    """Stores the evolution of several metrics along the epochs, plots
    and stores the plots in the experiment folder.
    """

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
