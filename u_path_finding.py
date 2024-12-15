import heapq

import numpy as np

from g_primitives import Point


def euclidean_distance(a, b):
    return np.linalg.norm(a.xy - b.xy)


def a_star(
    start: Point,
    end: Point,
    dist_func=None,
):
    if start is None or end is None:
        return None, float("inf")

    if dist_func is None:
        dist_func = euclidean_distance

    open_set = []
    heapq.heappush(open_set, (0, start))  # Priority queue with (f_score, node)
    came_from = {}
    g_score = {start: 0}
    f_score = {start: dist_func(start, end)}

    while open_set:
        current = heapq.heappop(open_set)[1]
        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1], f_score[end]

        for neighbor in current.neighbors:
            print(f"{current.fid}  {neighbor.fid} ")
            if current.get_shared_edge(neighbor).is_blocked:
                continue  # Skip blocked edges

            t_g_score = g_score[current] + dist_func(current, neighbor)
            if t_g_score < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = t_g_score
                f_score[neighbor] = t_g_score + dist_func(neighbor, end)
                if neighbor not in [
                    i[1] for i in open_set
                ]:  # Avoid duplicate nodes
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return None, float("inf")
