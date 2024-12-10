import numpy as np
import matplotlib.pyplot as plt
import heapq

from torch.onnx.symbolic_opset9 import true_divide

from geometry import Node, Point, Edge, Face, Mesh


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
        path = [start]
        apex = start
        left = start
        right = start
        iapex = 0

        i = 0
        # for i in range(len(tripath) - 1):
        while i < len(tripath) - 1:
            new_left, new_right = tripath[i+1].get_portal(tripath[i])
            if MathUtils.is_counter_clockwise(apex, right, new_right, True):
                if apex == right or MathUtils.is_clockwise(apex, left, new_right):
                    right = new_right
                else:
                    path.append(left)
                    apex = right = left
                    continue

            if MathUtils.is_clockwise(apex, left, new_left, True):
                if apex == left or MathUtils.is_counter_clockwise(apex, right, new_left):
                    left = new_left
                else:
                    path.append(right)
                    apex = left = right
                    continue

        path.append(end)
        return path

class MathUtils:
    @staticmethod
    def triarea2(a, b, c):
        return (b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)
        # return np.cross(b.xy - a.xy, c.xy - a.xy)

    @staticmethod
    def is_clockwise(a, b, c, can_be_collinear=False):
        if can_be_collinear:
            return MathUtils.triarea2(a, b, c) >= 0
        return MathUtils.triarea2(a, b, c) > 0

    @staticmethod
    def is_counter_clockwise(a, b, c, can_be_collinear=False):
        if can_be_collinear:
            return MathUtils.triarea2(a, b, c) <= 0
        return MathUtils.triarea2(a, b, c) > 0
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
