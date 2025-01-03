import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from f_layout import FLayout
from f_primitives import FPoint, FEdge, FFace
from g_primitives import Point
from o_door import ODoor
from o_loss_func import loss_func
from u_data_loader import Loader
from u_visualization import Visualizer


def init(case_id, np_seed=0):
    # Settings
    np.random.seed(np_seed)

    # Load data
    ld = Loader(".")
    ld.load_closed_rooms_case(case_id)
    ld.optimize()

    fp = FLayout()
    fp.set_default_types(FPoint, FEdge, FFace)
    fp.create_mesh(ld.vertices, ld.edges, 0)

    # Visualization
    vis = Visualizer()
    # vis.draw_mesh(fp, show=False, draw_text="e")

    return fp, vis


def make_sample_points(n=2000):
    return [Point(np.random.rand(2)) for _ in range(n)]


def f(fp, sp, batch_size=50):
    score = 0
    valid_paths = 0

    for i in range(0, len(sp), 2):
        start = sp[i]
        end = sp[i + 1]
        # start = agent.prev_pos
        # end = agent.curr_pos
        tripath = fp.find_tripath(start, end)
        path = fp.simplify(tripath, start, end)
        if path:
            valid_paths += 1
            score += loss_func(path)
        # agent.next()
    return score / valid_paths if valid_paths > 0 else float("inf")


def f_test(fp, sp):
    score = 0
    valid_paths = 0

    start = sp[0]
    end = sp[2]
    tripath = fp.find_tripath(start, end)
    path = fp.simplify(tripath, start, end)
    score += loss_func(path)
    return score


if __name__ == "__main__":
    # Initialize
    case_id = 4
    n_sp = 200
    fp, vis = init(case_id)

    sp = make_sample_points(n_sp)
    # for p in sp:
    #     plt.scatter(p.x, p.y, c="b", s=5)
    # plt.show()

    # plt.scatter(sp[0].x, sp[0].y, c="r", s=12)
    # plt.scatter(sp[2].x, sp[2].y, c="r", s=12)
    # vis.draw_mesh(fp, show=False, draw_text="e")

    e0 = fp.get_by_eid(0)
    door = ODoor(e0, fp)
    door.activate(np.array([0.1, 0.2]))

    # calculate the loss function
    xys = []
    scores = []
    best_score = 1000000
    best_x = door.center.copy()

    for iteration in tqdm(range(100)):
        door.step(-0.05)
        score = f(fp, sp)
        xys.append(door.center)
        scores.append(score)

        if score < best_score:
            best_score = score
            best_x = door.center.copy()
            best_e = door.bind_edge

    print(
        f"Best Score: {best_score:.3f} | Best X: {best_x} | Best E: {best_e.eid}"
    )
    # door.load_manually(best_e, best_x)

    # Visualization
    xs = [v[0] for v in xys]
    ys = [v[1] for v in xys]
    colormap = "rainbow"
    plt.scatter(
        xs,
        ys,
        c=scores,
        s=50,
        alpha=1,
        marker="o",
        cmap=mpl.colormaps[colormap],
    )
    plt.colorbar()

    for i in range(0, 30, 2):
        start = sp[i]
        end = sp[i + 1]
        tripath = fp.find_tripath(start, end)
        path = fp.simplify(tripath, start, end)
        if path:
            c = np.random.rand(3)
            vis.draw_point(start, c=c, s=12)
            vis.draw_point(end, c=c, s=12)
            vis.draw_linepath(path, c=c, lw=2, a=1)
        else:
            c = "r"
            vis.draw_point(start, c=c, s=8)
            vis.draw_point(end, c=c, s=8)
            vis.draw_linepath([start, end],"--", c=c, lw=2, a=1)

    # # ======manual test for one path=======
    # # start = Point(np.array([0.2, 0.9]))
    # # end = Point(np.array([0.5, 0.05]))
    # start = sp[0]
    # end = sp[2]
    # tripath = fp.find_tripath(start, end)
    # path = fp.simplify(tripath, start, end)
    # if path:
    #     c = "g"#np.random.rand(3)
    #     vis.draw_point(start, c=c, s=5)
    #     vis.draw_point(end, c=c, s=5)
    #     vis.draw_linepath(path, c=c, lw=2, a=1)

    vis.draw_mesh(fp, show=False, draw_text="")

    # vis.show(f"Result {case_id} | Lowest Cost at: {best_x}")
    #
    # # # Plot samples
    # plt.hist(samples, bins=100, density=True, alpha=0.5, label="Samples")
    # yy = np.linspace(0.4, 1, 100)
    # # for y in yy:
    # #     agent.set_pos(np.array([0.46875, y]))
    # #     plt.plot(y, f(), 'ro')
    # plt.legend()
    # plt.show()
