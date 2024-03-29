import torch
import torch.nn as nn

from .neural_net import NeuralNet


class NoisyNeuralNet(NeuralNet):
    def __init__(
            self,
            dim_in,
            dim_hidden,
            dim_out,
            act_func=nn.ReLU(),
            bias=True,
            noise_level=1e-8):

        super().__init__(dim_in, dim_hidden, dim_out, act_func=act_func,bias=bias)
        self.noise_level = noise_level

    def forward(self, x):
        n_row, n_col = x.size()
        noise = torch.FloatTensor(n_row, n_col).uniform_(-self.noise_level, self.noise_level).to(x.device)
        return self.net(x + noise)
        



