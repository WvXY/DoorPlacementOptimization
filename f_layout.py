from f_primitives import FVertex, FEdge, FFace, FRoom
from g_navmesh import NavMesh

import numpy as np


class FLayout(NavMesh):
    def __init__(self):
        super().__init__()
        self.set_default_types(FVertex, FEdge, FFace)

        self.clear()
        self.rooms = set()
        # self.outer_walls = set()
        # self.inner_walls = set()

    def init_rooms(self):
        """Create rooms from faces blocked by edges"""

        def visit_face(f, room):
            if f.is_visited:
                return
            f.is_visited = True
            room.faces.add(f)
            for fa in f.adjs:
                if f.get_shared_edge(fa).is_blocked:
                    continue
                visit_face(fa, room)

        self.reset_all_visited(self.faces)
        self.rooms = set()
        not_visited = self.faces.copy()
        while not_visited:
            room = FRoom()
            visit_face(not_visited.pop(), room)
            self.rooms.add(room)
            not_visited = [f for f in self.faces if not f.is_visited]
        return True

    # def set_room_connections(self, adj_m):
    #     for i in range(len(adj_m)):
    #         for j in range(i + 1, len(adj_m)):
    #             if adj_m[i, j] == 1:
    #                 self.rooms[i].adjs.add(self.rooms[j])
    #                 self.rooms[j].adjs.add(self.rooms[i])

    def set_room_connections(self):
        adj_m = np.zeros((len(self.rooms), len(self.rooms)))
        for wall in self.get_inner_walls():
            f1, f2 = wall.face, wall.twin.face
            r1 = self.__find_room_from_face(f1)
            r2 = self.__find_room_from_face(f2)
            r1.add_adj(r2)
            r2.add_adj(r1)

    def __find_room_from_face(self, f):
        for room in self.rooms:
            if f in room.faces:
                return room
        return None

    # utils
    def clear(self):
        """Clear all vertices, edges, faces"""
        FFace.clear()
        FEdge.clear()
        FVertex.clear()

    def get_by_eid(self, eid):
        for e in self.edges:
            if e.eid == eid:
                return e
        return None

    def get_inner_walls(self):
        return [e for e in self.edges if e.is_blocked and e.twin]

    def get_outer_walls(self):
        return [e for e in self.edges if e.is_blocked and not e.twin]

    def get_by_rid(self, rid):
        return next((r for r in self.rooms if r.rid == rid), None)

    # unused
    def clean(self):
        """Remove inactive vertices, edges, faces"""
        self.verts = [v for v in self.verts if v.is_active]
        self.edges = [e for e in self.edges if e.is_active]
        self.faces = [f for f in self.faces if f.is_active]


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from u_data_loader import Loader
    from u_visualization import Visualizer
    from u_geometry import add_vertex

    ld = Loader(".")
    ld.load_w_walls_case(3)
    ld.optimize()

    vis = Visualizer()

    fp = FLayout()
    fp.create_mesh(ld.vertices, ld.edges, 0)
    fp.init_rooms()

    rooms = list(fp.rooms)
    for r in rooms:
        print(f"Room: {r} | {[f.fid for f in r.faces]}")

    fp.set_room_connections()

    r0 = fp.get_by_rid(0)
    r3 = fp.get_by_rid(2)
    walls0 = r0.get_wall_edges()
    print(f"Room {r0.rid} adjs: {[r.rid for r in r0.adjs]}")

    e03 = r0.get_shared_edge(r3)
    print(f"e03: {[e.eid for e in e03]}")

    for room in rooms:
        center = room.get_center()
        vis.draw_point(center, c="r")
        vis.draw_room(room)

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

    vis.draw_half_edges(walls0)

    # vis.draw_half_edges(f10.half_edges)
    # vis.draw_half_edges(f5.half_edges, c="r")
    # vis.draw_half_edges(f11.half_edges, c="g")
    # vis.draw_half_edges(f9.half_edges, c="b")
    # vis.draw_half_edges(f7.half_edges, c="y")

    vis.draw_mesh(fp, show=False, draw_text="vef")
    plt.show()
