import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.data import DataLoader


def train_forward(
        model, 
        base_dist, 
        train_data, 
        optimizer, 
        epochs=1000, 
        batch_size=16, 
        print_n=100,
        scheduler=None,
    ):

    batches = DataLoader(dataset=train_data, batch_size=batch_size, 
                            shuffle=True) 

    model.train()
    losses = []

    for epoch in range(epochs):
        loss = 0
        for batch in batches:
            z, log_prob = model(batch)
            loss = -torch.mean(log_prob)

            model.zero_grad()
            loss.backward()
            optimizer.step()
            if scheduler != None:
                scheduler.step()
            loss += loss.item()
        losses.append(loss) 

        if epoch % print_n == 0:
            #print(loss.item())
            print(losses[epoch])

    model.eval()


def train_backward(
        model, 
        base_dist, 
        target_dist, 
        dim, 
        optimizer, 
        scheduler, 
        epochs=1000, 
        batch_size=16, 
        batches=20, 
        print_n=100,
    ):

    model.train()
    losses = []

    for epoch in range(epochs):
        for batch in range(batches):
            sample = base_dist.sample((batch_size, dim)) 
            x, log_prob = model(batch)
            target_prob = target_dist.log_prob(x[-1])
            loss = torch.mean(log_prob - target_prob)

            model.zero_grad()
            loss.backward()
            optimizer.step()
            scheduler.step()

        if epoch % print_n == 0:
            print(loss.item())