import numpy as np


class Loader:
    def __init__(self, root_dir="."):
        self.__root_dir = root_dir
        self.faces = None
        self.indices = None
        self.vertices = None
        self.success = False

    def load_wo_wall_case(self, idx):
        self.success = self._load("/assets/fp_wo_wall_{}.obj".format(idx))

    def load_w_walls_case(self, idx):
        self.success = self._load("/assets/fp_w_walls_{}.obj".format(idx))

    def _load(self, obj_file):
        self._load_obj(self.__root_dir + obj_file)
        self._optimize_data()
        return True

    def _optimize_data(self):
        normalize = lambda x: (x - np.min(x)) / (np.max(x) - np.min(x))
        # delete y-axis because its zero in our 2D case and normalize
        self.vertices = normalize(np.delete(self.vertices, 1, 1))

    def _load_obj(self, obj_file):
        with open(obj_file, "r") as f:
            ls = f.readlines()

        vertices, indices, faces = [], [], []
        for l in ls:
            if l.startswith("v "):
                _process_vertices(vertices, l)
            elif l.startswith("l "):
                _process_indices(indices, l)
            elif l.startswith("f "):
                _process_faces(faces, l)

        if vertices:
            self.vertices = np.array(vertices)
        if indices:
            self.indices = np.array(indices)
        if faces:
            self.faces = np.array(faces)

    def set_root_dir(self, root_dir):
        self.__root_dir = root_dir

    def remove_duplicates(self):
        # TODO: remove duplicate vertices and update indices and face
        pass


# ----------------- Utility functions -----------------
def _process_indices(indices_list, raw_data):
    # "l 1 2 3 4" -> [0, 1, 2, 3]
    indices_raw = [int(i) - 1 for i in raw_data.split(" ")[1:]]

    if len(indices_raw) == 2:
        indices_list.append(indices_raw)
    elif len(indices_raw) >= 3:
        for i in range(len(indices_raw) - 1):
            indices_list.append([indices_raw[i], indices_raw[i + 1]])
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
    ld.load_wo_wall_case(0)
    ld.load_w_walls_case(0)
    print(ld.vertices)
    print(ld.indices)
