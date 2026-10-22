import torch
from torch.utils.data import DataLoader

DATA_PATH = "C:/Users/alice/data/cifar10"
BATCH_SIZE = 32


def train(epochs=1):
    dataset = torch.randn(64, 3, 8, 8)
    loader = DataLoader(dataset, batch_size=BATCH_SIZE)
    model = torch.nn.Linear(3 * 8 * 8, 10)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    for epoch in range(epochs):
        for batch in loader:
            output = model(batch.flatten(1))
            loss = output.mean()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        print(f"epoch={epoch} loss={loss.item()}")


if __name__ == "__main__":
    train()
