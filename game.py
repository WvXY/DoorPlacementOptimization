import numpy as np
import matplotlib.pyplot as plt


EXAMINE_DIRS = (
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


def visualize(maze, start, end, path):
    if path:
        path = path + [start]
        path = path[::-1]

        for i in range(len(path) - 1):
            plt.plot(
                [path[i][0], path[i + 1][0]], [path[i][1], path[i + 1][1]], "r-"
            )
        plt.imshow(maze.T, cmap="gray")
        # plt.plot([start[0], end[0]], [start[1], end[1]], 'r-')
        plt.scatter(start[0], start[1], color="g", marker="s")
        plt.scatter(end[0], end[1], color="b", marker="s")
        plt.show()
    else:
        print("No path found")
        plt.imshow(maze.T, cmap="gray")
        # plt.plot([start[0], end[0]], [start[1], end[1]], 'r-')
        plt.scatter(start[0], start[1], color="g", marker="s")
        plt.scatter(end[0], end[1], color="b", marker="s")
        plt.show()


def gen_fp(xlim: int = 32, ylim: int = 32):
    room = np.random.choice([0, 1], (xlim, ylim), p=[0.3, 0.7])
    # room = np.ones((xlim, ylim), dtype=np.int8)
    # room[15, :] = 0
    return room


def find_rooms(fp):
    walls, emptys = [], []
    n, m = fp.shape
    for i in range(n):
        for j in range(m):
            if fp[i, j] == 0:
                walls.append((i, j))
            else:
                emptys.append((i, j))
    return walls, emptys


def gen_sample_points(candidates, n_points=100):
    isp = np.random.choice(candidates.shape[0], n_points)
    sp = candidates[isp]
    return sp


def walk_on_wall(fp, current):
    for dir in EXAMINE_DIRS:
        continue


class Pixel:
    # pGrid = []
    def __init__(self, type=1):
        self.neighbors = []
        self.type = type  # 0: wall, 1: walkable, for now
        self.visited = False

    @staticmethod
    def from_grid(grid):
        n, m = grid.shape
        pixels = []
        for i in range(n):
            row = []
            for j in range(m):
                row.append(Pixel(grid[i, j]))
            pixels.append(row)

        for i in range(n):
            for j in range(m):
                idirs = get_candidate_dirs(np.array([i, j]), n, m)
                nbs = extract_from_2d_array(pixels, idirs)
                pixels[i][j].neighbors = nbs

        return pixels

    @staticmethod
    def to_grid(pixels):
        n, m = len(pixels), len(pixels[0])
        grid = np.empty((n, m))
        for row, r_pixels in enumerate(pixels):
            for col, pixel in enumerate(r_pixels):
                grid[row, col] = pixel.type
        return grid


def extract_from_2d_array(arr, idx):
    ret = []
    for i, j in idx:
        ret.append(arr[i][j])
    return ret


def get_candidate_dirs(current, xlim, ylim):
    candidate_dirs = []
    for idir in current + np.array(EXAMINE_DIRS):
        if 0 <= idir[0] < xlim and 0 <= idir[1] < ylim:
            candidate_dirs.append(idir)
    return candidate_dirs


# class Pxl


def main():
    # settings
    np.random.seed(0)
    xlim, ylim = 24, 32

    fp = gen_fp(xlim, ylim)
    walls, emptys = find_rooms(fp)
    pixels = Pixel.from_grid(fp)

    for p in pixels[5][9].neighbors:
        p.type = 0

    print(len(pixels), len(pixels[0]))
    for rp in pixels:
        for p in rp:
            print(p.type, end="")
        print()

    fp = Pixel.to_grid(pixels)
    s = (0, 0)
    e = (xlim - 1, ylim - 1)
    fp[s] = 1
    fp[e] = 1
    path, score = aStar(fp, s, e)
    visualize(fp, s, e, path=path)

    # place doors and optimize
    # n = 600
    # best_score = 1000
    # door_loc = walls[0]
    # best_door_loc = door_loc
    # while n:
    #     score_sum = 0
    #     current_room = fp.copy()
    #     current_room[door_loc] = 1
    #     for i in range(sample_pairs):
    #         s, e = tuple(start[i]), tuple(end[i])
    #         _, score = aStar(current_room, s, e)
    #         score_sum += score
    #     score_avg = score_sum / sample_pairs
    #     if score_avg < best_score:
    #         best_score = score_avg
    #         best_door_loc = door_loc
    #     door_loc = walls[np.random.randint(0, len(walls))]
    #     n -= 1
    #
    # room[best_door_loc] = 1
    # path, score = aStar(room, start[0], end[0])
    # visualize(room, start[0], end[0], path)

    # ================== Task maze ==================
    # maze = np.random.choice([0, 1], (32, 32), p=[0.3, 0.7])
    # start = (0, 0)
    # end = (31, 31)
    # maze[start] = 1
    # maze[end] = 1

    # best_score = 0
    # best_maze = maze.copy()

    # current_maze = maze.copy()
    # n = 1000
    # while n:
    #     loc = np.random.randint(0, 32, 40).reshape(-1, 2)
    #     # print(loc)
    #     current_maze[loc[:, 0], loc[:, 1]] = -current_maze[loc[:, 0], loc[:, 1]] + 1

    #     maze[start] = 1
    #     maze[end] = 1
    #     path, score = aStar(current_maze, start, end)
    #     print(score)

    #     if score != np.inf and score > best_score:
    #         best_score = score
    #         # best_path = path
    #         best_maze = current_maze.copy()
    #     else:
    #         current_maze = best_maze.copy()
    #     n -= 1

    # path, score = aStar(best_maze, start, end)
    # print(score)
    # visualize(best_maze, start, end, path)


if __name__ == "__main__":
    main()
