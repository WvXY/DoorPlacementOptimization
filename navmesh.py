import numpy as np

# import torch
import pygmsh

import matplotlib.pyplot as plt
from matplotlib import patches

from obj_process import reformat_obj, read_obj


class Cases:
    @staticmethod
    def polygon(idx):
        return {
            0: np.array(
                [
                    [0, 0],
                    [1, 0],
                    [1, 0.8],
                    [0.6, 0.6],
                    [0.6, 1.2],
                    [0, 1],
                ],
                dtype=np.float32,
            ),
            1: np.array(
                [
                    [0, 0],
                    [1, 0],
                    [1, 1],
                    [0, 1],
                ],
                dtype=np.float32,
            ),
            2: np.array(
                [
                    [0, 0],
                    [1, 0],
                    [1, 1],
                    [0, 1],
                    [0.5, 0.5],
                ],
                dtype=np.float32,
            ),
            3: Cases.load_obj("assets/test_room3.obj"),
            4: Cases.load_obj("assets/test_room4.obj"),
            5: Cases.load_obj("assets/test_room5.obj"),
        }[idx]

    @staticmethod
    def load_obj(file_path):
        normalize = lambda x: (x - np.min(x)) / (np.max(x) - np.min(x))
        return normalize(np.delete(read_obj(file_path)[0], 1, 1))


class Node:
    __vid = 0

    def __init__(self, pos, idx=None):
        self.idx = idx
        self.pos = pos
        self.next = []
        self.prev = []

        self.edges = []
        self.faces = []
        self.border = False
        self.vid = Node.__vid
        Node.__vid += 1

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    @property
    def z(self):
        return self.pos[2]

    @property
    def xy(self):
        return self.pos[:2]

    @property
    def neighbors(self):
        return set(self.next + self.prev)

    # def move(self, dx, dy) -> None:
    #     if self.border:
    #         return
    #     xy_old = self.xy.copy()
    #     self.xy += [dx, dy]
    #     for f in self.faces:
    #         if f.flipped:
    #             self.xy = xy_old
    #             return

    def remove_duplicate(self):
        self.next = set(self.next)
        self.prev = set(self.prev)
        self.edges = set(self.edges)
        self.faces = set(self.faces)

    @xy.setter
    def xy(self, value):
        self._xy = value


class Edge:
    def __init__(self, origin, to):
        # half edge with direction origin -> to
        self.origin = origin
        self.to = to
        self.face = None
        self.twin = None
        self.next = None
        self.prev = None

        self.is_wall = False

    @property
    def outside(self):
        return not self.twin

    @property
    def gid(self):
        return self.face.gid

    def dir(self):
        return (self.to.xy - self.origin.xy) / self.length()

    def orth(self):
        return np.array([dir[1], -dir[0]])

    def length(self):
        return np.linalg.norm(self.to.xy - self.origin.xy)

    def intersect(self, other):
        pass

    @staticmethod
    def get_all_blocked(edges: list):
        return [e for e in edges if e.is_wall]


# alias
Point = Node
Vertex = Node
Line = Edge


class Face:
    def __init__(self):
        self.nodes = []
        self.gid = 0
        self.half_edges = []
        self.adj_faces = []
        self.center = None

    @property
    def area(self):
        area = 0
        for i in range(3):
            j = (i + 1) % 3
            area += (
                    self.nodes[i].x * self.nodes[j].y - self.nodes[j].x * self.nodes[i].y
            )
        return area / 2

    @property
    def flipped(self):
        return self.area < 0

    @property
    def neighbors(self):
        return self.adj_faces

    @property
    def xy(self):
        return self.center

    @property
    def x(self):
        return self.center[0]

    @property
    def y(self):
        return self.center[1]

    def set_adj_faces(self):
        self.adj_faces = []
        for e in self.half_edges:
            if e.twin:
                self.adj_faces.append(e.twin.face)
        return self.adj_faces

    def remove_duplicate(self):
        self.nodes = set(self.nodes)
        self.half_edges = set(self.half_edges)

    def set_center(self):
        if not self.nodes:
            return
        else:
            xys = [n.xy for n in self.nodes]
            self.center = np.average(xys, axis=0)

    def get_portal(self, other):
        for e in self.half_edges:
            if e.twin and e.twin.face == other:
                return e.origin, e.to
        return None


