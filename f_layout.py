from heapq import merge

import numpy as np

from g_primitives import Point, Edge, Face
from g_mesh import Mesh
from g_navmesh import NavMesh


class RInfo:
    def __init__(self):
        self.room = None
        self.visited = False


class RPoint(Point, RInfo):
    def __init__(self, xy, id):
        Point.__init__(self, xy, id)
        RInfo.__init__(self)


class RFace(Face, RInfo):
    def __init__(self):
        Face.__init__(self)
        RInfo.__init__(self)

    def merge(self, other: "RFace"):
        e = self.get_shared_edge(other)
        if e is None or e.visited:
            return False
        if e.is_blocked:
            return False

        e.prev.next = e.twin.next
        e.next.prev = e.twin.prev
        e.twin.prev.next = e.next
        e.twin.next.prev = e.prev
        e.visited = True
        e.twin.visited = True
        return True


class REdge(Edge, RInfo):
    def __init__(self, origin, to):
        Edge.__init__(self, origin, to)
        RInfo.__init__(self)


class Room(RFace):
    __id = 0

    def __init__(self):
        super().__init__()
        self.id = Room.__id
        Room.__id += 1

        self.faces = []
        # self.edges = []
        # self.nodes = []
        self.type = 0
        self.inner_walls = []
        self.outer_walls = []


class FloorPlan(NavMesh):
    def __init__(self):
        super().__init__()
        self.Node = RPoint
        self.Face = RFace
        self.Edge = REdge

        self.rooms = []
        self.outer_walls = []
        self.inner_walls = []

    def init(self, mesh: Mesh):
        center = np.array([0.5, 0.5])

    def reconnect_closed_edges(self):
        self.reset_visited(self.edges)
        for f in self.faces:
            for ff in f.adj_faces:
                f.merge(ff)

    def create_rooms(self):
        self.reset_visited(self.edges)

        wall_edges = [e for e in self.edges if e.is_blocked]
        remains = [e for e in wall_edges if not e.visited]
        while remains:
            room = Room()
            self.traverse_edges(remains[0])
            self.rooms.append(room)
            room.faces = set([e.face for e in remains if e.visited])
            room.half_edges = [e for e in remains if e.visited]
            remains = [e for e in wall_edges if not e.visited]

    def traverse_edges(self, e: REdge):
        if e.visited:
            return
        e.visited = True
        self.traverse_edges(e.next)

    def reset_visited(self, rgeos):
        for g in rgeos:
            g.visited = False


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from u_data_loader import Loader
    from u_visualization import Visualizer

    ld = Loader(".")
    ld.load_w_walls_case(3)
    ld.optimize()

    fp = FloorPlan()
    fp.create(ld.vertices, ld.edges, 0)
    fp.reconnect_closed_edges()
    fp.create_rooms()

    print(len(fp.rooms))
    for r in fp.rooms:
        print([f.fid for f in r.faces])
        print([e.eid for e in r.half_edges])

    vis = Visualizer()
    vis.draw_mesh(fp, show=False, draw_text="ef")
    plt.show()
