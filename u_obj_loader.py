import numpy as np


class UObjData:
    def __init__(self):
        self.verts = None
        self.edges = None
        self.faces = None

    @property
    def vertices(self):
        return self.verts

    @vertices.setter
    def vertices(self, value):
        self.verts = value


class UObjLoader:
    __root_dir = "."

    @classmethod
    def load(cls, obj_path):
        data = cls.__load(obj_path)  # Use cls instead of self
        assert data is not None, f"Failed to load {obj_path}"
        return data

    @classmethod
    def set_root_dir(cls, root_dir):
        cls.__root_dir = root_dir  # Use cls instead of self

    # ----------------- Private -----------------
    @classmethod
    def __load(cls, obj_file):
        obj_data = cls.__load_raw_obj(cls.__root_dir + obj_file)
        cls.__optimize(obj_data)
        cls.__flip_z(obj_data)
        return obj_data

    @staticmethod
    def __load_raw_obj(obj_path):
        with open(obj_path, "r") as f:
            ls = f.readlines()

        vertices, edges, faces = [], [], []
        for l in ls:
            if l.startswith("v "):
                _process_vertices(vertices, l)
            elif l.startswith("l "):
                _process_edges(edges, l)
            elif l.startswith("f "):
                _process_faces(faces, l)

        data = UObjData()
        if vertices:
            data.verts = np.array(vertices, dtype=np.float64)
        if edges:
            data.edges = np.array(edges, dtype=np.int64)
        if faces:
            data.faces = np.array(faces, dtype=np.int64)

        return data

    @staticmethod
    def __optimize(obj_data):
        """remove duplicates and normalize"""
        UObjLoader.__remove_duplicates(obj_data)
        UObjLoader.__normalize(obj_data)

    @staticmethod
    def __remove_duplicates(obj_data):
        vertex_map = {}
        unique_vertices = []
        new_index = 0

        def hash_vertex(vertex):
            return "".join([str(round(x, 6)) for x in vertex])

        for i, vertex in enumerate(obj_data.verts):
            if hash_vertex(vertex) not in vertex_map:
                vertex_map[hash_vertex(vertex)] = new_index
                unique_vertices.append(vertex)
                new_index += 1

        if obj_data.edges is not None:
            obj_data.edges = [
                (
                    vertex_map[hash_vertex(obj_data.verts[start])],
                    vertex_map[hash_vertex(obj_data.verts[end])],
                )
                for start, end in obj_data.edges
            ]
        if obj_data.faces is not None:
            obj_data.faces = [
                (
                    vertex_map[hash_vertex(obj_data.verts[face[0]])],
                    vertex_map[hash_vertex(obj_data.verts[face[1]])],
                    vertex_map[hash_vertex(obj_data.verts[face[2]])],
                )
                for face in obj_data.faces
            ]
        obj_data.verts = np.array(unique_vertices)

    @staticmethod
    def __normalize(obj_data):
        normalize = lambda x: (x - np.min(x)) / (np.max(x) - np.min(x))
        obj_data.verts = normalize(np.delete(obj_data.verts, 1, 1))

    @staticmethod
    def __flip_z(obj_data):
        obj_data.verts[:, 1] = 1 - obj_data.verts[:, 1]


# ----------------- Utility functions -----------------
def _process_edges(edges_list, raw_data):
    # "l 1 2 3 4" -> [0, 1, 2, 3]
    edges_raw = [int(i) - 1 for i in raw_data.split(" ")[1:]]

    if len(edges_raw) == 2:
        edges_list.append(edges_raw)
    elif len(edges_raw) >= 3:
        for i in range(len(edges_raw) - 1):
            edges_list.append([edges_raw[i], edges_raw[i + 1]])
    return True


def _process_faces(faces_list, raw_data):
    # "f 1/1/1 2/2/2 3/3/3" -> [0, 1, 2] only first matter
    face_raw = [ls.split("/")[0] for ls in raw_data.split(" ")]

    if len(face_raw) != 3:
        return False

    faces_list.append([int(x) - 1 for x in face_raw[1:]])
    return True


def _process_vertices(vertices_list, raw_data):
    # "v 1.0 2.0 3.0" -> [1.0, 2.0, 3.0]
    vertices_list.append([float(x) for x in raw_data.split(" ")[1:]])
    return True
