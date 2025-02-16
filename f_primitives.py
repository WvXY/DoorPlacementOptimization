from g_primitives import Vertex, Edge, Face, _GeoBase


class _FInfo:
    def __init__(self):
        self.room = None
        self.is_active = True


class FVertex(Vertex, _FInfo):
    def __init__(self, xy):
        super().__init__(xy)

    def __hash__(self):
        # for not hashable error
        return hash(self.guid)

    def __repr__(self):
        return f"FVertex {self.vid} ({self.xy[0]:.2f}, {self.xy[1]:.2f})"


class FEdge(Edge, _FInfo):
    def __init__(self, origin, to):
        super().__init__(origin, to)

    def __repr__(self):
        return f"FEdge {self.eid} ({self.ori.vid} -> {self.to.vid})"


class FFace(Face, _FInfo):
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return f"FFace {self.fid} (Verts {[v.vid for v in self.verts]})"


class FRoom(_FInfo, _GeoBase):
    __room_list = []
    __rid = 0

    def __init__(self):
        _GeoBase.__init__(self)
        _FInfo.__init__(self)
        FRoom.__room_list.append(self)
        self.rid = FRoom.__rid
        FRoom.__rid += 1

        self.faces = set()
        self.adjs = set()

    def add_adj(self, room):
        self.adjs.add(room)

    def add_face(self, face):
        self.faces.add(face)

    def replace_face(self, old_face, new_face):
        self.faces.remove(old_face)
        self.faces.add(new_face)

    def remove_faces(self, faces):
        """Remove faces from room: no warning if face not in room"""
        self.faces.difference_update(faces)

    def get_all_edges(self):
        all_edges = set()
        for f in self.faces:
            all_edges.update(f.edges)
        return all_edges

    def get_wall_edges(self):
        all_edges = self.get_all_edges()
        wall_edges = set()
        for e in all_edges:
            if e.twin is None or e.twin not in all_edges:
                wall_edges.add(e)
        return wall_edges

    def get_area(self):
        return sum([f.area for f in self.faces])

    def get_center(self):
        centers = [f.center for f in self.faces]
        areas = [f.area for f in self.faces]
        area_sum = sum(areas)
        x = sum([c[0] * a for c, a in zip(centers, areas)]) / area_sum
        y = sum([c[1] * a for c, a in zip(centers, areas)]) / area_sum
        return (x, y)

    def get_shared_edges(self, other: "FRoom"):
        other_wall_edges = other.get_wall_edges()
        shared_edges = []
        for e in self.get_wall_edges():
            if e.twin in other_wall_edges:
                shared_edges += [e, e.twin]
        return shared_edges

    @property
    def id(self):
        return self.rid

    def get_by_rid(self, rid):
        return self.get_by_(FRoom.__room_list, rid)

    def __repr__(self):
        return f"FRoom {self.rid} (Faces {[f.fid for f in self.faces]}, Adjs {[r.rid for r in self.adjs]})"


# Alias
FNode = FVertex
FPoint = FVertex
