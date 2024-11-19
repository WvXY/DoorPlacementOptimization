import numpy as np
import matplotlib.pyplot as plt

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

        open_set = {start}
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.dist(start, end)}

        while open_set:
            current = min(open_set, key=lambda x: f_score[x])
            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1], f_score[end]

            open_set.remove(current)
            for neighbor in current.neighbors:
                if True:
                    t_g_score = g_score[current] + self.dist(current, neighbor)
                    if t_g_score < g_score.get(neighbor, float("inf")):
                        came_from[neighbor] = current
                        g_score[neighbor] = t_g_score
                        f_score[neighbor] = t_g_score + self.dist(neighbor, end)
                        if neighbor not in open_set:
                            open_set.add(neighbor)
        return None, float("inf")

    def get_point_inside_face(self, point):
        for f in self.faces:
            if f is None:
                continue
            if f.flipped:
                continue
            if self.point_in_face(point, f):
                return f
        return None

    @staticmethod
    def point_in_face(point, face):
        for i in range(3):
            j = (i + 1) % 3
            if (
                    np.cross(
                        face.nodes[j].xy - face.nodes[i].xy, point.xy - face.nodes[i].xy
                    )
                    < 0
            ):
                return False
        return True

    def funnel_algorithm(self, tripath, start_point: Node, end_point: Node):
        path = [start_point]
        apex = start_point

        left_edge, right_edge = tripath[0].get_portal(tripath[1])

        for i in range(2, len(tripath)):
            new_left, new_right = tripath[i - 1].get_portal(tripath[i])
            # plt.plot([new_left.x, new_right.x], [new_left.y, new_right.y], "r", lw=2)
            plt.scatter(new_left.x, new_left.y, c="r", s=60)
            plt.scatter(new_right.x, new_right.y, c="y", s=60)
            if self.is_outside(apex, left_edge, new_left):
                path.append(left_edge)
                apex = left_edge
                left_edge = new_left
            if self.is_outside(apex, right_edge, new_right):
                path.append(right_edge)
                apex = right_edge
                right_edge = new_right

        path.append(end_point)
        return path

    def is_outside(self, apex: Node, left: Node, right: Node):
        return np.cross(left.xy - apex.xy, right.xy - apex.xy) <= 0



# class PathUtils:
#     def __init__(self):
#         pass
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
