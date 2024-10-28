import numpy as np
import matplotlib.pyplot as plt


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
            if 0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1] and grid[neighbor] == 1:
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + manhattan_dist(neighbor, end)
                    if neighbor not in open_set:
                        open_set.add(neighbor)
    return None, float('inf')

def visualize(maze, start, end, path):
    if path:
        path = path + [start]
        path = path[::-1]

        for i in range(len(path) - 1):
            plt.plot([path[i][0], path[i + 1][0]], [path[i][1], path[i + 1][1]], 'r-')
        plt.imshow(maze.T, cmap='gray')
        # plt.plot([start[0], end[0]], [start[1], end[1]], 'r-')
        plt.scatter(start[0], start[1], color='g', marker='s')
        plt.scatter(end[0], end[1], color="b", marker="s")
        plt.show()
    else:
        print("No path found")
        plt.imshow(maze.T, cmap='gray')
        # plt.plot([start[0], end[0]], [start[1], end[1]], 'r-')
        plt.scatter(start[0], start[1], color='g', marker='s')
        plt.scatter(end[0], end[1], color="b", marker="s")
        plt.show()

def main():
    np.random.seed(0)

    room = np.random.choice([0, 1], (32, 32), p=[0.2, 0.8])
    room[15, :] = 0
    sample_pairs = 100

    # find walls to place doors
    walls = []
    empty = []
    for i in range(32):
        for j in range(32):
            if room[i, j] == 0:
                walls.append((i, j))
            else:
                empty.append((i, j))
    
    # samples
    # start = np.random.randint(0, 32, (sample_pairs, 2)).tolist()
    # end = np.random.randint(0, 32, (sample_pairs, 2)).tolist()
    start = np.random.choice(range(len(empty)), sample_pairs, replace=False)
    end = np.random.choice(range(len(empty)), sample_pairs, replace=False)
    start = [empty[i] for i in start]
    end = [empty[i] for i in end]

    # place doors and optimize
    n = 600
    best_score = 1000
    door_loc = walls[0]
    best_door_loc = door_loc
    while n:
        score_sum = 0
        current_room = room.copy()
        current_room[door_loc] = 1
        for i in range(sample_pairs):
            s, e = tuple(start[i]), tuple(end[i])
            _, score = aStar(current_room, s, e)
            score_sum += score
        score_avg = score_sum / sample_pairs
        if score_avg < best_score:
            best_score = score_avg
            best_door_loc = door_loc
        door_loc = walls[np.random.randint(0, len(walls))]
        n -= 1

    room[best_door_loc] = 1
    path, score = aStar(room, start[0], end[0])
    visualize(room, start[0], end[0], path)

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
