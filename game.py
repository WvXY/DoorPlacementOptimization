import numpy as np
import matplotlib.pyplot as plt

from itertools import combinations
import random
import math


EXAMINE_DIRS8 = (
    (1, 0),
    (0, 1),
    (-1, 0),
    (0, -1),
    # 4 corners
    (1, 1),
    (-1, 1),
    (1, -1),
    (-1, -1),
)

EXAMINE_DIRS4 = ((1, 0), (0, 1), (-1, 0), (0, -1))


def manhattan_dist(p1, p2):
    if isinstance(p1, Pixel):
        return abs(p1.index[0] - p2.index[0]) + abs(p1.index[1] - p2.index[1])
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def chebyshev_dist(p1, p2):
    if isinstance(p1, Pixel):
        return max(
            abs(p1.index[0] - p2.index[0]), abs(p1.index[1] - p2.index[1])
        )
    return max(abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))


def euclidian_dist(p1, p2):
    if isinstance(p1, Pixel):
        return np.sqrt(
            (p1.index[0] - p2.index[0]) ** 2 + (p1.index[1] - p2.index[1]) ** 2
        )
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def aStar(start, end):
    open_set = {start}
    came_from = {}
    g_score = {start: 0}
    f_score = {start: manhattan_dist(start, end)}

    while open_set:
        current = min(open_set, key=lambda x: f_score[x])
        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path, f_score[end]

        open_set.remove(current)
        for neighbor in current.neighbors4:
            if neighbor.type == 1:
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + manhattan_dist(
                        neighbor, end
                    )
                    if neighbor not in open_set:
                        open_set.add(neighbor)
    return None, float("inf")


def gen_layout(xlim: int = 32, ylim: int = 32):
    # layout = np.random.choice([0, 1], (xlim, ylim), p=[0.3, 0.7])
    layout = np.ones((xlim, ylim), dtype=np.int8)
    # layout[15, :] = 0
    for i in range(xlim):
        for j in range(ylim):
            if abs(euclidian_dist([i, j], [8, 8]) - 17) < 0.5:
                layout[i, j] = 0
    return layout


def separate_pixels(p_grid):
    blocked, walkable = [], []
    n, m = len(p_grid), len(p_grid[0])
    for i in range(n):
        for j in range(m):
            if p_grid[i][j].type == 0:
                blocked.append(p_grid[i][j])
            else:
                walkable.append(p_grid[i][j])
    return blocked, walkable


def gen_sample_points(candidates, n_points=20):
    sp = []
    for i in np.random.choice(len(candidates), n_points):
        sp.append(candidates[i])
    return sp


def extract_from_2d_array(arr, idx):
    ret = []
    for i, j in idx:
        ret.append(arr[i][j])
    return ret


def get_candidate_dirs(current, xlim, ylim, dirs):
    candidate_dirs = []
    for idir in current + np.array(dirs):
        if 0 <= idir[0] < xlim and 0 <= idir[1] < ylim:
            candidate_dirs.append(idir)
    return candidate_dirs


class Pixel:
    pGrid = []

    def __init__(self, index=None, p_type=1):
        self.neighbors8 = []
        self.neighbors4 = []
        self.type = p_type  # 0: wall, 1: walkable, for now
        self.visited = False
        self.index = index

    def swap_status(self, other):
        self.type, other.type = other.type, self.type
        self.visited, other.visited = other.visited, self.visited
        self.neighbors8, other.neighbors8 = other.neighbors8, self.neighbors8
        self.neighbors4, other.neighbors4 = other.neighbors4, self.neighbors4

    @staticmethod
    def from_grid(grid):
        n, m = grid.shape
        # pixels = []
        for i in range(n):
            row = []
            for j in range(m):
                row.append(Pixel((i, j), grid[i, j]))
            Pixel.pGrid.append(row)

        for i in range(n):
            for j in range(m):
                idirs = get_candidate_dirs(
                    np.array([i, j]), n, m, EXAMINE_DIRS4
                )
                nbs = extract_from_2d_array(Pixel.pGrid, idirs)
                Pixel.pGrid[i][j].neighbors4 = nbs

                idirs = get_candidate_dirs(
                    np.array([i, j]), n, m, EXAMINE_DIRS8
                )
                nbs = extract_from_2d_array(Pixel.pGrid, idirs)
                Pixel.pGrid[i][j].neighbors8 = nbs

    @staticmethod
    def to_grid():
        n, m = len(Pixel.pGrid), len(Pixel.pGrid[0])
        grid = np.empty((n, m))
        for row, r_pixels in enumerate(Pixel.pGrid):
            for col, pixel in enumerate(r_pixels):
                grid[row, col] = pixel.type
        return grid


