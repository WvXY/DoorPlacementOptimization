import numpy as np

from geometry import Point
from loader import Loader
from navmesh import NavMesh
from visualizer import Visualizer

# from time import time

# from optimizer import Optimizer

# settings
case_id = 6

np.random.seed(0)
ld = Loader(".")
ld.load_w_walls_case(case_id)

nm = NavMesh()
nm.create(ld.vertices, ld.edges, 0)
vis = Visualizer()
vis.draw_mesh(nm, show=False)

start = Point(np.array([0.2, 0.3]))
end = Point(np.array([0.1, 0.6]))
c = np.random.rand(3)

tripath = nm.find_tripath(start, end)

if tripath is None:
    print("No path found")
    vis.show("Mesh")
    exit()

path = nm.simplify(tripath, start, end)

vis.draw_tripath(tripath)
vis.draw_point(start, c="g", s=40, m="s")
vis.draw_point(end, c="r", s=40)
vis.draw_linepath(path, c="k", lw=10, a=0.3)

vis.show(f"Result")
