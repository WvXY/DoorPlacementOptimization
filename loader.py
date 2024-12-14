import numpy as np


class Loader:
    def __init__(self, root_dir=None):
        self.__root_dir = root_dir

    def get_case(self, idx):
        return {
            0: np.array(
                [
                    [0, 0],
                    [1, 0],
                    [1, 0.8],
                    [0.6, 0.6],
                    [0.6, 1.2],
                    [0, 1],
                ],
                dtype=np.float32,
            ),
            1: np.array(
                [
                    [0, 0],
                    [1, 0],
                    [1, 1],
                    [0, 1],
                ],
                dtype=np.float32,
            ),
            2: np.array(
                [
                    [0, 0],
                    [1, 0],
                    [1, 1],
                    [0, 1],
                    [0.5, 0.5],
                ],
                dtype=np.float32,
            ),
            3: self.load_obj("/assets/test_room3.obj"),
            4: self.load_obj("/assets/test_room4.obj"),
            5: self.load_obj("/assets/test_room5.obj"),
        }[idx]
    
    def get_fp_w_walls(self, idx):
        return self.load_obj("/assets/fp_w_walls_{}.obj".format(idx))
    
    def set_root_dir(self, root_dir):
        self.__root_dir = root_dir

    def load_obj(self, file_path):
        normalize = lambda x: (x - np.min(x)) / (np.max(x) - np.min(x))
        return normalize(np.delete(self.read_obj(file_path)[0], 1, 1))

    def reformat_obj(self, obj_file, out_file):
        with open(obj_file, "r") as f:
            lines = f.readlines()

        with open(out_file, "w") as f:
            for line in lines:
                if line.startswith("v "):
                    f.write(line)
                elif line.startswith("f "):
                    new_line = [ls.split("/")[0] for ls in line.split(" ")]
                    f.write(" ".join(new_line) + "\n")

    def read_obj(self, obj_file):
        with open(self.__root_dir + obj_file, "r") as f:
            lines = f.readlines()
        vertices = []
        faces = []
        for line in lines:
            if line.startswith("v "):
                vertices.append([float(x) for x in line.split(" ")[1:]])
            elif line.startswith("f "):
                new_line = [ls.split("/")[0] for ls in line.split(" ")]
                faces.append([int(x) for x in new_line[1:]])
        return vertices, faces

    def write_obj(self, vertices, faces, out_file):
        with open(out_file, "w") as f:
            for vertex in vertices:
                f.write("v " + " ".join([str(x) for x in vertex]) + "\n")
            for face in faces:
                f.write("f " + " ".join([str(x) for x in face]) + "\n")

