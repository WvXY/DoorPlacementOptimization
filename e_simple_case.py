import numpy as np
from copy import deepcopy

from g_primitives import Point
from f_primitives import RPoint, REdge, RFace
from u_data_loader import Loader
from u_visualization import Visualizer

# from time import time
from f_layout import FloorPlan
from o_optimizer import Optimizer
from o_agent import Agent

from u_geometry import split_edge


# settings
case_id = "0a"

np.random.seed(0)
ld = Loader(".")
ld.load_w_walls_case(case_id)
ld.optimize()

nm = FloorPlan()
nm.create_mesh(ld.vertices, ld.edges, 0)
# nm.reconnect_closed_edges()
# nm.create_rooms()

inner_walls = nm.inner_fixed_edges

e0 = nm.get_by_eid(0)
agent = Agent(e0, np.array([0.5, 0.5]))
agent.activate()

nm.append(agent.new_verts, agent.new_edges, agent.new_faces)

# v, e, f = split_edge(e0, [0.45, 0.5], Point=RPoint, Edge=REdge, Face=RFace)
# nm.append(v, e, f)

# e12 = nm.get_by_eid(12)
# e13 = nm.get_by_eid(13)
#
# e12.is_blocked = False
# e13.is_blocked = False


start = Point(np.array([0.2, 0.4]))
end = Point(np.array([0.6, 0.6]))

tripath = nm.find_tripath(start, end)
path = nm.simplify(tripath, start, end)

print(f"tripath: {tripath}")


# draw
vis = Visualizer()
vis.draw_mesh(nm, show=False, draw_text="vef")
vis.draw_tripath(tripath)
vis.draw_point(start, c="g", s=40, m="s")
vis.draw_point(end, c="r", s=40)
vis.draw_linepath(path, c="k", lw=10, a=0.3)

for f in nm.faces:
    # vis.draw_half_edges(f.half_edges, c="b", lw=0.003)
    c = np.random.rand(3) * 0.8
    vis.draw_tri_half_edges(f, c=c, lw=0.006)

for e in inner_walls:
    vis.draw_linepath([e.ori, e.to], c="b", lw=8, a=1)

vis.show(f"Result")
