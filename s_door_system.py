import numpy as np

from u_geometry import split_half_edge, projection_on_edge, remove_vertex


class DoorSystem:
    def __init__(self, ecs, fp):
        self.ecs = ecs
        self.fp = fp

    # ----------------------------------------------------
    # Metropolis-Hastings
    # ----------------------------------------------------
    def activate_all(self):
        for door_comp in self.ecs.doors.values():
            door_comp.ratio = 0.5  # start from the middle
            self.activate(door_comp)

    def propose(self, sigma=0.1):
        for entity_id, door_comp in list(self.ecs.doors.items()):
            if door_comp.is_active:
                self.step(door_comp, sigma=sigma)
            else:
                print(f"WARNING: Door {entity_id} is not active")

    # debug method
    def move_all_by(self, delta):
        for door_comp in self.ecs.doors.values():
            self.step(door_comp, delta)

    def reject(self):
        for entity_id, door_comp in list(self.ecs.doors.items()):
            if door_comp.is_active:
                self._restore_last_state(door_comp)
            else:
                print(f"WARNING: Door {entity_id} is not active")

    def load_manually(self, edges, ratios):
        for door_comp, edge, ratio in zip(
            self.ecs.doors.values(), edges, ratios
        ):
            # print(f"Manually load door {door_comp} to edge {edge.eid}")
            self.manually_load_history(door_comp, edge, ratio)

    def get_states(self):
        edges = []
        ratios = []
        for door_comp in self.ecs.doors.values():
            edges.append(door_comp.bind_edge)
            ratios.append(door_comp.ratio)
        return edges, ratios

    # ----------------------------------------------------
    # Basic operations on single door components
    # ----------------------------------------------------
    def activate(self, door_comp):
        """
        Activate from bind_edge and ratio.
        Split the edge and add new geometry to the rooms.
        """
        assert door_comp.is_active is False, "Door is already active"
        assert door_comp.bind_rooms[0] is not None, "Room 0 is not set"
        assert door_comp.bind_rooms[1] is not None, "Room 1 is not set"

        def add_two_face_to_rooms(door_comp, faces):
            """A dirty way to add two new faces to the existing rooms"""
            for f_adj in faces[0].adjs:
                if f_adj is faces[1]:
                    continue

                # must be directly connected, not blocked
                e = faces[0].get_shared_edge(f_adj)
                if e.is_blocked:
                    continue

                if f_adj in door_comp.bind_rooms[0].faces:
                    door_comp.bind_rooms[0].add_face(faces[0])
                    door_comp.bind_rooms[1].add_face(faces[1])
                    break
            else:
                door_comp.bind_rooms[0].add_face(faces[1])
                door_comp.bind_rooms[1].add_face(faces[0])

        # Find shared edges between the two rooms
        self._calc_brooms_cache(door_comp)
        if door_comp.bind_edge is None:
            door_comp.bind_edge = door_comp.shared_edges[0]
        self._calc_bedge_cache(door_comp)

        door_comp.bind_edge.reset_all_visited()

        # cut the edge
        cut_p0, cut_p1 = self._cut_at(door_comp, door_comp.ratio)
        # Replace with your real `split_half_edge` logic
        (new_v0, new_e0, new_f0) = split_half_edge(door_comp.bind_edge, cut_p0)
        (new_v1, new_e1, new_f1) = split_half_edge(door_comp.bind_edge, cut_p1)
        door_comp.verts = new_v0 + new_v1
        door_comp.edges = new_e0 + new_e1
        door_comp.faces = new_f0 + new_f1

        # Update rooms accordingly
        add_two_face_to_rooms(door_comp, new_f0)
        add_two_face_to_rooms(door_comp, new_f1)

        # Mark door edges as unblocked, etc.
        new_e1[0].is_blocked = False
        new_e1[1].is_blocked = False

        door_comp.is_active = True
        self.sync_floor_plan(door_comp)

    def deactivate(self, door_comp):
        """Opposite of activate. Remove the newly created geometry."""
        if not door_comp.is_active:
            return

        reactivate_list = []
        adj_door_comps = self.ecs.get_adjacent_doors(door_comp).copy()
        # check
        while True:
            for v in door_comp.verts:
                n_edges = len(v.half_edges)
                if n_edges != 8:
                    # deactivate one door at a time and try again
                    d = adj_door_comps.pop()
                    self.deactivate(d)
                    reactivate_list.append(d)
                    print(f"temporarily deactivate {d}")
                    break
            else:   # can remove without broken geometry
                break

        # deactivate this door component
        del_v0, del_e0, del_f0 = remove_vertex(door_comp.verts.pop())
        del_v1, del_e1, del_f1 = remove_vertex(door_comp.verts.pop())
        door_comp.verts = del_v0 + del_v1
        door_comp.edges = del_e0 + del_e1
        door_comp.faces = del_f0 + del_f1

        door_comp.bind_rooms[0].remove_faces(door_comp.faces)
        door_comp.bind_rooms[1].remove_faces(door_comp.faces)

        door_comp.is_active = False
        # door_comp.bind_edge = None
        self.sync_floor_plan(door_comp)

        # reactivate deactivated doors
        while reactivate_list:
            self.activate(reactivate_list.pop())

    def step(self, door_comp, delta=0.0, sigma=0.1):
        if not door_comp.is_active:
            return

        # Possibly do random motion or geometry updates
        if delta == 0.0:
            delta = np.random.normal(delta, sigma)

        ratio = door_comp.ratio + delta / door_comp.e_len

        # save the current state
        self._store_current_state(door_comp)

        # move the door
        if not self._within_limit(door_comp, ratio):
            self._to_next_edge(door_comp, ratio)
        else:  # slide door along the edge
            # print("move by", delta)
            door_comp.ratio = ratio
            self._move_by(door_comp, delta)

    # ----------------------------------------------------
    # Helper methods: geometry, ratio, limiting, etc.
    # ----------------------------------------------------

    # location
    def _projection_to_edge(self, door_comp, loc):
        return projection_on_edge(door_comp.bind_edge, loc)

    def _pos_to_ratio(self, door_comp, pos):
        edge = door_comp.bind_edge
        frac = np.linalg.norm(edge.ori.xy - pos) / edge.get_length()
        # Dot to check direction
        if (pos - edge.ori.xy) @ edge.get_dir() > 0:
            return frac
        else:
            return -frac

    def _ratio_to_pos(self, door_comp, ratio):
        return (
            door_comp.bind_edge.ori.xy
            + door_comp.bind_edge.get_dir() * ratio * door_comp.e_len
        )

    def _cut_at(self, door_comp, ratio):
        offset = door_comp.bind_edge.get_dir() * door_comp.d_len / 2 * 0.95
        center = self._ratio_to_pos(door_comp, ratio)
        cut_p0 = center + offset
        cut_p1 = center - offset
        return (cut_p0, cut_p1)

    def _calc_bedge_cache(self, door_comp):
        assert door_comp.bind_edge is not None, "Edge is not set"
        assert door_comp.is_active is False, "Door is already active"
        door_comp.e_len = door_comp.bind_edge.get_length()
        self._calc_limits(door_comp)

    def _calc_brooms_cache(self, door_comp):
        door_comp.shared_edges = door_comp.bind_rooms[0].get_shared_edges(
            door_comp.bind_rooms[1]
        )

    # constraints
    def _calc_limits(self, door_comp):
        d_len = door_comp.d_len
        e_len = door_comp.e_len
        door_comp.move_limit = [
            d_len / 2.0 / e_len,
            1 - d_len / 2.0 / e_len,
        ]  # lower  # upper

    def _within_limit(self, door_comp, ratio):
        return door_comp.move_limit[0] <= ratio <= door_comp.move_limit[1]

    # movement
    def _move_to(self, door_comp, ratio):
        """Set the door to a specific ratio along the edge."""
        if not door_comp.is_active:
            return

        assert 0 <= ratio <= 1, "Ratio must be between 0 and 1"

        pos0, pos1 = self._cut_at(door_comp, ratio)
        door_comp.ratio = ratio
        door_comp.verts[0].xy = pos0
        door_comp.verts[1].xy = pos1

    def _move_by(self, door_comp, delta):
        # don't forget to update the door_comp.ratio
        # door_comp.ratio += delta / door_comp.e_len
        direction = door_comp.bind_edge.get_dir() * delta
        for v in door_comp.verts:
            v.xy += direction

    def _to_next_edge(self, door_comp, ratio):
        self.deactivate(door_comp)
        success = self._find_next_edge(door_comp, ratio)
        if not success:
            print("Door cannot move to the next edge")
            self.activate(door_comp)  # revert
        else:
            # move to new edge
            self.activate(door_comp)

    def _find_next_edge(self, door_comp, ratio):
        assert door_comp.is_active is False, "Door is already active"

        def search_next_shared_edge(vertex):
            for e in door_comp.shared_edges:
                if e is door_comp.bind_edge or e is door_comp.bind_edge.twin:
                    continue

                if e.ori is vertex or e.to is vertex:
                    return e

            for e in door_comp.shared_edges:
                if e.is_visited is False:
                    return e

            return None

        # search next edge
        if ratio >= door_comp.move_limit[1]:
            v = door_comp.bind_edge.to
            e = search_next_shared_edge(v)
            if e is None:
                door_comp.bind_edge = door_comp.bind_edge.twin
                # return False
            else:
                door_comp.bind_edge = e if e.ori is v else e.twin
            self._calc_bedge_cache(door_comp)
            door_comp.ratio = door_comp.move_limit[0]

        elif ratio <= door_comp.move_limit[0]:
            v = door_comp.bind_edge.ori
            e = search_next_shared_edge(v)
            if e is None:
                door_comp.bind_edge = door_comp.bind_edge.twin
            else:
                door_comp.bind_edge = e if e.to is v else e.twin
            self._calc_bedge_cache(door_comp)
            door_comp.ratio = door_comp.move_limit[1]

        door_comp.bind_edge.visit()
        return True

    # History
    def _store_current_state(self, door_comp):
        """Store the current state of the door component."""
        door_comp.history["ratio"] = door_comp.ratio
        door_comp.history["bind_edge"] = door_comp.bind_edge

    def _restore_last_state(self, door_comp):
        if door_comp.bind_edge == door_comp.history["bind_edge"]:
            # didn't move to a new edge, just reset the ratio
            # print("restore", door_comp.history["ratio"])
            self._move_to(door_comp, door_comp.history["ratio"])
        else:
            # reset the door to the last state: different edges
            # print("restore edge")
            self.deactivate(door_comp)
            door_comp.ratio = door_comp.history["ratio"]
            door_comp.bind_edge = door_comp.history["bind_edge"]
            self.activate(door_comp)

    def manually_load_history(self, door_comp, edge, ratio):
        door_comp.bind_edge = edge
        door_comp.ratio = ratio
        self.deactivate(door_comp)
        self.activate(door_comp)

    def sync_floor_plan(self, door_comp):
        """Add or remove geometry from the floor plan."""
        if door_comp.is_active:
            self.fp.append(door_comp.verts, door_comp.edges, door_comp.faces)
        else:
            self.fp.remove(door_comp.verts, door_comp.edges, door_comp.faces)
