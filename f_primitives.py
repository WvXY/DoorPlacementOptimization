from g_primitives import Point, Edge, Face
from g_navmesh import NavMesh


class FInfo:
    def __init__(self):
        self.room = None
        self.is_visited = False


class FPoint(Point, FInfo):
    def __init__(self, xy):
        Point.__init__(self, xy)
        FInfo.__init__(self)


class FFace(Face, FInfo):
    def __init__(self):
        Face.__init__(self)
        FInfo.__init__(self)

    def merge(self, other: "FFace"):
        e = self.get_shared_edge(other)
        if e is None or e.is_visited:
            return False
        if e.is_blocked:
            return False

        e.disconnect()

        e.is_visited = True
        e.twin.is_visited = True
        return True


class FEdge(Edge, FInfo):
    def __init__(self, origin, to):
        Edge.__init__(self, origin, to)
        FInfo.__init__(self)

    def disconnect(self):
        if self.is_visited:
            return False
        if self.is_blocked:
            return False

        super().disconnect()
        self.is_visited = True
        self.twin.is_visited = True
        return True
