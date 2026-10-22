import random
import numpy as np
from sklearn.metrics import accuracy_score

random.seed(42)
np.random.seed(42)

dataset_name = "CIFAR-10"
predictions = np.array([0, 1, 1, 0])
labels = np.array([0, 1, 0, 0])
metric = "accuracy"
score = accuracy_score(labels, predictions)
print(dataset_name, metric, score)
