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
