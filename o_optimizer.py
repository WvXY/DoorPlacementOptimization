import numpy as np
from tqdm import tqdm


# Metropolis-Hastings Optimizer
class MHOptimizer:
    def __init__(self, layout, system, f, T, samples):

        self.system = system
        self.layout = layout
        self.f = f
        self.T = T  # Temperature
        self.samples = samples

        self.has_started = False

        # for logging
        self.losses = []
        self.prev_score = None
        self.best_score = None
        self.best_edge, self.best_ratio = None, None

    def init(self):
        if self.has_started:
            self.losses = []
            print(
                "WARNING: Optimizer has already started."
                " Might cause unexpected behavior"
            )

        self.has_started = True
        self.prev_score = self.f(self.layout, self.samples)
        self.__update_bests(self.prev_score)
        # fig = vis.get_fig()

    def step(self):
        self.system.propose()

        new_score = self.f(self.layout, self.samples)
        df = new_score - self.prev_score

        # Accept or reject proposal
        alpha = np.exp(-df / self.T)
        if np.random.rand() < alpha:
            self.prev_score = new_score
            self.losses.append(new_score)
            if new_score < self.best_score:
                self.__update_bests(new_score)
        else:
            self.system.reject()

        self.T *= 0.99

    def end(self):
        assert self.has_started, "Optimizer has not started yet"

        self.system.load_manually(self.best_edge, self.best_ratio)
        self.has_started = False

    def run(self, num_steps):
        """
        Automatically run the optimizer for num_steps
        If you want to show the results for each steps, use step() instead
        """
        for _ in tqdm(range(num_steps)):
            self.step()

        self.end()

    def __update_bests(self, score):
        self.best_edge, self.best_ratio = self.system.get_states()
        self.best_score = score
