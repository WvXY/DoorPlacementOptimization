import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches


class Visualizer:
    def __init__(self):
        self.ax, self.fig = plt.subplots()

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

    def draw_tripath(self, tripath):
        if tripath is None:
            return

        for f in tripath:
            if f:
                self.fig.fill(
                    [n.x for n in f.nodes],
                    [n.y for n in f.nodes],
                    "y",
                    alpha=0.3,
                )

    def draw_mesh(self, mesh: "Mesh", title=None, show=True, draw_text=False):
        for f in mesh.faces:
            if f is None:
                continue

            tri = [n.xy for n in f.nodes]
            self.fig.add_patch(patches.Polygon(tri, color="k", alpha=0.1))

        for fe in mesh.fixed_edges:
            ori, to = fe.origin, fe.to
            self.fig.plot([ori.x, to.x], [ori.y, to.y], "k", lw=2)

        for v in mesh.vertices:
            if v is None:
                continue
            plt.scatter(v.x, v.y, c="k", s=10)
            if draw_text:
                plt.text(
                    v.x,
                    v.y,
                    str(v.guid),
                    fontsize=12,
                    horizontalalignment="right",
                    verticalalignment="top",
                )

        if title:
            self.fig.set_title(title)
        plt.axis("equal")

        if show:
            plt.show()

    def show(self, title=None):
        self.fig.set_title(title)
        plt.show()
