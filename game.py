import numpy as np
import matplotlib.pyplot as plt

from itertools import combinations, permutations
import random


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
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def aStar(grid, start, end):
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
            # print(f_score[end])
            return path, f_score[end]

        open_set.remove(current)
        for i, j in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = current[0] + i, current[1] + j
            if (
                0 <= neighbor[0] < grid.shape[0]
                and 0 <= neighbor[1] < grid.shape[1]
                and grid[neighbor] == 1
            ):
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


def gen_fp(xlim: int = 32, ylim: int = 32):
    # fp = np.random.choice([0, 1], (xlim, ylim), p=[0.3, 0.7])
    fp = np.ones((xlim, ylim), dtype=np.int8)
    fp[15, :] = 0
    return fp


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


def get_candidate_dirs(current, xlim, ylim):
    candidate_dirs = []
    for idir in current + np.array(EXAMINE_DIRS8):
        if 0 <= idir[0] < xlim and 0 <= idir[1] < ylim:
            candidate_dirs.append(idir)
    return candidate_dirs


def walk_on_wall(fp, current):
    for dir in EXAMINE_DIRS8:
        continue


class Pixel:
    pGrid = []

    def __init__(self, index=None, p_type=1):
        self.neighbors = []
        self.type = p_type  # 0: wall, 1: walkable, for now
        self.visited = False
        self.index = index

    def swap_status(self, other):
        self.type, other.type = other.type, self.type
        self.visited, other.visited = other.visited, self.visited
        self.neighbors, other.neighbors = other.neighbors, self.neighbors

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
                idirs = get_candidate_dirs(np.array([i, j]), n, m)
                nbs = extract_from_2d_array(Pixel.pGrid, idirs)
                Pixel.pGrid[i][j].neighbors = nbs

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
        next = self.pick_from_candidates(self.agent.neighbors)
        # self.agent.swap_status(next)
        # self.agent.type = 0  # reset
        # self.agent = next
        # self.agent.type = 1
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
                [path[i][1], path[i + 1][1]],
                [path[i][0], path[i + 1][0]],
                "r-",
                lw=10,
                alpha=0.03,
            )

    @staticmethod
    def draw_only_start_end(start, end):
        plt.scatter(start[1], start[0], color="g", marker="o")
        plt.scatter(end[1], end[0], color="b", marker="s")

    @staticmethod
    def show():
        plt.show()


def optimize_single_step():
    pass


def main():
    # settings
    # np.random.seed(0)
    xlim, ylim = 32, 32

    fp = gen_fp(xlim, ylim)
    Pixel.from_grid(fp)
    p_grid = Pixel.pGrid

    blocked, walkable = separate_pixels(p_grid)

    sp = gen_sample_points(walkable, 10)

    # optimize
    door = Agent(blocked[0])
    print(door.agent.type)
    best_score = 1000
    best_pos = door.agent
    for _ in range(100):
        score_avg = 0
        for pairs in combinations(sp, 2):
            grid = Pixel.to_grid()
            s = pairs[0].index
            e = pairs[1].index
            _, score = aStar(grid, s, e)
            score_avg += score
        score_avg /= len(sp) * (len(sp) - 1) / 2
        if best_score > score_avg:
            best_score = score_avg
            best_pos = door.agent
        door.step()

    door.set_to(best_pos)

    # visualize
    grid = Pixel.to_grid()
    Visualize.draw_grid(grid)
    for pairs in combinations(sp, 2):
        s = pairs[0].index
        e = pairs[1].index
        path, _ = aStar(grid, s, e)
        if path:
            Visualize.draw_path(path, s, e)

    Visualize.show()


if __name__ == "__main__":
    main()
