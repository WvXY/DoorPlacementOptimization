import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches


class Visualizer:
    def __init__(self):
        self.ax, self.fig = plt.subplots()

    def get_fig(self):
        return self.fig

    def get_axis(self):
        return self.ax

    def draw_point(self, point, c="r", s=60, m="o"):
        self.fig.scatter(point.x, point.y, c=c, s=s, marker=m)

    def draw_linepath(self, path, c, s=60, a=1, lw=2):
        if path is None:
            return

        if isinstance(path[0], np.ndarray):
            self.fig.plot(
                [n[0] for n in path], [n[1] for n in path], c=c, lw=lw, alpha=a
            )
        else:
            self.fig.plot(
                [n.x for n in path], [n.y for n in path], c=c, lw=lw, alpha=a
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

    def draw_mesh(self, mesh, title=None, show=True, draw_text=""):
        for f in mesh.faces:
            if f is None:
                continue

            tri = [n.xy for n in f.verts]
            self.fig.add_patch(patches.Polygon(tri, color="k", alpha=0.1))

        for fe in mesh.get_block_edges():
            ori, to = fe.ori, fe.to
            self.fig.plot([ori.x, to.x], [ori.y, to.y], "k", lw=2)

        for v in mesh.vertices:
            if v is None:
                continue
            plt.scatter(v.x, v.y, c="k", s=10)

        if draw_text:
            self.draw_infos(
                mesh, f="f" in draw_text, e="e" in draw_text, v="v" in draw_text
            )

        if title:
            self.fig.set_title(title)
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
                    horizontalalignment="right",
                    verticalalignment="top",
                    c="k",
                )

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

    def show(self, title=None, axis="equal", axis_off=False):
        self.fig.set_title(title)
        plt.axis(axis)
        if axis_off:
            plt.axis("off")
        plt.show()
