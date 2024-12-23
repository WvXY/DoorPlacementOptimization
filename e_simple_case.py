import matplotlib.pyplot as plt
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

from u_geometry import add_vertex


# settings
case_id = "0a"

np.random.seed(0)
ld = Loader(".")
ld.load_w_walls_case(case_id)
ld.optimize()

nm = FloorPlan()
nm.set_default_types(RPoint, REdge, RFace)
nm.create_mesh(ld.vertices, ld.edges, 0)
# nm.reconnect_closed_edges()
# nm.create_rooms()

inner_walls = nm.inner_fixed_edges

e0 = nm.get_by_eid(0)
agent = Agent(e0, np.array([0.5, 0.8]))
agent.activate()
# print(len(agent.new_verts), len(agent.new_edges), len(agent.new_faces))
nm.append(agent.new_verts, agent.new_edges, agent.new_faces)

# for e in agent.new_edges:
#     print(f"e{e.eid}= next: {e.next.eid}, prev: {e.prev.eid}")

# dv, de, df = agent.deactivate()
# # # print([e.eid for e in de])
# nm.remove(dv, de, df)

# print(agent.move_by(-0.2))

# v, e, f = split_edge(e0, [0.45, 0.5], Point=RPoint, Edge=REdge, Face=RFace)
# nm.append(v, e, f)


# start = Point(np.array([0.2, 0.4]))
# end = Point(np.array([0.6, 0.6]))
#
# tripath = nm.find_tripath(start, end)
# path = nm.simplify(tripath, start, end)
#
# print(f"tripath: {tripath}")


# draw
vis = Visualizer()


def score_func(path):
    score = 0
    for i in range(len(path) - 1):
        score += np.linalg.norm(path[i].xy - path[i + 1].xy)
    return score


sample_points = np.random.rand(2000, 2)
scores, locs = [], []

###############################
# metropolis hastings
T = 1


def dx():
    return np.random.normal(1) * 0.06


def pi(fx, T=T):
    return np.exp(-fx / T)


def proposal(agent):
    agent.move_by(dx())


def f():
    score = 0
    i = 0
    for i in range(1000):
        start = Point(sample_points[i])
        end = Point(sample_points[i + 1])

        tripath = nm.find_tripath(start, end)
        path = nm.simplify(tripath, start, end)
        if path:
            i += 1
            score += score_func(path)
    return score / i


# run
for l in range(100):

    old_score = f()
    old_pos = agent.center.copy()

    proposal(agent)
    new_score = f()

    alpha = np.exp((old_score - new_score) / T)
    print(f"alpha: {alpha}")
    u = np.random.rand()
    if u >= alpha:
        agent.set_pos(old_pos)  # reject

    print(
        f"agent: {agent.center} | old_score: {old_score} | new_score: {new_score}"
    )

vis.draw_mesh(nm, show=False, draw_text="vef")

# vis.draw_tripath(tripath)
# vis.draw_point(start, c="g", s=40, m="s")
# vis.draw_point(end, c="r", s=40)

# for f in nm.faces:
#     # vis.draw_half_edges(f.half_edges, c="b", lw=0.003)
#     c = np.random.rand(3) * 0.8
#     vis.draw_tri_half_edges(f, c=c, lw=0.006)

# for e in inner_walls:
#     vis.draw_linepath([e.ori, e.to], c="b", lw=8, a=1)

vis.show(f"Result")

# plt.plot(locs, scores)
# plt.show()
