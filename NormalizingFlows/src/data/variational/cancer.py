from .data import Dataset

import torch
import numpy as np
import scipy.io

from pathlib import Path

from torch.distributions.half_cauchy import HalfCauchy
from torch.distributions.normal import Normal
from torch.distributions.multivariate_normal import MultivariateNormal
from torch.nn.functional import softplus

dirname = Path(__file__).parent.absolute()
DATAPATH = str(dirname) + '/../../../data/preprocessed/cancer/ALLAML.mat'

class CancerRegression(Dataset):
    def __init__(self):
        super().__init__()

        datafile = scipy.io.loadmat(DATAPATH)
        X = datafile['X']
        y = datafile['Y']
        y = y - 1

        self.n_train = 60
        self.n_test = 12
        self.dim = 2 * X.shape[1] + 3
        self.beta_dim = X.shape[1]
        self.dim_input = self.dim

        X_train = torch.from_numpy(X[:self.n_train,:]).to(self.device)
        X_test = torch.from_numpy(X[self.n_train:,:]).to(self.device)

        mean, var = torch.mean(X_train, axis=0), torch.var(X_train, axis=0)
        X_train = (X_train - mean)/torch.sqrt(var)
        X_test = (X_test - mean)/torch.sqrt(var)

        y_train = torch.from_numpy(y[:self.n_train,:])
        y_test = torch.from_numpy(y[self.n_train:,:])

        self.train_data = [X_train, y_train]
        self.test_data = [X_test, y_test]

        self.tau_0 = 1/(self.dim-1) * 2/(self.n_train**0.5)

        self.tau_distr = HalfCauchy(torch.tensor(self.tau_0).to(self.device))
        self.lam_distr = HalfCauchy(torch.tensor(1).to(self.device))
        self.beta0_distr = Normal(torch.tensor(0).to(self.device),torch.tensor(10).to(self.device))

    def log_prior(self, param):
        beta = param[:, :self.beta_dim]
        lam = softplus(param[:, self.beta_dim:(2 * self.beta_dim)])
        beta_0 = param[:,-3]
        tau = softplus(param[:,-2])
        c_sqr = softplus(param[:,-1])**2
        
        log_p = -3 * torch.log(c_sqr) - 8/c_sqr
        log_p = log_p + self.tau_distr.log_prob(tau)
        log_p = log_p + self.lam_distr.log_prob(lam)

        variance = tau**2 * ((c_sqr*lam**2)/(c_sqr + tau**2*lam**2))
        beta_distr = MultivariateNormal(torch.zeros(self.beta_dim), torch.eye(beta_dim) * variance)
        log_p = log_p + beta_distr.log_prob(beta)

        return log_p

    def log_lik(self, param, data):
        X, y = data
        beta = param[:, :self.beta_dim]
        beta_0 = param[:,-3]
        p = torch.sigmoid(beta @ data.T + beta_0)

        log_l = y * torch.log(p) + (1-y) * torch.log(1-p)
        log_l = torch.sum(log_l, axis=1)

        return ((1/(X.size()[0]) * log_l)[:,0]).to(self.device)
    
