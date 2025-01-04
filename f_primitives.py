from g_primitives import Vertex, Edge, Face


class _FInfo:
    def __init__(self):
        self.room = None
        self.is_visited = False
        self.is_active = True


class FVertex(Vertex, _FInfo):
    def __init__(self, xy):
        Vertex.__init__(self, xy)
        _FInfo.__init__(self)


class FEdge(Edge, _FInfo):
    def __init__(self, origin, to):
        Edge.__init__(self, origin, to)
        _FInfo.__init__(self)

    def disconnect(self):
        if self.is_visited:
            return False
        if self.is_blocked:
            return False

        super().disconnect()
        self.is_visited = True
        self.twin.is_visited = True
        return True


class FFace(Face, _FInfo):
    def __init__(self):
        Face.__init__(self)
        _FInfo.__init__(self)

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


class FRoom(_FInfo):
    def __init__(self):
        _FInfo.__init__(self)
        self.faces = []
        self.half_edges = []


# Alias
FNode = FVertex
FPoint = FVertex
