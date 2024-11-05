def reformat_obj(obj_file, out_file):
    with open(obj_file, "r") as f:
        lines = f.readlines()

    with open(out_file, "w") as f:
        for line in lines:
            if line.startswith("v "):
                f.write(line)
            elif line.startswith("f "):
                new_line = [ls.split("/")[0] for ls in line.split(" ")]
                f.write(" ".join(new_line) + "\n")


def read_obj(obj_file):
    with open(obj_file, "r") as f:
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


def write_obj(vertices, faces, out_file):
    with open(out_file, "w") as f:
        for vertex in vertices:
            f.write("v " + " ".join([str(x) for x in vertex]) + "\n")
        for face in faces:
            f.write("f " + " ".join([str(x) for x in face]) + "\n")
