import numpy as np

from o_door import DoorComponent
from u_geometry import split_half_edge, closet_position_on_edge


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
        """
        The system holds a reference to the ECS 'world'
        so it can access all DoorComponents.
        """
        self.ecs = ecs
        self.fp = fp

    def update_all(self):
        """
        Called each frame/tick.
        Iterates all door components in the ECS and applies any needed logic.
        """
        for entity_id, door_comp in list(self.ecs.doors.items()):
            if door_comp.is_active and door_comp.need_optimization:
                self.step(door_comp)

    def activate(self, door_comp, center=None, need_correction=True):
        """Originally 'activate' was part of the ODoor class. Now it's a system method."""
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
        if center is None:
            center = door_comp.bind_edge.get_center()

        if need_correction:
            center = self._correct_location(door_comp, center)

        self._calc_cache(door_comp)

        cut_p0, cut_p1 = self._cut_at_position(door_comp, center)
        # Replace with your real `split_half_edge` logic
        (new_v0, new_e0, new_f0) = split_half_edge(door_comp.bind_edge, cut_p0)
        (new_v1, new_e1, new_f1) = split_half_edge(door_comp.bind_edge, cut_p1)
        door_comp.new["v"].extend(new_v0 + new_v1)
        door_comp.new["e"].extend(new_e0 + new_e1)
        door_comp.new["f"].extend(new_f0 + new_f1)

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

        # Example of removing geometry and resetting state
        # ...
        door_comp.is_active = False
        self.sync_floor_plan(door_comp)

        # Clear the new geometry references
        door_comp.new = {"v": [], "e": [], "f": []}

    def step(self, door_comp, delta=0.0):
        """Your per-frame logic for moving or optimizing the door."""
        if not door_comp.is_active:
            return

        # Possibly do random motion or geometry updates
        if delta == 0.0:
            delta = np.random.normal(0, 0.05)

        ratio = door_comp.ratio + delta / door_comp.e_len
        if not self._within_limit(door_comp, ratio):
            # Move to next edge or revert
            self._to_next_edge(door_comp, ratio)
        else:
            # Just shift the door geometry along the current edge
            self._move_door(door_comp, delta, ratio)

    # ----------------------------------------------------
    # Helper methods: geometry, ratio, limiting, etc.
    # ----------------------------------------------------
    def _correct_location(self, door_comp, loc):
        return closet_position_on_edge(door_comp.bind_edge, loc)

    def _calc_cache(self, door_comp):
        door_comp.e_len = door_comp.bind_edge.get_length()
        self._calc_ratio(door_comp, door_comp._history["center"])
        self._calc_limits(door_comp)

    def _calc_ratio(self, door_comp, pos):
        edge = door_comp.bind_edge
        frac = np.linalg.norm(edge.ori.xy - pos) / edge.get_length()
        # Dot to check direction
        if (pos - edge.ori.xy) @ edge.get_dir() > 0:
            door_comp.ratio = frac
        else:
            door_comp.ratio = -frac

    def _calc_limits(self, door_comp):
        d_len = door_comp.d_len
        e_len = door_comp.e_len
        door_comp.move_limit = [
            d_len / 2.0 / e_len,
            1 - d_len / 2.0 / e_len,
        ]  # lower  # upper

    def _cut_at_position(self, door_comp, center):
        offset = door_comp.bind_edge.get_dir() * door_comp.d_len / 2 * 0.95
        cut_p0 = center + offset
        cut_p1 = center - offset
        return (cut_p0, cut_p1)

    def _within_limit(self, door_comp, ratio):
        return door_comp.move_limit[0] <= ratio <= door_comp.move_limit[1]

    def _move_door(self, door_comp, delta, ratio):
        door_comp.ratio = ratio
        direction = door_comp.bind_edge.get_dir() * delta
        for v in door_comp.new["v"]:
            v.xy += direction

    def _to_next_edge(self, door_comp, ratio):
        """
        'Jump' to next edge if ratio is out of bounds.
        Deactivate on current edge, find new edge, reactivate there, etc.
        """
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
        """
        Logic for picking a new edge from the shared edges.
        Return (success, edge, new_center).
        """
        # This is heavily dependent on your mesh connectivity.
        # For demonstration, pretend we found a valid next edge:
        # ...
        return (False, None, None)  # e.g. fail by default

    def sync_floor_plan(self, door_comp):
        """Add or remove geometry from the floor plan."""
        if door_comp.is_active:
            self.fp.append(
                door_comp.new["v"], door_comp.new["e"], door_comp.new["f"]
            )
        else:
            self.fp.remove(
                door_comp.new["v"], door_comp.new["e"], door_comp.new["f"]
            )


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
