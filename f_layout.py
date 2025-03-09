import numpy as np

from f_primitives import FVertex, FEdge, FFace, FRoom
from g_navmesh import NavMesh


class FLayout(NavMesh):
    def __init__(self):
        super().__init__()
        self.set_default_types(FVertex, FEdge, FFace)

        self.clear()
        self.rooms = set()
        self.adj_m = None

    def init_rooms(self):
        """Create rooms from faces blocked by edges"""

        def visit_face(f, room):
            if f.is_visited:
                return
            f.visit()
            room.faces.add(f)
            for fa in f.adjs:
                if f.get_shared_edge(fa).is_blocked:
                    continue
                visit_face(fa, room)

        self.reset_all_visit_status(self.faces)
        self.rooms = set()
        not_visited = self.faces.copy()
        while not_visited:
            room = FRoom()
            visit_face(not_visited.pop(), room)
            self.rooms.add(room)
            not_visited = [f for f in self.faces if not f.is_visited]
        return True

    def set_room_connections(self):
        assert len(self.rooms) > 0, "No rooms found"

        adj_m = np.zeros((len(self.rooms), len(self.rooms)))
        for wall in self.get_inner_walls():
            f1, f2 = wall.face, wall.twin.face
            r1 = self.__find_room_from_face(f1)
            r2 = self.__find_room_from_face(f2)
            r1.add_adj(r2)
            r2.add_adj(r1)
            adj_m[r1.rid, r2.rid] = 1
            adj_m[r2.rid, r1.rid] = 1
        self.adj_m = adj_m
        return True

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

    def get_inner_walls(self):
        return [e for e in self.edges if e.is_blocked and e.twin]

    def get_outer_walls(self):
        return [e for e in self.edges if e.is_blocked and not e.twin]

    def get_by_rid(self, rid):
        return next((r for r in self.rooms if r.rid == rid), None)

    def get_by_eid(self, eid):
        return next((e for e in self.edges if e.eid == eid), None)

    # unused
    def clean(self):
        """Remove inactive vertices, edges, faces"""
        self.verts = [v for v in self.verts if v.is_active]
        self.edges = [e for e in self.edges if e.is_active]
        self.faces = [f for f in self.faces if f.is_active]
