import numpy as np

from debug_log import DbgLogger
from geometry import Node, Point, Face, Mesh
from path_finding import a_star


class NavMesh(Mesh):
    def __init__(self):
        super().__init__()

    def find_tripath(self, start: Point, end: Point, dist_func=None):
        start = self.get_point_inside_face(start)
        end = self.get_point_inside_face(end)
        path = a_star(start, end, dist_func)[0]
        return path

    def simplify(self, tripath, start: Point, end: Point):
        if tripath is None:
            return None
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
            e = tripath[i].get_shared_edge(tripath[i + 1])
            left, right = e.origin, e.to
            if left is None or right is None:
                print("Error: portal is None")
                continue
            portals.append((left, right))
        return portals

    def funnel_algorithm(self, tripath, start: Node, end: Node):
        raw_portals = self.get_portals(tripath)
        portals = raw_portals + [(end, end)]

        path = [start]
        apex = left = right = start
        apex_index = left_index = right_index = 0

        i = 0
        while i < len(portals):
            left_pt, right_pt = portals[i]

            # right funnel side
            if MathUtils.triarea2(apex, right, right_pt) <= 0:
                if (
                    apex == right
                    or MathUtils.triarea2(apex, left, right_pt) > 0
                ):
                    right = right_pt
                    right_index = i
                else:
                    if path[-1] != left:
                        path.append(left)

                    apex = left
                    apex_index = left_index
                    left = right = apex
                    left_index = right_index = apex_index
                    i = apex_index + 1
                    continue

            # left funnel side
            if MathUtils.triarea2(apex, left, left_pt) >= 0:
                if apex == left or MathUtils.triarea2(apex, right, left_pt) < 0:
                    left = left_pt
                    left_index = i
                else:
                    if path[-1] != right:
                        path.append(right)

                    apex = right
                    apex_index = right_index
                    left = right = apex
                    left_index = right_index = apex_index
                    i = apex_index + 1
                    continue

            i += 1

        if path[-1] != end:
            path.append(end)

        return path


class MathUtils:
    @staticmethod
    def triarea2(a, b, c):
        if isinstance(a, np.ndarray):
            return (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])
        return (b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)

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
