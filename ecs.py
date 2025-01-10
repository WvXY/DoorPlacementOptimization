import numpy as np

from o_door import DoorComponent
from u_geometry import split_half_edge, closet_position_on_edge, remove_vertex


class ECS:
    def __init__(self):
        self.next_entity_id = 0
        # For demonstration, we'll just store DoorComponents
        self.doors = {}  # entity_id -> DoorComponent

    def create_entity(self):
        """Generate and return a unique entity ID."""
        entity_id = self.next_entity_id
        self.next_entity_id += 1
        return entity_id

    def add_door_component(self, door_comp):
        """Attach a DoorComponent to a given entity ID."""
        entity_id = self.create_entity()
        self.doors[entity_id] = door_comp

    def remove_door_component(self, entity_id):
        """Remove the DoorComponent for a given entity."""
        if entity_id in self.doors:
            del self.doors[entity_id]


class DoorSystem:
    def __init__(self, ecs, fp):
        self.ecs = ecs
        self.fp = fp

    def update_all(self):
        for entity_id, door_comp in list(self.ecs.doors.items()):
            if door_comp.is_active and door_comp.need_optimization:
                self.step(door_comp)

    def activate(self, door_comp):
        """
        Activate from bind_edge and ratio.
        Split the edge and add new geometry to the rooms.
        """
        assert door_comp.is_active is False, "Door is already active"
        assert door_comp.bind_edge is not None, "Door is not binded to any edge"

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

        door_comp.bind_edge.reset_all_visited()

        # Find or set the cut center
        self._calc_cache(door_comp)

        cut_p0, cut_p1 = self._cut_at_position(door_comp, door_comp.ratio)
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
        new_e0[0].is_blocked = False
        new_e0[1].is_blocked = False

        door_comp.is_active = True
        self.sync_floor_plan(door_comp)

    def deactivate(self, door_comp):
        """Opposite of activate. Remove the newly created geometry."""
        if not door_comp.is_active:
            return

        del_v0, del_e0, del_f0 = remove_vertex(self.verts.pop())
        del_v1, del_e1, del_f1 = remove_vertex(self.verts.pop())
        door_comp.verts = del_v0 + del_v1
        door_comp.edges = del_e0 + del_e1
        door_comp.faces = del_f0 + del_f1

        door_comp.bind_rooms[0].remove_faces(door_comp.faces)
        door_comp.bind_rooms[1].remove_faces(door_comp.faces)

        door_comp.is_active = False
        self.sync_floor_plan(door_comp)

    def slide_to(self, door_comp, ratio):
        """Set the door to a specific ratio along the edge."""
        if not door_comp.is_active:
            return

        assert 0 <= ratio <= 1, "Ratio must be between 0 and 1"
        pos0, pos1 = self._cut_at_position(door_comp, ratio)
        door_comp.ratio = ratio
        for v, pos in zip(door_comp.verts, [pos0, pos1]):
            v.xy = pos

    def step(self, door_comp, delta=0.0):
        if not door_comp.is_active:
            return

        # Possibly do random motion or geometry updates
        if delta == 0.0:
            delta = np.random.normal(0, 0.05)

        ratio = door_comp.ratio + delta / door_comp.e_len

        if not self._within_limit(door_comp, ratio):
            self._to_next_edge(door_comp, ratio)
        else:  # slide door along the edge
            self._move_door(door_comp, delta, ratio)

    # ----------------------------------------------------
    # Helper methods: geometry, ratio, limiting, etc.
    # ----------------------------------------------------
    def _correct_location(self, door_comp, loc):
        return closet_position_on_edge(door_comp.bind_edge, loc)

    def _calc_cache(self, door_comp):
        door_comp.e_len = door_comp.bind_edge.get_length()
        door_comp.ratio = 0.5 if door_comp.ratio is None else door_comp.ratio
        self._calc_limits(door_comp)

    def _pos_to_ratio(self, door_comp, pos):
        edge = door_comp.bind_edge
        frac = np.linalg.norm(edge.ori.xy - pos) / edge.get_length()
        # Dot to check direction
        if (pos - edge.ori.xy) @ edge.get_dir() > 0:
            door_comp.ratio = frac
        else:
            door_comp.ratio = -frac
        return door_comp.ratio

    def _calc_limits(self, door_comp):
        d_len = door_comp.d_len
        e_len = door_comp.e_len
        door_comp.move_limit = [
            d_len / 2.0 / e_len,
            1 - d_len / 2.0 / e_len,
        ]  # lower  # upper

    def _cut_at_position(self, door_comp, ratio):
        offset = door_comp.bind_edge.get_dir() * door_comp.d_len / 2 * 0.95
        center = self._ratio_to_pos(door_comp, ratio)
        cut_p0 = center + offset
        cut_p1 = center - offset
        return (cut_p0, cut_p1)

    def _ratio_to_pos(self, door_comp, ratio):
        return (
            door_comp.bind_edge.ori.xy
            + door_comp.bind_edge.get_dir() * ratio * door_comp.e_len
        )

    def _within_limit(self, door_comp, ratio):
        return door_comp.move_limit[0] <= ratio <= door_comp.move_limit[1]

    def _move_door(self, door_comp, delta, ratio):
        door_comp.ratio = ratio
        direction = door_comp.bind_edge.get_dir() * delta
        for v in door_comp.verts:
            v.xy += direction

    def _to_next_edge(self, door_comp, ratio):
        self.deactivate(door_comp)
        success, new_edge, center = self._find_next_edge(door_comp, ratio)
        if not success:
            # revert
            self.activate(door_comp, door_comp._history["center"])
        else:
            # move to new edge
            door_comp.bind_edge = new_edge
            self.activate(door_comp, center)

    def _find_next_edge(self, door_comp, ratio):

        return (False, None, None)  # e.g. fail by default

    # History
    def _store_current_state(self, door_comp):
        """Store the current state of the door component."""
        door_comp._history["ratio"] = door_comp.ratio
        door_comp._history["bine_edge"] = door_comp.bind_edge

    def _restore_last_state(self, door_comp):
        if door_comp.bind_edge == door_comp._history["bind_edge"]:
            self.set_to(door_comp, door_comp._history["ratio"])
        else:
            self.deactivate(door_comp)
            door_comp.ratio = door_comp._history["ratio"]
            door_comp.bind_edge = door_comp._history["bind_edge"]
            self.activate(door_comp)


    def manually_load_history(self, door_comp, edge, ratio):
        door_comp.bind_edge = edge
        door_comp.ratio = ratio
        self.activate(door_comp)

    def sync_floor_plan(self, door_comp):
        """Add or remove geometry from the floor plan."""
        if door_comp.is_active:
            self.fp.append(door_comp.verts, door_comp.edges, door_comp.faces)
        else:
            self.fp.remove(door_comp.verts, door_comp.edges, door_comp.faces)


if __name__ == "__main__":
    # 1. Create our ECS world
    ecs_world = ECS()

    # 2. Create a door system
    door_system = DoorSystem(ecs_world)

    # 3. Create an entity for the door and attach a DoorComponent
    door_entity = ecs_world.create_entity()
    door_comp = DoorComponent(
        room0=some_room0,
        room1=some_room1,
        floor_plan=some_floor_plan,
        edge=some_edge,
        door_length=0.07,
    )
    ecs_world.add_door_component(door_entity, door_comp)

    # 4. Activate the door using the system
    door_system.activate(door_comp, center=np.array([0.75, 0.75]))

    # 5. Run your game loop or simulation loop
    for frame in range(100):
        # Possibly other systems would update here as well
        door_system.update_all()

    # 6. Deactivate or remove the door
    door_system.deactivate(door_comp)
    ecs_world.remove_door_component(door_entity)
