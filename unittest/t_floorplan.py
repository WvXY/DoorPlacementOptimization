import unittest


class FloorPlanTest(unittest.TestCase):
    from u_data_loader import Loader

    ld = Loader("..")

    def test_room_generation(self):
        from f_layout import FloorPlan

        self.ld.load_w_walls_case(3)
        self.ld.optimize()

        fp = FloorPlan()
        fp.create_mesh(self.ld.vertices, self.ld.edges, 0)
        fp.reconnect_closed_edges()
        fp.create_rooms()

        self.assertEqual(len(fp.rooms), 5)

        room_faces = []
        for room in fp.rooms:
            fids = [f.fid for f in room.faces]
            fids.sort()
            room_faces.append(fids)

        self.assertIn([0, 6, 7, 13, 14, 15, 18, 19], room_faces)

    def test_split_edge(self):
        from f_layout import FloorPlan, RPoint, RFace, REdge
        from u_geometry import add_vertex

        self.ld.load_w_walls_case(0)
        self.ld.optimize()

        fp = FloorPlan()
        fp.create_mesh(self.ld.vertices, self.ld.edges, 0)
        fp.reconnect_closed_edges()
        fp.create_rooms()

        # modify the mesh
        e0 = REdge.get_by_eid(2)
        v, e, f = add_vertex(
            e0, [0.65, 0.55], Point=RPoint, Edge=REdge, Face=RFace
        )
        fp.append(v=v, e=e, f=f)

        v3 = RPoint.get_by_vid(3)
        v3.pos = [0.6, 0.8]

        start = RPoint([0.5, 0.55])
        end = RPoint([0.55, 0.45])

        tripath = fp.find_tripath(start, end)
        path = fp.simplify(tripath, start, end)

        expected_res = [10, 3, 9, 11]
        observed_res = [p.vid for p in path]
        self.assertEqual(expected_res, observed_res)


if __name__ == "__main__":
    unittest.main()
