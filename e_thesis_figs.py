import numpy as np

from g_primitives import Point
from u_data_loader import Loader
from g_navmesh import NavMesh
from u_visualization import Visualizer

# from time import time

from f_optimization import Optimizer, OptiAgent

# settings
case_id = "5"

np.random.seed(0)
ld = Loader(".")
ld.load_w_walls_case(case_id)
ld.optimize()

nm = NavMesh()
nm.create_mesh(ld.vertices, ld.edges, 0)
inner_walls = nm.inner_fixed_edges
outer_walls = nm.border_edges

agent = OptiAgent()
agent.xy = np.array([0.5, 0.5])


start = Point(np.array([0.2, 0.3]))
end = Point(np.array([0.1, 0.6]))

tripath = nm.find_tripath(start, end)
path = nm.simplify(tripath, start, end)

# draw
vis = Visualizer()
vis.draw_mesh(nm, show=False)
# vis.draw_tripath(tripath)
# vis.draw_point(start, c="g", s=40, m="s")
# vis.draw_point(end, c="r", s=40)
# vis.draw_linepath(path, c="k", lw=10, a=0.3)

for e in inner_walls:
    vis.draw_linepath([e.ori, e.to], c="k", lw=2, a=1)

for e in outer_walls:
    vis.draw_linepath([e.ori, e.to], c="k", lw=2, a=1)

for v in nm.vertices:
    vis.draw_point(v, c="k", s=40)

for f in nm.faces:
    # vis.draw_half_edges(f.half_edges, c="b", lw=0.003)
    c = np.random.rand(3) * 0.8
    vis.draw_tri_half_edges(f, c=c, lw=0.006)

vis.show(None, axis_off=True)
