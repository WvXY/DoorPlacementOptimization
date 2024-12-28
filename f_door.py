

class FDoor:
    def __init__(self):
        self.bind_edge = None
        self.floor_plan = None

        # Properties
        self.dir = None
        self.d_len = 0.1  # door length
        self.e_len = None # edge length
        self.ratio = 0.0

        self.move_limit = [0.0, 1.0]

        self.new = {
            "vertices": [],
            "edges": [],
            "faces": []
        }


    def activate(self, position):
        """Set a door at the given position."""
        pass

    def deactivate(self):
        """Deactivate the door."""
        pass

    def move(self, delta):
        """Move the door by delta along the edge."""
        pass

    def step(self):
        """Move the door by a random amount."""
        pass

    # History (trace back)
    def save_history(self):
        """Save the current state of the door."""
        pass

    def load_history(self):
        """Load the previous state of the door."""
        pass

    # Utility
    def __find_next_edge(self):
        """Find the next edge to bind to."""
        pass

    def __update_properties(self):
        """Update the properties of the door."""
        pass

    def __set_move_limits(self):
        """Set the move limits of the door."""
        pass

    def __calculate_ratio(self, position):
        """Calculate the ratio of the door."""
        pass

    @property
    def center(self):
        """Return the center of the door."""
        pass
