import numpy as np


class Loader:
    def __init__(self, root_dir="."):
        self.__root_dir = root_dir
        self.faces = None
        self.edges = None
        self.vertices = None
        self.success = False

    def load_wo_wall_case(self, idx):
        self.success = self._load("/assets/fp_wo_wall_{}.obj".format(idx))

    def load_w_walls_case(self, idx):
        self.success = self._load("/assets/fp_w_walls_{}.obj".format(idx))

    def load_closed_rooms_case(self, idx):
        self.success = self._load("/assets/fp_closed_rooms_{}.obj".format(idx))

    def load_final_case(self, idx):
        self.success = self._load("/assets/fp_final_{}.obj".format(idx))

    def set_root_dir(self, root_dir):
        self.__root_dir = root_dir

    def _load(self, obj_file):
        self._clear()
        self._load_obj(self.__root_dir + obj_file)
        self._optimize()
        self._flip_z()  # flip y in 2D
        return True

    def _clear(self):
        self.faces = None
        self.edges = None
        self.vertices = None

    def _load_obj(self, obj_file):
        with open(obj_file, "r") as f:
            ls = f.readlines()

        vertices, edges, faces = [], [], []
        for l in ls:
            if l.startswith("v "):
                _process_vertices(vertices, l)
            elif l.startswith("l "):
                _process_edges(edges, l)
            elif l.startswith("f "):
                _process_faces(faces, l)

        if vertices:
            self.vertices = np.array(vertices, dtype=np.float64)
        if edges:
            self.edges = np.array(edges, dtype=np.int64)
        if faces:
            self.faces = np.array(faces, dtype=np.int64)

    def _optimize(self):
        """remove duplicates and normalize"""
        self._remove_duplicates()
        self._normalize()

    def _remove_duplicates(self):
        vertex_map = {}
        unique_vertices = []
        new_index = 0

        def hash_vertex(vertex):
            return "".join([str(round(x, 6)) for x in vertex])
            # return tuple(vertex)

        for i, vertex in enumerate(self.vertices):
            if hash_vertex(vertex) not in vertex_map:
                vertex_map[hash_vertex(vertex)] = new_index
                unique_vertices.append(vertex)
                new_index += 1

        # Update edge list using the vertex_map
        if self.edges is not None:
            self.edges = [
                (
                    vertex_map[hash_vertex(self.vertices[start])],
                    vertex_map[hash_vertex(self.vertices[end])],
                )
                for start, end in self.edges
            ]
        if self.faces is not None:
            self.faces = [
                (
                    vertex_map[hash_vertex(self.vertices[face[0]])],
                    vertex_map[hash_vertex(self.vertices[face[1]])],
                    vertex_map[hash_vertex(self.vertices[face[2]])],
                )
                for face in self.faces
            ]
        self.vertices = np.array(unique_vertices)

    def _normalize(self):
        normalize = lambda x: (x - np.min(x)) / (np.max(x) - np.min(x))
        # delete y-axis because its zero in our 2D case and normalize
        self.vertices = normalize(np.delete(self.vertices, 1, 1))

    def _flip_z(self):
        self.vertices[:, 1] = 1 - self.vertices[:, 1]


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


# no need at the moment
# def write_obj(self, vertices, indices, faces, out_file):
#     with open(out_file, "w") as f:
#         for vertex in vertices:
#             f.write("v " + " ".join([str(x) for x in vertex]) + "\n")
#         for face in faces:
#             f.write("f " + " ".join([str(x) for x in face]) + "\n")


if __name__ == "__main__":
    ld = Loader()
    ld.set_root_dir(".")
    ld.load_closed_rooms_case(2)
    # ld.load_closed_rooms_case(1)
    print(ld.vertices)
    print(ld.edges)
