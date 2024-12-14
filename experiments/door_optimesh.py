import unittest
import numpy as np

from geometry import Point
from visualizer import Visualizer
from navmesh import NavMesh
from loader import Loader
from debug_log import DbgLogger

from geometry import _GeoBase

should_draw = True

logger = DbgLogger()


class NavmeshTest(unittest.TestCase):
    ld = Loader("..")

    def reset(self):
        _GeoBase.reset_guid()
        np.random.seed(0)

    def draw(self, nm, start, end, tripath, path):
        vis = Visualizer()
        vis.draw_mesh(nm, show=False)
        vis.draw_point(start, c="g", s=100)
        vis.draw_point(end, c="r", s=100)
        vis.draw_linepath(path, "b", 2)
        vis.draw_tripath(tripath)
        vis.show("navmesh")

    def test_simple_path(self):
        self.reset()
        logger.info("------------test_simple_path------------")
        self.ld.load_wo_wall_case(2)

        nm = NavMesh()
        nm.create(self.ld.vertices, self.ld.indices)

        start = Point(np.array([0.2, 0.9]))
        end = Point(np.array([0.1, 0.2]))

        tripath = nm.find_tripath(start, end)
        path = nm.simplify(tripath, start, end)

        if should_draw:
            self.draw(nm, start, end, tripath, path)

        expected_res = [52, 11, 53]
        observed_res = [p.guid for p in path]
        logger.debug(f"observed_res: {observed_res}")
        logger.debug(f"expected_res: {expected_res}")
        self.assertEqual(expected_res, observed_res)

    def test_complicated_path(self):
        self.reset()
        logger.info("------------test_complicated_path--------------")
        self.ld.load_wo_wall_case(4)

        nm = NavMesh()
        nm.create(self.ld.vertices, self.ld.indices)

        start = Point(np.array([0.8, 0.2]))
        end = Point(np.array([0.6, 0.25]))

        tripath = nm.find_tripath(start, end)
        path = nm.simplify(tripath, start, end)

        if should_draw:
            self.draw(nm, start, end, tripath, path)

        expected_res = [372, 34, 33, 28, 25, 24, 22, 21, 20, 8, 9, 373]
        observed_res = [p.guid for p in path]
        logger.debug(f"observed_res: {observed_res}")
        logger.debug(f"expected_res: {expected_res}")
        self.assertEqual(expected_res, observed_res)


if __name__ == "__main__":
    unittest.main()
