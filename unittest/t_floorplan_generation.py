import unittest


class FloorPlanGenTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
