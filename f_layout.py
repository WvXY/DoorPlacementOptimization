from g_primitives import Point, Edge, Face
from g_navmesh import NavMesh


class RInfo:
    def __init__(self):
        self.room = None


class RPoint(Point, RInfo):
    def __init__(self, xy):
        Point.__init__(self, xy)
        RInfo.__init__(self)


class RFace(Face, RInfo):
    def __init__(self):
        Face.__init__(self)
        RInfo.__init__(self)

    def merge(self, other: "RFace"):
        e = self.get_shared_edge(other)
        if e is None or e.is_visited:
            return False
        if e.is_blocked:
            return False

        e.disconnect()

        e.is_visited = True
        e.twin.is_visited = True
        return True


class REdge(Edge, RInfo):
    def __init__(self, origin, to):
        Edge.__init__(self, origin, to)
        RInfo.__init__(self)

    def disconnect(self):
        if self.is_visited:
            return False
        if self.is_blocked:
            return False

        super().disconnect()
        self.is_visited = True
        self.twin.is_visited = True
        return True


class Room(RFace):
    __id = 0

    def __init__(self):
        super().__init__()
        self.id = Room.__id
        Room.__id += 1

        self.faces = []
        self.type = 0
        self.inner_walls = []
        self.outer_walls = []


class FloorPlan(NavMesh):
    def __init__(self):
        super().__init__()
        self.Node = RPoint
        self.Face = RFace
        self.Edge = REdge

        self.clear()
        self.rooms = []
        self.outer_walls = []
        self.inner_walls = []

    def reconnect_closed_edges(self):
        self.reset_all_visited(self.edges)
        for e in self.edges:
            e.disconnect()

    def create_rooms(self):
        self.reset_all_visited(self.edges)

        wall_edges = [e for e in self.edges if e.is_blocked]
        remains = [e for e in wall_edges if not e.is_visited]
        while remains:
            room = Room()
            self.traverse_edges(remains[0])
            self.rooms.append(room)
            room.faces = set([e.face for e in remains if e.is_visited])
            room.half_edges = [e for e in remains if e.is_visited]
            remains = [e for e in wall_edges if not e.is_visited]

    def traverse_edges(self, e: REdge):
        if e.is_visited:
            return
        e.is_visited = True
        self.traverse_edges(e.next)

    def clear(self):
        self.Face.clear()
        self.Edge.clear()
        self.Node.clear()


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from u_data_loader import Loader
    from u_visualization import Visualizer
    from u_geometry import split_edge

    ld = Loader(".")
    ld.load_w_walls_case(3)
    ld.optimize()

    fp = NavMesh()
    fp.set_default_types(Node=RPoint, Edge=REdge, Face=RFace)
    fp.create_mesh(ld.vertices, ld.edges, 0)
    # fp.reconnect_closed_edges()
    # fp.create_rooms()

    e17 = Edge.get_by_eid(17)
    v, e, f = split_edge(e17, [0.2, 0.1], Point=RPoint, Edge=REdge, Face=RFace)
    fp.append(v=v, e=e, f=f)

    # e6 = Edge.get_by_eid(6)
    # v, e, f = split_edge(e6, [0.7, 0.5], Point=RPoint, Edge=REdge, Face=RFace)
    # fp.append(v=v, e=e, f=f)

    # debug
    f10 = Face.get_by_fid(10)
    f5 = Face.get_by_fid(5)
    f9 = Face.get_by_fid(9)
    f11 = Face.get_by_fid(11)
    f7 = Face.get_by_fid(7)

    vis = Visualizer()

    vis.draw_half_edges(f10.half_edges)
    vis.draw_half_edges(f5.half_edges, c="r")
    vis.draw_half_edges(f11.half_edges, c="g")
    vis.draw_half_edges(f9.half_edges, c="b")
    vis.draw_half_edges(f7.half_edges, c="y")

    vis.draw_mesh(fp, show=False, draw_text="vef")
    plt.show()
