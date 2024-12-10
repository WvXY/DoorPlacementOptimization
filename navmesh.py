import heapq

import numpy as np

from geometry import Node, Point, Face, Mesh
from path_finding import a_star


class NavMesh(Mesh):
    def __init__(self):
        super().__init__()
        # self.visited = [False] * len(self.nodes)

    def find_tripath(self, start: Point, end: Point, dist_func=None):
        start = self.get_point_inside_face(start)
        end = self.get_point_inside_face(end)
        return a_star(start, end, dist_func)[0]

    def simplify(self, tripath, start: Point, end: Point):
        return self.funnel_algorithm(tripath, start, end)

    def get_point_inside_face(self, point):
        for f in self.faces:
            if f is None or f.flipped:
                continue
            if self.is_inside_face(point, f):
                return f
        return None

    @staticmethod
    def is_inside_face(point: Point, face: Face):
        for i in range(3):
            j = (i + 1) % 3
            if (
                np.cross(
                    face.nodes[j].xy - face.nodes[i].xy,
                    point.xy - face.nodes[i].xy,
                )
                < 0
            ):
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
            new_left, new_right = tripath[i + 1].get_portal(tripath[i])
            i += 1
            if MathUtils.is_counter_clockwise(apex, right, new_right, True):
                if apex == right or MathUtils.is_clockwise(
                    apex, left, new_right
                ):
                    right = new_right
                else:
                    path.append(left)
                    apex = right = left
                    continue

            if MathUtils.is_clockwise(apex, left, new_left, True):
                if apex == left or MathUtils.is_counter_clockwise(
                    apex, right, new_left
                ):
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