class Mesh:
    def __init__(self):
        self.faces = []
        self.edges = []
        self.nodes = []

        self.blocked_edges = None

    @property  # alias
    def vertices(self):
        return self.nodes

    def create(self, polygon, mesh_size=0.1):
        with pygmsh.geo.Geometry() as geom:
            geom.add_polygon(
                polygon,
                mesh_size=mesh_size,
            )
            mesh = geom.generate_mesh()
            # return mesh.points, mesh.cells_dict["triangle"]
        self.from_mesh(mesh.points, mesh.cells_dict["triangle"])

    def from_mesh(self, nodes, faces):
        self.clear()

        # nodes
        for i, xy in enumerate(nodes):
            self.nodes.append(Node(xy[:2], i))

        # faces
        for i, f in enumerate(faces):
            face = Face()
            face.nodes = [
                self.nodes[f[0]],
                self.nodes[f[1]],
                self.nodes[f[2]],
            ]
            self.faces.append(face)

            for j in f:
                self.nodes[j].faces.append(face)

        for i, (fi, fj, fk) in enumerate(faces):
            # prev i - k - j - i
            self.nodes[fi].prev.append(self.nodes[fk])
            self.nodes[fj].prev.append(self.nodes[fi])
            self.nodes[fk].prev.append(self.nodes[fj])
            # next i - j - k - i
            self.nodes[fi].next.append(self.nodes[fj])
            self.nodes[fj].next.append(self.nodes[fk])
            self.nodes[fk].next.append(self.nodes[fi])

            eij = Edge(self.nodes[fi], self.nodes[fj])
            ejk = Edge(self.nodes[fj], self.nodes[fk])
            eki = Edge(self.nodes[fk], self.nodes[fi])

            # face.half_edges
            eij.next, ejk.next, eki.next = ejk, eki, eij
            eij.prev, ejk.prev, eki.prev = eki, eij, ejk
            eij.face, ejk.face, eki.face = (
                self.faces[i],
                self.faces[i],
                self.faces[i],
            )

            self.edges += [eij, ejk, eki]
            self.faces[i].half_edges = [eij, ejk, eki]

            # node.edges
            self.nodes[fi].edges += [eij, eki]
            self.nodes[fj].edges += [eij, ejk]
            self.nodes[fk].edges += [ejk, eki]

        # finalize
        self.set_twin()
        self.set_nodes_info()
        self.set_faces_info()
        self.blocked_edges = Edge.get_all_blocked(self.edges)

    def set_twin(self):
        n = len(self.edges)
        for i in range(n):
            ei = self.edges[i]
            if ei.twin:
                continue

            for j in range(i + 1, n):
                ej = self.edges[j]
                if ej.twin:
                    continue

                if ei.origin == ej.to and ei.to == ej.origin:
                    ei.twin, ej.twin = ej, ei

    def set_nodes_info(self):
        for e in self.edges:
            if e.twin is None:
                self.nodes[e.origin.idx].border = True
                self.nodes[e.to.idx].border = True
                e.is_wall = True

    def set_faces_info(self):
        for f in self.faces:
            f.set_adj_faces()
            f.set_center()

    def clear(self):
        self.faces.clear()
        self.edges.clear()
        self.nodes.clear()

    def get_node_by_vid(self, vid):
        for n in self.nodes:
            if n.vid == vid:
                return n
        return None


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
        fs = self.get_point_inside_face(start)
        fe = self.get_point_inside_face(end)

        if fs is None or fe is None:
            return None

        tripath = self.find_rough_path(fs, fe)[0]
        return self.funnel_algorithm(tripath, start, end)

    def find_rough_path(self, start: Face, end: Face):
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
                return path, f_score[end]

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

    def funnel_algorithm(self, tripath, start_point: Node, end_point:Node):
        # portals = get_portals(rough_path, nav_mesh)  # Each portal is a shared edge
        path = [start_point]
        apex = start_point

        left_edge, right_edge = tripath[0].get_portal(tripath[1])

        # for portal in portals[1:]:
        for i in range(2, len(tripath)):
            new_left, new_right = tripath[i].get_portal(tripath[i - 1])

            # Narrow the funnel as needed to stay within the polygons
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
        return np.cross(left.xy - apex.xy, right.xy - apex.xy) < 0



