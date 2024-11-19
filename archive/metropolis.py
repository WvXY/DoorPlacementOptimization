import numpy as np


class Metropolis:
    def __init__(self):
        self.agent: Agent

        self.agent = None
        self.map = None

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

    def g(self):
        return Agent.pick_from_candidates(self.agent.agent.neighbors8)

    def f(self, x: Pixel):
        self.agent.set_to(x)
        score_avg = 0
        # for pairs in combinations(sp, 2):
        for i in range(0, N_SAMPLES, 2):
            s, e = self.map[i], self.map[i + 1]
            _, score = aStar(s, e)
            score_avg += score
        score_avg /= N_SAMPLES / 2
        # return np.exp(-score_avg)
        return score_avg
