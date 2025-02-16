import unittest


class FloorPlanTest(unittest.TestCase):
    from u_data_loader import Loader

    ld = Loader("..")

    def test_room_generation(self):
        from f_layout import FLayout

        self.ld.load_w_walls_case(3)

        fp = FLayout()
        fp.create_mesh(self.ld.vertices, self.ld.edges, 0)

        self.assertEqual(len(fp.rooms), 5)

        room_faces = []
        for room in fp.rooms:
            fids = [f.fid for f in room.faces]
            fids.sort()
            room_faces.append(fids)

        self.assertIn([0, 6, 7, 13, 14, 15, 18, 19], room_faces)

    def test_split_edge(self):
        from f_layout import FLayout
        from f_primitives import FVertex, FFace, FEdge
        from u_geometry import split_half_edge

        self.ld.load_w_walls_case(0)

        fp = FLayout()
        fp.create_mesh(self.ld.vertices, self.ld.edges, 0)

        # modify the mesh
        e0 = FEdge.get_by_eid(2)
        v, e, f = split_half_edge(e0, [0.65, 0.55])
        fp.append(v=v, e=e, f=f)

        v3 = FVertex.get_by_vid(3)
        v3.pos = [0.6, 0.8]

        start = FVertex([0.5, 0.55])
        end = FVertex([0.55, 0.45])

        tripath = fp.find_tripath(start, end)
        path = fp.simplify(tripath, start, end)

        expected_res = [10, 3, 9, 11]
        observed_res = [p.vid for p in path]
        self.assertEqual(expected_res, observed_res)


if __name__ == "__main__":
    unittest.main()
