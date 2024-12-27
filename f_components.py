from g_primitives import _GeoBase


# class Door(_GeoBase):
#     door_list = []
#
#     def __init__(self, number, status):
#         super().__init__()
#         self.number = number
#         self.status = status
#
#         Door.door_list.append(self)
#
#     def open(self):
#         self.status = "open"
#
#     def close(self):
#         self.status = "closed"
#
#     def create(self):
#         self.status = "created"
#
#     def __str__(self):
#         return f"Door {self.number} is {self.status}"


class Room(_GeoBase):
    __id = 0

    def __init__(self):
        super().__init__()
        self.id = Room.__id
        Room.__id += 1

        self.faces = []
        self.type = 0
        self.inner_walls = []
        self.outer_walls = []
