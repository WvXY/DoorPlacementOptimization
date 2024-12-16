import numpy as np
import tqdm

from u_data_loader import Loader
from f_layout import FloorPlan, RPoint, RFace, REdge
from u_visualization import Visualizer

# from time import time
from u_geometry import split_edge
from f_optimization import Optimizer, OptiAgent

# settings
case_id = "5"
sample_size = 100
np_seed_id = 0


def path_length(path):
    length = 0
    for i in range(len(path) - 1):
        length += np.linalg.norm(path[i].xy - path[i + 1].xy)
    return length


np.random.seed(np_seed_id)
ld = Loader(".")
ld.load_w_walls_case(case_id)
ld.optimize()

fp = FloorPlan()
fp.create_mesh(ld.vertices, ld.edges, 0)
fp.reconnect_closed_edges()
fp.create_rooms()

# e0 = REdge.get_by_eid(0)
# v, e, f = split_edge(e0, [0.2, 0.5], Point=RPoint, Edge=REdge, Face=RFace)
# fp.append(v=v, e=e, f=f)

# for face in fp.faces:
#     print(f"face: {face.fid} | {[f.fid for f in face.neighbors]}")
#     print(f"edges: {[e.eid for e in face.half_edges]}")


# draw
vis = Visualizer()
vis.draw_mesh(fp, show=False, draw_text="ef")
# vis.show()

agent = OptiAgent()

path_lens = 0
valid_samples = 0
pbar = tqdm.tqdm(total=sample_size)  # showing progress

while valid_samples < sample_size:
    start = RPoint(np.random.rand(2))
    end = RPoint(np.random.rand(2))

    tripath = fp.find_tripath(start, end)
    if tripath is None:
        continue

    valid_samples += 1
    path = fp.simplify(tripath, start, end)
    path_lens += path_length(path)
    vis.draw_linepath(path, c="r", lw=10, a=1 / np.sqrt(sample_size))

    pbar.update(1)

cost = path_lens / sample_size
pbar.close()

vis.show(
    f"Result "
    f"| Case:{case_id} "
    f"| Sample Size:{sample_size} "
    f"| cost:{cost:.2f}"
)
