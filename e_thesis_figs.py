import numpy as np
import matplotlib.pyplot as plt

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


start = Point(np.array([0.96, 0.29]))
end = Point(np.array([0.45, 0.63]))

tripath = nm.find_tripath(start, end)
path, track = nm.simplify(tripath, start, end)

# draw
vis = Visualizer()
fig = vis.get_fig()
vis.draw_mesh(nm, show=False)
vis.draw_tripath(tripath)
vis.draw_point(start, c="g", s=50, m="s")
vis.draw_point(end, c="r", s=50)
# vis.draw_linepath(path, c="g", lw=2, a=1)

for e in inner_walls:
    vis.draw_linepath([e.ori, e.to], c="k", lw=2, a=1)

for e in outer_walls:
    vis.draw_linepath([e.ori, e.to], c="k", lw=2, a=1)

for v in nm.vertices:
    vis.draw_point(v, c="k", s=40)


portals = track[0]
for i, p in enumerate(portals):
    if i >= 4:
        # fig.scatter(p[0].x, p[0].y, c="g", s=60, marker="s")
        # fig.scatter(p[1].x, p[1].y, c="g", s=60, marker="s")
        fig.plot([p[0].x, p[1].x], [p[0].y, p[1].y], "--", c="g", lw=1)
    else:
        fig.plot([p[0].x, p[1].x], [p[0].y, p[1].y], "--", c="b", lw=1)

funnels = track[1]

funnel = funnels[2]
apex, left, right = funnel
fig.plot([apex.x, left.x], [apex.y, left.y], c="c", lw=2)
fig.plot([apex.x, right.x], [apex.y, right.y], c="c", lw=2)
fig.plot([left.x, right.x], [left.y, right.y], c="b", lw=2)
vis.fig.fill(
    [n.x for n in funnel],
    [n.y for n in funnel],
    "b",
    alpha=0.5,
)

paths = track[2]
path = paths[1][:2]
vis.draw_linepath(path, c="g", lw=2, a=1)  # path is always the same (refs)

# vis.fig.fill(
#     [n.x for n in tk],
#     [n.y for n in tk],
#     "r",
#     alpha=0.5,
# )


# for f in nm.faces:
#     # vis.draw_half_edges(f.half_edges, c="b", lw=0.003)
#     c = np.random.rand(3) * 0.8
#     vis.draw_tri_half_edges(f, c=c, lw=0.006)

vis.show(None, axis_off=True)
