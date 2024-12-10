import numpy as np
# from time import time

from geometry import Point
from visualizer import Visualizer
from navmesh import NavMesh
from loader import Loader
# from optimizer import Optimizer

np.random.seed(0)
i_case = 5

nm = NavMesh()
ld = Loader()
nm.create(ld.get_case(i_case), 0.8)

vis = Visualizer()
vis.draw_mesh(nm, show=False)
# draw.show()

# p1 = Point(np.array([0.9, 0.5]))
# f1 = nm.get_point_inside_face(p1)
# plt.scatter(p1.x, p1.y, c="b", s=100)
# if f1:
#     plt.fill([n.x for n in f1.nodes], [n.y for n in f1.nodes], "b", alpha=0.2)

# p2 = Point(np.array([0.2, 0.2]))
# f2 = nm.get_point_inside_face(p2)
# plt.scatter(p2.x, p2.y, c="b", s=100)
# if f2:
#     plt.fill([n.x for n in f2.nodes], [n.y for n in f2.nodes], "b", alpha=0.2)

# for i in range(30):
#     p1 = Point(np.random.rand(2))
#     p2 = Point(np.random.rand(2))
#
#     path = nm.find_path(p1, p2)
#     if path:
#         nm.simplify_path(path)
#         nm.draw_path(path, np.random.rand(3))

start = Point(np.array([0.2, 0.2]))
end = Point(np.array([0.9, 0.6]))
tripath = nm.find_rough_path(start, end)[0]
vis.draw_tripath(tripath)

path = nm.funnel_algorithm(tripath, start, end)
vis.draw_point(start, c="g", s=100)
vis.draw_point(end, c="r", s=100)
vis.draw_linepath(path, "b", 2)

vis.show("navmesh")