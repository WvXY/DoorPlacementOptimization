from u_geometry import closet_position_on_edge, del_vertex, add_vertex
from f_primitives import FPoint, FEdge, FFace

import numpy as np
from copy import deepcopy, copy


class FDoor:
    def __init__(self, edge, fp=None):
        self.bind_edge = edge
        self.floor_plan = fp

        # self.dir = self.get_dir()

        self.d_len = 0.01

        self.e_len = None
        self.move_limit = None
        self.ratio = None

        self.new = {
            "v": [],
            "e": [],
            "f": []
        }

        self.is_active = False
        self.is_synced = True

        self.__history = {
            "bind_edge": None,
            "center": None,
        }

    # calculations
    def __cal_limits(self):
        return [
            self.d_len / 2.0 / self.e_len,  # lower limit
            1 - self.d_len / 2.0 / self.e_len,  # upper limit
        ]

    def __cal_ratio(self, pos):
        frac = np.linalg.norm(self.bind_edge.ori.xy - pos) / self.e_len
        if (pos - self.bind_edge.ori.xy) @ self.dir > 0:
            return frac
        else:
            return -frac

    # getters
    def get_dir(self):
        return self.bind_edge.get_dir()

    def get_edge_len(self):
        return self.bind_edge.get_length()

    # setters
    def set_floor_plan(self, fp):
        self.floor_plan = fp

    def set_door_center(self, center):
        new_center = center  # closet_position_on_edge(self.bind_edge, pos)
        p = self.__cal_ratio(new_center)
        if not self.__within_limit(p):
            return False

        self.new["v"][0].xy = new_center + self.dir * self.d_len / 2
        self.new["v"][1].xy = new_center - self.dir * self.d_len / 2
        self.ratio = p

    # actions
    def activate(self, center=None):
        if self.is_active:
            return

        # find the first center
        if center is None:
            # if self.__history["ratio"] > 0.5:
            #     new_center = (self.bind_edge.to.xy
            #                   - self.move_limit[0] * self.dir * self.e_len)
            # else:
            #     new_center = (self.bind_edge.ori.xy
            #                   + self.move_limit[0] * self.dir * self.e_len)
            new_center = self.bind_edge.get_mid()
        else:
            new_center = self.__correct_location(center)

        # init some properties
        self.e_len = self.get_edge_len()
        self.ratio = self.__cal_ratio(new_center)
        self.move_limit = self.__cal_limits()

        # Reconstruct mesh and add new v e f
        cut_p0 = new_center + self.dir * self.d_len / 2
        cut_p1 = new_center - self.dir * self.d_len / 2
        self.new["v"], self.new["e"], self.new["f"] = add_vertex(
            self.bind_edge, cut_p0, Point=FPoint, Edge=FEdge, Face=FFace
        )

        v, e, f = add_vertex(
            self.bind_edge, cut_p1, Point=FPoint, Edge=FEdge, Face=FFace
        )
        self.new["v"] += v
        self.new["e"] += e
        self.new["f"] += f

        e[0].is_blocked = False
        e[1].is_blocked = False  # twin of e[0]

        # set properties
        # self.__init_properties()
        self.sync_floor_plan()

        self.is_active = True

    def deactivate(self):
        if not self.is_active:
            return

        # 1 -> 0 is working, but 0 -> 1 is not working
        v_del, e_del, f_del = del_vertex(self.new["v"][1])
        v, e, f = del_vertex(self.new["v"][0])
        v_del.extend(v)
        e_del.extend(e)
        f_del.extend(f)

        # for v in v_del:
        #     v.is_active = False
        # for e in e_del:
        #     e.is_active = False
        # for f in f_del:
        #     f.is_active = False

        self.is_active = False
        self.sync_floor_plan()
        self.new = {
            "v": [],
            "e": [],
            "f": []
        }
        # return v_del, e_del, f_del

    def step(self):
        if not self.is_active:
            RuntimeError("Door is not active")

        delta = np.random.normal(0, 0.05)
        # delta = -0.05
        ratio = self.ratio + delta / self.e_len
        print(f"ratio: {self.ratio} | edge{self.bind_edge.eid} | center: {self.center}")
        self.save_history()

        if not self.__within_limit(ratio):
            print("STEP: to next edge")
            self.deactivate()
            self.__find_next_edge(ratio)
            self.activate()
            print(f"bind_edge: {self.bind_edge.eid} | ratio: {self.ratio} | center: {self.center}")
        else:
            print("STEP: move")
            self.ratio = ratio
            for v in self.new["v"]:
                v.xy += delta * self.dir

    # utility
    def __correct_location(self, loc):
        if self.bind_edge is None:
            return None
        return closet_position_on_edge(self.bind_edge, loc)

    def __within_limit(self, ratio):
        # print(f"fraction: {self.fraction(pos)} pos: {pos}")
        return self.move_limit[0] <= ratio <= self.move_limit[1]

    def __find_next_edge(self, ratio):
        def search_next_edge(vertex):
            for e in vertex.half_edges:
                if (e.is_inner and e.is_active and
                        not (self.bind_edge is e or
                             e is self.bind_edge.twin)):
                    return e
            return None

        if ratio >= self.move_limit[1]:
            v = self.bind_edge.to
            e = search_next_edge(v)
            self.bind_edge = e if e.ori is v else e.twin
        elif ratio <= self.move_limit[0]:
            v = self.bind_edge.ori
            e = search_next_edge(v)
            self.bind_edge = e if e.to is v else e.twin

    def __init_properties(self):
        # self.dir = self.get_dir()
        self.e_len = self.get_edge_len()
        self.move_limit = self.__cal_limits()
        self.ratio = self.__cal_ratio(self.center)

    # properties
    @property
    def center(self):
        return (self.new["v"][0].xy + self.new["v"][1].xy) / 2

    @property
    def dir(self):
        return self.bind_edge.get_dir()

    @property
    def vertices(self):
        return self.new["v"]

    @property
    def edges(self):
        return self.new["e"]

    @property
    def faces(self):
        return self.new["f"]

    # history
    def save_history(self):
        self.__history["bind_edge"] = self.bind_edge.eid
        self.__history["center"] = self.center.copy()

    def load_history(self):
        def find_edge(eid):
            for e in self.floor_plan.edges:
                if e.eid == eid:
                    return e
            return None

        if self.bind_edge is self.__history["bind_edge"]:
            print("=== load history (same) ===")
            # on the same edge
            self.set_door_center(self.__history["center"])
        else:   # on the different edge
            print("=== load history (diff) ===")
            self.deactivate()
            # self.bind_edge = self.__history["bind_edge"]
            self.bind_edge = find_edge(self.__history["bind_edge"])
            self.activate(self.__history["center"])
            print(f"bind_edge: {self.bind_edge.eid} | ratio: {self.ratio}")


    # floor plan
    def sync_floor_plan(self):
        if self.is_active:
            self.floor_plan.append(self.new["v"], self.new["e"], self.new["f"])
        else:
            self.floor_plan.remove(self.new["v"], self.new["e"], self.new["f"])


if __name__ == "__main__":
    import numpy as np

    from f_primitives import FPoint, FEdge, FFace
    from u_data_loader import Loader
    from f_layout import FLayout
    from u_geometry import add_vertex

    # settings
    case_id = "0a"

    np.random.seed(0)
    ld = Loader(".")
    ld.load_w_walls_case(case_id)
    ld.optimize()

    nm = FLayout()
    nm.set_default_types(FPoint, FEdge, FFace)
    nm.create_mesh(ld.vertices, ld.edges, 0)
    # nm.reconnect_closed_edges()
    # nm.create_rooms()

    inner_walls = nm.inner_fixed_edges

    e0 = nm.get_by_eid(0)
    agent = FDoor(e0, nm)
    agent.activate(np.array([0.5, 0.8]))

    # I am not sure the mesh structure is still correct after loading the history or after deactivating the door
    # TODO: I need to visualize the mesh here for debugging
