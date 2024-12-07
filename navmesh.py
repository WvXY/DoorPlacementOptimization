import numpy as np
import matplotlib.pyplot as plt
import heapq

from geometry import Node, Point, Edge, Face, Mesh
from pynavmesh_test import start


class NavMesh(Mesh):
    def __init__(self):
        super().__init__()
        self.visited = [False] * len(self.nodes)

    def dist(self, a, b):
        if isinstance(a, Face) and isinstance(b, Face):
            return np.linalg.norm(a.center - b.center)
        else:
            return np.linalg.norm(a.xy - b.xy)

    def find_path(self, start: Point, end: Point):
        tripath = self.find_rough_path(start, end)[0]
        return self.funnel_algorithm(tripath, start, end)

    def find_rough_path(self, start: Point, end: Point):
        start = self.get_point_inside_face(start)
        end = self.get_point_inside_face(end)
        if start is None or end is None:
            return None

        open_set = []
        heapq.heappush(open_set, (0, start))  # Priority queue with (f_score, node)
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.dist(start, end)}

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
                t_g_score = g_score[current] + self.dist(current, neighbor)
                if t_g_score < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = t_g_score
                    f_score[neighbor] = t_g_score + self.dist(neighbor, end)
                    if neighbor not in [i[1] for i in open_set]:  # Avoid duplicate nodes
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return None, float("inf")

    def get_point_inside_face(self, point):
        for f in self.faces:
            if f is None or f.flipped:
                continue
            if self.point_in_face(point, f):
                return f
        return None

    @staticmethod
    def point_in_face(point, face):
        for i in range(3):
            j = (i + 1) % 3
            if np.cross(face.nodes[j].xy - face.nodes[i].xy, point.xy - face.nodes[i].xy) < 0:
                return False
        return True

    def funnel_algorithm(self, tripath, start: Node, end: Node):
        tail = []
        left = []
        right = []
        tail.append(start)
        new_left, new_right = tripath[0].get_portal(tripath[1])
        left.append(new_left)
        right.append(new_right)

        for i in range(1, len(tripath)-1):
            new_left, new_right = tripath[i].get_portal(tripath[i+1])
            if new_left != left[-1]:
                if MathUtils.triarea2(tail[-1], left[-1], new_left) >= 0:
                    left[-1] = new_left     # on the right of left_node
                else:
                    left.append(new_left)   # on the left side

            if new_right != right[-1]:
                if MathUtils.triarea2(tail[-1], right[-1], new_right) <= 0:
                    right[-1] = new_right   # on the left of right_node
                else:
                    right.append(new_right) # on the right

            # left.append(new_left)
            # right.append(new_right)
        return right

class Detour:
    pass

class Recast:
    pass


class MathUtils:
    @staticmethod
    def triarea2(o:Node, a:Node, b:Node):
        return np.cross(a.xy - o.xy, b.xy - o.xy)
#
#
# def intersection(l1: Line, l2: Line):
#     x1, y1 = l1.origin.xy
#     x2, y2 = l1.to.xy
#     x3, y3 = l2.origin.xy
#     x4, y4 = l2.to.xy
#     den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
#
#     if den == 0:
#         return None
#
#     t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
#     u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den
#
#     if 0 < t < 1 and 0 < u < 1:
#         x = x1 + t * (x2 - x1)
#         y = y1 + t * (y2 - y1)
#         return (x, y)
#     else:
#         return None