class Agent:
    def __init__(self, agent: Pixel = None):
        self.agent = self.init_agent(agent) if agent else None
        self.score = 1000

    def init_agent(self, agent):
        agent.type = 1
        return agent

    def step(self):
        next = self.pick_from_candidates(self.agent.neighbors8)
        self.set_to(next)

    def set_to(self, new_agent):
        self.agent.type = 0  # reset
        self.agent = new_agent
        self.agent.type = 1

    def pick_from_candidates(self, candidates):
        random.shuffle(candidates)
        for c in candidates:
            if c.type != 0:
                continue
            return c
        return None


# visualization
class Visualize:
    @staticmethod
    def draw_grid(grid):
        plt.imshow(grid, cmap="gray")

    @staticmethod
    def draw_path(path, start, end):
        Visualize.draw_only_path(path, start)
        Visualize.draw_only_start_end(start, end)

    @staticmethod
    def draw_only_path(path, start):
        path = path + [start]
        path = path[::-1]
        for i in range(len(path) - 1):
            plt.plot(
                [path[i].index[1], path[i + 1].index[1]],
                [path[i].index[0], path[i + 1].index[0]],
                "r-",
                lw=10,
                alpha=0.1,
            )

    @staticmethod
    def draw_only_start_end(start, end):
        plt.scatter(start.index[1], start.index[0], color="g", marker="o")
        plt.scatter(end.index[1], end.index[0], color="b", marker="s")

    @staticmethod
    def show():
        plt.show()


def optimize_single_step():
    pass


def main():
    # settings
    np.random.seed(0)
    xlim, ylim = 32, 32
    n_samples = 64

    layout = gen_layout(xlim, ylim)
    Pixel.from_grid(layout)

    Visualize.draw_grid(Pixel.to_grid())
    Visualize.show()

    p_grid = Pixel.pGrid
    blocked, walkable = separate_pixels(p_grid)

    sp = gen_sample_points(walkable, n_samples)

    # --------------------------------------------
    door = Agent(blocked[0])

    # brutal force get accurate ans
    scores = []
    for b in blocked:
        b.type = 1
        score_avg = 0
        for i in range(0, n_samples, 2):
            s, e = sp[i], sp[i + 1]
            _, score = aStar(s, e)
            score_avg += score
        score_avg /= n_samples / 2
        scores.append(score_avg)
        b.type = 0
    best_ans = blocked[np.argmin(scores)]

    # optimize method
    # best_score = 1000000
    # best_ans = door.agent
    # for _ in range(100):
    #     score_avg = 0
    #     # for pairs in combinations(sp, 2):
    #     for i in range(0, n_samples, 2):
    #         s, e = sp[i], sp[i + 1]
    #         _, score = aStar(s, e)
    #         score_avg += score
    #     score_avg /= n_samples / 2
    #     if best_score > score_avg:
    #         best_score = score_avg
    #         best_ans = door.agent
    #     door.step()

    door.set_to(best_ans)

    # visualize
    grid = Pixel.to_grid()
    Visualize.draw_grid(grid)
    for i in range(0, n_samples, 2):
        s, e = sp[i], sp[i + 1]
        path, _ = aStar(s, e)
        if path:
            Visualize.draw_path(path, s, e)
        else:
            Visualize.draw_only_start_end(s, e)

    Visualize.show()


if __name__ == "__main__":
    main()
