# ECS (Entity-Component-System) for the door system.


class ECS:
    def __init__(self):
        self.next_entity_id = 0
        # For demonstration, we'll just store DoorComponents
        self.doors = {}  # entity_id -> DoorComponent
        self.connections = {}  # entity_id -> entity_id and vice versa

    def create_entity(self):
        """Generate and return a unique entity ID."""
        entity_id = self.next_entity_id
        self.next_entity_id += 1
        return entity_id

    def add_door_component(self, door_comp):
        """Attach a DoorComponent to a given entity ID."""
        entity_id = self.create_entity()
        self.connections[door_comp] = []
        for k, v in self.doors.items():
            if set(v.rooms) & set(door_comp.rooms):
                # use entity_id instead of door_comp
                self.connections[door_comp].append(v)
                self.connections[v].append(door_comp)
        self.doors[entity_id] = door_comp

    def get_door_component(self, entity_id):
        """Return the DoorComponent for a given entity ID."""
        return self.doors.get(entity_id, None)

    def get_adjacent_doors(
        self, door_comp
    ):  # use entity_id instead of door_comp
        """Return the DoorComponents connected to a given entity."""
        return self.connections.get(door_comp, [])

    def remove_door_component(self, entity_id):
        """Remove the DoorComponent for a given entity."""
        if entity_id in self.doors:
            del self.doors[entity_id]
