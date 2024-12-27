import numpy as np
from o_door import FDoor

class Optimizer:
    def __init__(self):
        self.agent: None

        self.sampler = None
        self.agent = None
        self.map = None

        self.f = None
        self.g = None

    def set_f(self, f):
        self.f = f

    def set_g(self, g):
        self.g = g

    def metropolis_step(self, f=None, g=None):
        if not g:
            g = self.g
        if not f:
            f = self.f
        x_proposed = g()
        a = min(1.0, f(x_proposed) / f(self.agent.agent))
        x_new = np.random.choice([x_proposed, self.agent.agent], p=[a, 1 - a])
        # return x_new
        self.agent.set_to(x_new)

    def metropolis_iterate(self, num_steps, f=None, g=None):
        for n in range(num_steps):
            self.metropolis_step()
