import unittest

import numpy as np

from g_navmesh import NavMesh
from g_primitives import Point
from g_primitives import _GeoBase
from u_obj_loader import UObjLoader
from u_visualization import Visualizer

should_draw = True


class NavmeshTest(unittest.TestCase):
    def reset(self):
        _GeoBase.reset_guid()
        np.random.seed(0)

    def generate_navmesh(self, file_name):
        data = UObjLoader.load(f"/../assets/{file_name}.obj")
        nm = NavMesh()
        nm.from_obj_data(data)
        return nm

    def draw(self, nm, start, end, tripath, path, title):
        vis = Visualizer()
        vis.draw_mesh(nm).set_axis(title=f"Unittest: navmesh | {title}") \
            .draw_point(start, c="g", s=100).draw_point(end, c="r", s=100) \
            .draw_linepath(path, c="b", s=2).draw_tripath(tripath) \
            .save(f"../results/unittest_navmesh-{title}.png")  # or .show()

    def test_simple_path(self):
        self.reset()
        # logger.info("------------test_simple_path------------")
        obj_name = "fp_wo_wall_2"
        nm = self.generate_navmesh(obj_name)

        start = Point(np.array([0.2, 0.9]))
        end = Point(np.array([0.1, 0.2]))

        tripath = nm.find_tripath(start, end)
        path = nm.simplify(tripath, start, end)

        if should_draw:
            self.draw(nm, start, end, tripath, path, title=obj_name)

        expected_res = [52, 11, 53]
        observed_res = [p.guid for p in path]
        self.assertEqual(expected_res, observed_res)

    def test_complicated_path(self):
        self.reset()
        # logger.info("------------test_complicated_path--------------")
        obj_name = "fp_wo_wall_4"
        nm = self.generate_navmesh(obj_name)

        start = Point(np.array([0.78, 0.83]))
        end = Point(np.array([0.67, 0.8]))

        tripath = nm.find_tripath(start, end)
        path = nm.simplify(tripath, start, end)

        if should_draw:
            self.draw(nm, start, end, tripath, path, title=obj_name)

        expected_res = [372, 34, 33, 28, 25, 24, 22, 21, 20, 8, 9, 13, 373]
        observed_res = [p.guid for p in path]
        self.assertEqual(expected_res, observed_res)


if __name__ == "__main__":
    unittest.main()
