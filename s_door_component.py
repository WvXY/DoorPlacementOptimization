from typing import List


class DoorComponent:

    def __init__(self, room0, room1, door_length=0.07):
        self.bind_edge = None  # e.g., FEdge
        self.bind_rooms: List = [room0, room1]  # e.g., [FRoom, FRoom]

        # Door geometry properties
        self.d_len = door_length
        self.e_len = None
        self.ratio = None  # equivalent to "current position" of the door
        self.move_limit = None

        # Cached new geometry (vertices, edges, faces) after splitting
        self.verts = []
        self.edges = []
        self.faces = []
        self.shared_edges = []

        # Status / flags
        self.is_active = False
        self.is_synced = True
        self.need_optimization = True

        # For storing some last-known states (history)
        self.history = {
            "bind_edge": None,
            "ratio": None,
        }

    def __repr__(self):
        return (
            f"DoorComponent("
            f"rooms={[r.rid for r in self.bind_rooms]}, "
            f"edge={self.bind_edge.eid}, "
            f"ratio={self.ratio:.5f}, "
            f"is_active={self.is_active})"
        )