class Draw:
    def __init__(self):
        self.ax, self.fig = plt.subplots()

    def draw_point(self, point, c="r", s=60):
        plt.scatter(point.x, point.y, c=c, s=s)

    def draw_linepath(self, path, c, s=60):
        plt.plot([n.x for n in path], [n.y for n in path], c=c, lw=2)

    def draw_tripath(self, tripath):
        for f in tripath:
            if f is None:
                continue
            plt.fill([n.x for n in f.nodes], [n.y for n in f.nodes], "b", alpha=0.2)

    def draw_mesh(self, mesh: Mesh, title=None, show=True):
        for f in mesh.faces:
            if f is None:
                continue

            tri = [n.xy for n in f.nodes]
            # c = np.ones(3) * f.gid
            c = np.zeros(3)
            # c[int(f.gid)] = 1
            self.fig.add_patch(patches.Polygon(tri, color=c, alpha=0.1))

        for e in mesh.edges:
            if e is None:
                continue
            ori, to = e.origin, e.to
            if e.is_wall:
                self.fig.plot([ori.x, to.x], [ori.y, to.y], "k", lw=2)
            # elif int(e.twin.gid) != int(e.gid):
            #     ax.plot([ori.x, to.x], [ori.y, to.y], "b", lw=2)

        if title:
            self.fig.set_title(title)
        plt.axis("equal")

        if show:
            plt.show()

    def show(self):
        plt.show()


class PathUtils:
    def __init__(self):
        pass


def intersection(l1: Line, l2: Line):
    x1, y1 = l1.origin.xy
    x2, y2 = l1.to.xy
    x3, y3 = l2.origin.xy
    x4, y4 = l2.to.xy
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    if den == 0:
        return None

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den

    if 0 < t < 1 and 0 < u < 1:
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return (x, y)
    else:
        return None


def main():
    # from time import time

    np.random.seed(0)
    i_case = 0

    nm = NavMesh()
    nm.create(Cases.polygon(i_case), 0.2)

    draw = Draw()
    draw.draw_mesh(nm, show=False)

    # p1 = Point(np.array([0.9, 0.5]))
    # f1 = nm.get_point_inside_face(p1)
    # plt.scatter(p1.x, p1.y, c="b", s=100)
    # if f1:
    #     plt.fill([n.x for n in f1.nodes], [n.y for n in f1.nodes], "b", alpha=0.2)

    # p2 = Point(np.array([0.2, 0.2]))
    # f2 = nm.get_point_inside_face(p2)
    # plt.scatter(p2.x, p2.y, c="b", s=100)
    # if f2:
    #     plt.fill([n.x for n in f2.nodes], [n.y for n in f2.nodes], "b", alpha=0.2)

    # for i in range(30):
    #     p1 = Point(np.random.rand(2))
    #     p2 = Point(np.random.rand(2))
    #
    #     path = nm.find_path(p1, p2)
    #     if path:
    #         nm.simplify_path(path)
    #         nm.draw_path(path, np.random.rand(3))

    p1 = Point(np.array([0.9, 0.5]))
    p2 = Point(np.array([0.1, 0.8]))
    path = nm.find_path(p1, p2)
    # draw.draw_tripath(path)
    draw.draw_point(p1, c="g", s=100)
    draw.draw_point(p2, c="r", s=100)
    draw.draw_linepath(path, "k", 2)

    draw.show()


if __name__ == "__main__":
    main()
