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

    def test_complicated_path(self):
        self.reset()
        logger.info("------------test_complicated_path--------------")

        i_case = 5
        nm = NavMesh()
        nm.create(self.ld.get_case(i_case), 0.8)
        start = Point(np.array([0.2, 0.2]))
        end = Point(np.array([0.9, 0.6]))
        tripath = nm.find_tripath(start, end)
        path = nm.simplify(tripath, start, end)

        if should_draw:
            vis = Visualizer()
            vis.draw_mesh(nm, show=False)
            vis.draw_tripath(tripath)
            vis.draw_point(start, c="g", s=100)
            vis.draw_point(end, c="r", s=100)
            vis.draw_linepath(path, "b", 2)
            vis.show("navmesh")

        expected_res = [286, 26, 6, 287]
        observed_res = [p.guid for p in path]
        logger.debug(f"observed_res: {observed_res}")
        logger.debug(f"expected_res: {expected_res}")
        self.assertEqual(expected_res, observed_res)

    def test_simple_path(self):
        self.reset()
        logger.info("------------test_simple_path------------")

        i_case = 0
        nm = NavMesh()
        nm.create(self.ld.get_case(i_case), 0.8)
        start = Point(np.array([0.4, 1.0]))
        end = Point(np.array([0.9, 0.6]))
        tripath = nm.find_tripath(start, end)
        path = nm.simplify(tripath, start, end)

        if should_draw:
            vis = Visualizer()
            vis.draw_mesh(nm, show=False)
            vis.draw_tripath(tripath)
            vis.draw_point(start, c="g", s=100)
            vis.draw_point(end, c="r", s=100)
            vis.draw_linepath(path, "b", 2)
            vis.show("navmesh")

        expected_res = [59, 3, 60]
        observed_res = [p.guid for p in path]
        logger.debug(f"observed_res: {observed_res}")
        logger.debug(f"expected_res: {expected_res}")
        self.assertEqual(expected_res, observed_res)


if __name__ == "__main__":
    unittest.main()
