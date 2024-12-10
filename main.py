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

start = Point(np.array([0.2, 0.2]))
end = Point(np.array([0.9, 0.6]))
tripath = nm.find_tripath(start, end)
vis.draw_tripath(tripath)

path = nm.simplify(tripath, start, end)
vis.draw_point(start, c="g", s=100)
vis.draw_point(end, c="r", s=100)
vis.draw_linepath(path, "b", 2)

vis.show("navmesh")
