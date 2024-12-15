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
        super().__init__(xy, id)
        # super(RInfo).__init__()


class RTriangle(Face, RInfo):
    def __init__(self):
        super().__init__()


class REdge(Edge, RInfo):
    def __init__(self, origin, to):
        super().__init__(origin, to)


class Room(Face):
    __id = 0

    def __init__(self):
        self.id = Room.__id
        Room.__id += 1

        self.faces = []
        self.edges = []
        self.nodes = []
        self.type = 0
        self.inner_walls = []
        self.outer_walls = []


class FloorPlan(NavMesh):
    def __init__(self):
        super().__init__()
        self.Node = RPoint
        self.Face = RTriangle
        self.Edge = REdge

        self.rooms = []
        self.outer_walls = []
        self.inner_walls = []

    def init(self, mesh: Mesh):
        center = np.array([0.5, 0.5])

    def init_rooms(self):
        for f in self.faces:
            f.visited = False

        for e in self.edges:
            e.visited = False

    def find_rooms(self):
        self.init_rooms()

        all_visited = False
        while not all_visited:
            all_visited = True
            for e in self.fixed_edges:
                if not e.visited:
                    all_visited = False
                    room = Room()
                    self.rooms.append(room)
                    self.loop_edges(e, room)

    def loop_edges(self, e: REdge, room: Room):
        if e.visited:
            return

        e.visited = True
        if e in self.border_edges:
            room.outer_walls.append(e)
        else:
            room.inner_walls.append(e)

        self.loop_edges(e.next, room)


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from u_data_loader import Loader

    ld = Loader(".")
    ld.load_w_walls_case(3)
    ld.optimize()

    print(ld.vertices)

    fp = FloorPlan()
    fp.create(ld.vertices, ld.edges, 0)
    fp.find_rooms()

    print(fp.rooms[0].outer_walls)
    print(fp.rooms[0].inner_walls)
    print(fp.rooms[1].outer_walls)
    print(fp.rooms[1].inner_walls)
