import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches


class Visualizer:
    def __init__(self, dpi=120):
        self.ax, self.fig = plt.subplots(dpi=dpi)

    def get_fig(self):
        return self.fig

    def get_axis(self):
        return self.ax

    def draw_point(self, point, c="r", s=60, m="o"):
        if (
            isinstance(point, np.ndarray)
            or isinstance(point, list)
            or isinstance(point, tuple)
        ):
            self.fig.scatter(point[0], point[1], color=c, s=s, marker=m)
        else:
            self.fig.scatter(point.x, point.y, color=c, s=s, marker=m)

    def draw_linepath(self, path, linetype="-", c="k", s=60, a=1, lw=2):
        if path is None:
            return

        if isinstance(path[0], np.ndarray):
            self.fig.plot(
                [n[0] for n in path],
                [n[1] for n in path],
                linetype,
                c=c,
                lw=lw,
                alpha=a,
            )
        else:
            self.fig.plot(
                [n.x for n in path],
                [n.y for n in path],
                linetype,
                c=c,
                lw=lw,
                alpha=a,
            )

    def draw_half_edges(self, half_edges, c="c", lw=0.01):
        for e in half_edges:
            x, y = e.ori.x, e.ori.y
            dx, dy = e.to.x - e.ori.x, e.to.y - e.ori.y
            self.fig.arrow(
                x, y, dx, dy, width=lw, color=c, length_includes_head=True
            )

    def draw_tri_half_edges(self, triangle, c="c", lw=0.01, scale=0.8):
        # Calculate the centroid of the triangle
        verts = triangle.verts
        centroid_x = sum(v.x for v in verts) / 3
        centroid_y = sum(v.y for v in verts) / 3

        # Shrink vertices toward the centroid
        shrunk_verts = []
        for v in verts:
            shrunk_x = centroid_x + (v.x - centroid_x) * scale
            shrunk_y = centroid_y + (v.y - centroid_y) * scale
            shrunk_verts.append((shrunk_x, shrunk_y))

        # Draw the edges of the shrunk triangle
        for i in range(3):
            x, y = shrunk_verts[i]
            dx, dy = (
                shrunk_verts[(i + 1) % 3][0] - x,
                shrunk_verts[(i + 1) % 3][1] - y,
            )
            self.fig.arrow(
                x, y, dx, dy, width=lw, color=c, length_includes_head=True
            )

    def draw_tripath(self, tripath):
        if tripath is None:
            return

        for f in tripath:
            if f:
                self.fig.fill(
                    [n.x for n in f.verts],
                    [n.y for n in f.verts],
                    "y",
                    alpha=0.3,
                )

    def draw_mesh(
        self,
        mesh,
        show=True,
        clear=False,
        draw_text="",
        fig_title=None,
        axis_show=True,
        axis_equal=True,
    ):
        if clear:
            self.ax, self.fig = plt.subplots()

        for f in mesh.faces:
            if f is None:
                continue

            tri = [n.xy for n in f.verts]
            self.fig.add_patch(patches.Polygon(tri, color="k", alpha=0.2))

        for fe in mesh.get_block_edges():
            ori, to = fe.ori, fe.to
            self.fig.plot([ori.x, to.x], [ori.y, to.y], "k", lw=2)

        for v in mesh.vertices:
            if v is None:
                continue
            plt.scatter(v.x, v.y, c="k", s=16)

        if draw_text:
            self.draw_infos(
                mesh, f="f" in draw_text, e="e" in draw_text, v="v" in draw_text
            )

        if fig_title:
            self.fig.set_title(fig_title)

        if not axis_show:
            plt.axis("off")

        if axis_equal:
            plt.axis("equal")

        if show:
            plt.show()

    def draw_infos(self, mesh, f=False, e=False, v=False):
        if f:
            for f in mesh.faces:
                if f is None:
                    continue
                self.fig.text(
                    f.x,
                    f.y,
                    str(f.fid),
                    fontsize=12,
                    c="k",
                )
                # self.fig.scatter(f.x, f.y, c="k", s=16, marker="o")

        if e:
            mesh.reset_all_visited(mesh.edges)
            for f in mesh.faces:
                if f is None:
                    continue
                for e in f.half_edges:
                    if e is None or e.is_visited:
                        continue
                    self.fig.text(
                        e.get_mid()[0],
                        e.get_mid()[1],
                        str(f"{e.eid}/{e.twin.eid}" if e.twin else e.eid),
                        fontsize=10,
                        horizontalalignment="center",
                        verticalalignment="center",
                        c="r" if e.is_blocked else "g",
                    )
                    e.is_visited = True
                    if e.twin:
                        e.twin.is_visited = True

        if v:
            for v in mesh.vertices:
                if v is None:
                    continue
                self.fig.text(
                    v.x,
                    v.y,
                    str(v.vid),
                    fontsize=12,
                    horizontalalignment="right",
                    verticalalignment="top",
                    c="m",
                )

    # for floor plan layout
    def draw_room(self, room, c="k", lw=0.01):
        for f in room.faces:
            if f is None:
                continue
            vxs = [n.x for n in f.verts]
            vys = [n.y for n in f.verts]
            self.fig.fill(
                vxs,
                vys,
                c,
                alpha=0.2,
            )
            self.fig.scatter(vxs, vys, c="k", s=16, marker="o")

        center = room.get_center()
        self.fig.text(center[0], center[1], str(room.rid), fontsize=16, c="b")
        walls = room.get_wall_edges()
        for e in walls:
            self.fig.plot(
                [e.ori.x, e.to.x],
                [e.ori.y, e.to.y],
                c="k",
                lw=1.6,
            )

    def draw_door(self, door, c="k", lw=0.01):
        a = door.new["v"][0].xy
        b = door.new["v"][1].xy
        self.fig.plot([a[0], b[0]], [a[1], b[1]], c="c", lw=2)
        self.fig.scatter(a[0], a[1], c="c", s=40, marker="h")
        self.fig.scatter(b[0], b[1], c="c", s=40, marker="h")

    def draw_connection(self, fp, c="g", lw=2):
        if fp.adj_m is None:
            fp.set_room_connections()

        for i in range(len(fp.adj_m)):
            r0 = fp.get_by_rid(i)
            c0 = r0.get_center()
            for j in range(i + 1, len(fp.adj_m)):
                if fp.adj_m[i, j] == 1:
                    r1 = fp.get_by_rid(j)
                    c1 = r1.get_center()
                    self.fig.plot(
                        [c0[0], c1[0]],
                        [c0[1], c1[1]],
                        "-.",
                        c=c,
                        lw=lw,
                    )
                    self.fig.scatter(*c0, c="b", s=40, marker="s")
                    self.fig.scatter(*c1, c="b", s=40, marker="s")

    def draw_floor_plan(
        self, fp, doors=None, draw_connection=False, show=False
    ):
        self.ax, self.fig = plt.subplots()

        for room in fp.rooms:
            self.draw_room(room)

        if draw_connection:
            self.draw_connection(fp)

        if doors:
            for door in doors:
                self.draw_door(door)

        if show:
            plt.axis("equal")
            plt.show()

    def show(self, title=None, axis="equal", axis_off=False):
        self.fig.set_title(title)
        plt.axis(axis)
        if axis_off:
            plt.axis("off")
        plt.show()

    def __del__(self):
        plt.show()
