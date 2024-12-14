import numpy as np

# from time import time

from geometry import Point
from visualizer import Visualizer
from navmesh import NavMesh
from loader import Loader

# from optimizer import Optimizer

# settings
case_id = "0a"
sample_size = 300
np_seed_id = 0


def path_length(path):
    length = 0
    for i in range(len(path) - 1):
        length += np.linalg.norm(path[i].xy - path[i + 1].xy)
    return length


np.random.seed(np_seed_id)
ld = Loader(".")
ld.load_w_walls_case(case_id)

nm = NavMesh()
nm.create(ld.vertices, ld.indices, 0)
vis = Visualizer()
vis.draw_mesh(nm, show=False)


path_lens = 0
valid_samples = 0
while valid_samples < sample_size:
    start = Point(np.random.rand(2))
    end = Point(np.random.rand(2))

    tripath = nm.find_tripath(start, end)
    if tripath is None:
        continue

    valid_samples += 1
    path = nm.simplify(tripath, start, end)
    path_lens += path_length(path)
    vis.draw_linepath(path, c="r", lw=10, a=1 / np.sqrt(sample_size))

cost = path_lens / sample_size

vis.show(
    f"Result | Case:{case_id} | Sample Size:{sample_size} | cost:{cost:.2f}"
)
