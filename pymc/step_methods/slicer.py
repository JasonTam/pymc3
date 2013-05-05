# Modified from original implementation by Dominik Wabersich (2013)

from ..core import *
from arraystep import *
from numpy import floor, abs, atleast_1d
from numpy.random import standard_exponential, random, uniform

__all__ = ['Slice']

class Slice(ArrayStep):
    """Slice sampler"""
    def __init__(self, vars, w=1, m=20, n_tune=0,
            tune=True, tune_interval=100, model=None):

        model = modelcontext(model)

        self.vars = vars
        self.w = w
        self.m = m
        self.n_tune = n_tune
        self.w_tune = []
        self.tune = tune
        self.tune_interval = tune_interval
        self.model = model

        super(Slice,self).__init__(vars, [model.logpc])

    def astep(self, q0, logp):

        y = logp(q0) - standard_exponential()

        # Stepping out procedure
        L = q0 - self.w*random()
        R = L + self.w
        J = floor(self.m*random())
        K = (self.m - 1) - J

        while(J>0 and y<logp(L)):
            L = L - self.w
            J = J - 1

        while(K>0 and y<logp(R)):
            R = R + self.w
            K = K - 1

        # Sample uniformly from slice
        q_new = atleast_1d(uniform(L, R))
        y_new = logp(q_new)

        while(y_new<y):
            # Shrink bounds of uniform
            if (q_new < q0):
                L = q_new
            else:
                R = q_new
            q_new = atleast_1d(uniform(L,R))
            y_new = logp(q_new)

        if (len(self.w_tune) > self.n_tune):
            # Tune sampler parameters
            self.w_tune.append(abs(q0 - q_new))
            self.w = 2 * sum(self.w_tune)/len(self.w_tune)

        return q_new