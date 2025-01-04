from f_primitives import FVertex, FEdge, FFace, FRoom
from g_navmesh import NavMesh


class FLayout(NavMesh):
    def __init__(self):
        super().__init__()
        self.set_default_types(FVertex, FEdge, FFace)

        self.clear()
        self.rooms = []
        self.outer_walls = []
        self.inner_walls = []

    def init_rooms(self):
        """Create rooms from faces blocked by edges"""

        def visit_face(f, room):
            if f.is_visited:
                return
            f.is_visited = True
            room.faces.append(f)
            for fa in f.adjs:
                if f.get_shared_edge(fa).is_blocked:
                    continue
                visit_face(fa, room)

        self.reset_all_visited(self.faces)
        self.rooms = []
        not_visited = self.faces
        while not_visited:
            room = FRoom()
            visit_face(not_visited[0], room)
            self.rooms.append(room)
            not_visited = [f for f in self.faces if not f.is_visited]
        return True

    def clear(self):
        FFace.clear()
        FEdge.clear()
        FVertex.clear()

    def get_by_eid(self, eid):
        for e in self.edges:
            if e.eid == eid:
                return e
        return None

    def clean(self):
        self.verts = [v for v in self.verts if v.is_active]
        self.edges = [e for e in self.edges if e.is_active]
        self.faces = [f for f in self.faces if f.is_active]


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from u_data_loader import Loader
    from u_visualization import Visualizer
    from u_geometry import add_vertex

    ld = Loader(".")
    ld.load_w_walls_case(2)
    ld.optimize()

    fp = FLayout()
    fp.create_mesh(ld.vertices, ld.edges, 0)
    fp.init_rooms()

    rooms = fp.rooms
    for r in rooms:
        print(f"Room: {r} | {[f.fid for f in r.faces]}")

    # fp.reconnect_closed_edges()
    # fp.create_rooms()

    # e17 = FEdge.get_by_eid(17)
    # v, e, f = add_vertex(e17, [0.2, 0.1])
    # fp.append(v=v, e=e, f=f)

    # e6 = Edge.get_by_eid(6)
    # v, e, f = split_edge(e6, [0.7, 0.5], Point=RPoint, Edge=REdge, Face=RFace)
    # fp.append(v=v, e=e, f=f)

    # ===debug===
    # f10 = FFace.get_by_fid(10)
    # f5 = FFace.get_by_fid(5)
    # f9 = FFace.get_by_fid(9)
    # f11 = FFace.get_by_fid(11)
    # f7 = FFace.get_by_fid(7)

    vis = Visualizer()

    # vis.draw_half_edges(f10.half_edges)
    # vis.draw_half_edges(f5.half_edges, c="r")
    # vis.draw_half_edges(f11.half_edges, c="g")
    # vis.draw_half_edges(f9.half_edges, c="b")
    # vis.draw_half_edges(f7.half_edges, c="y")

    vis.draw_mesh(fp, show=False, draw_text="vef")
    plt.show()
