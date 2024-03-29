import torch
import torch.nn as nn

from .transformation import Transformation
from .affine import Affine
from .piecewise import PiecewiseAffine 

class PiecewiseAffineAffine(Transformation):
    def __init__(self, forward_flow=True, a_param=torch.exp, c_param=torch.exp):
        super().__init__(4, forward_flow)
        self.piecewise = PiecewiseAffine(forward_flow, a_param)
        self.affine = Affine(forward_flow=forward_flow, a_param=c_param)

    def training_direction(self, z, param):
        a, b, c, d = param[0], param[1], param[2], param[3]


        x, log_det_1 = self.piecewise.training_direction(z, [a,b])
        
        x, log_det_2 = self.affine.training_direction(x, [c,d])

        return x, (log_det_1 + log_det_2)

    def inverse_direction(self, x, param):
        a, b, c, d = param[0], param[1], param[2], param[3]

        z, log_det_1 = self.affine.inverse_direction(x, [c,d])

        z, log_det_2 = self.piecewise.inverse_direction(z, [a,b])

        return z, (log_det_1 + log_det_2)
