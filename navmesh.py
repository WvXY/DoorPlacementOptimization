from copy import deepcopy

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

    def get_portals(self, tripath):
        portals = []
        for i in range(len(tripath) - 1):
            left, right = tripath[i + 1].get_shared_edge(tripath[i])
            if left is None or right is None:
                print("Error: portal is None")
            portals.append(left)
            portals.append(right)
        return portals

    def funnel_algorithm(self, tripath, start: Node, end: Node):
        portal_apex = start
        portal_left = start
        portal_right = start
        path = [portal_apex]
        portal_apex_index = 0
        portal_left_index = 0
        portal_right_index = 0
        npoints = 1

        portals = self.get_portals(tripath)

        max_points = len(portals)

        i = 0
        while i < max_points // 2 and npoints < max_points:
            left = portals[i * 2]
            right = portals[i * 2 + 1]
            # print(
            #     f"portal_left: {portal_left_index}, "
            #     f"portal_right: {portal_right_index}, "
            #     f"portal_apex: {portal_apex_index}"
            # )
            print(
                "triarea l", MathUtils.triarea2(portal_apex, portal_left, left)
            )
            print(
                "triarea r",
                MathUtils.triarea2(portal_apex, portal_right, right),
            )
            print(portal_apex.x, portal_apex.y)

            if MathUtils.triarea2(portal_apex, portal_right, right) <= 0:
                if (
                    portal_apex == portal_right
                    or MathUtils.triarea2(portal_apex, portal_left, right) > 0
                ):
                    portal_right = right
                    portal_right_index = i
                else:
                    path.append(portal_left)
                    npoints += 1

                    portal_apex = portal_left
                    portal_apex_index = portal_left_index

                    portal_left = portal_apex
                    portal_right = portal_apex
                    portal_left_index = portal_apex_index
                    portal_right_index = portal_apex_index
                    i = portal_apex_index + 1
                    continue

            if MathUtils.triarea2(portal_apex, portal_left, left) >= 0:
                if (
                    portal_apex == portal_left
                    or MathUtils.triarea2(portal_apex, portal_right, left) < 0
                ):
                    portal_left = left
                    portal_left_index = i
                    print(f"portal_left_index: {portal_left_index}")
                else:
                    path.append(portal_right)
                    npoints += 1

                    portal_apex = portal_right
                    portal_apex_index = portal_right_index
                    portal_left = portal_right = portal_apex
                    portal_left_index = portal_right_index = portal_apex_index
                    i = portal_apex_index + 1
                    continue

            i += 1

        # Append the end point
        path.append(end)
        return path


class MathUtils:
    @staticmethod
    def triarea2(a, b, c):
        # return (b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)
        return np.cross((b.xy - a.xy) * 100.0, (c.xy - a.xy) * 100.0)

    @staticmethod
    def is_clockwise(a, b, c, can_be_collinear=False):
        if can_be_collinear:
            return MathUtils.triarea2(a, b, c) >= 0
        return MathUtils.triarea2(a, b, c) > 0

    @staticmethod
    def is_counter_clockwise(a, b, c, can_be_collinear=False):
        if can_be_collinear:
            return MathUtils.triarea2(a, b, c) <= 0
        return MathUtils.triarea2(a, b, c) < 0


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
