# ECS (Entity-Component-System) for the door system.


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

    def get_door_component(self, entity_id):
        """Return the DoorComponent for a given entity ID."""
        return self.doors.get(entity_id, None)

    def add_door_component(self, door_comp):
        """Attach a DoorComponent to a given entity ID."""
        entity_id = self.create_entity()
        self.doors[entity_id] = door_comp

    def remove_door_component(self, entity_id):
        """Remove the DoorComponent for a given entity."""
        if entity_id in self.doors:
            del self.doors[entity_id]
