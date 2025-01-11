import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from f_layout import FLayout
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

    fp = FLayout()
    # fp.set_default_types(FPoint, FEdge, FFace)
    fp.create_mesh(ld.vertices, ld.edges, 0)
    fp.init_rooms()
    fp.set_room_connections()

    # Visualization
    vis = Visualizer()
    # vis.draw_mesh(fp, show=False, draw_text="e")

    return fp, vis


def make_sample_points(n=300):
    return [Point(np.random.rand(2)) for _ in range(n)]


def f(fp, sp, batch_size=50):
    # indices = np.random.choice(range(0, 500, 2), batch_size, replace=False)

    loss = 0
    valid_paths = 0
    # agents = [Agent(fp) for _ in range(batch_size)]
    # agent.init()
    for i in range(0, len(sp) - 1):
        # for i in range(0, len(sp), 2):
        start = sp[i]
        end = sp[i + 1]
        # start = agent.prev_pos
        # end = agent.curr_pos
        tripath = fp.find_tripath(start, end)
        path = fp.simplify(tripath, start, end)
        if path:
            valid_paths += 1
            loss += loss_func(path)
        # agent.next()
    return loss / valid_paths if valid_paths > 0 else float("inf")


def metropolis_hasting(fp, door, T=0.01, iters=200):
    # Metropolis-Hastings settings
    old_score = f(fp, sp)
    samples = []
    best_score = old_score
    best_x = door.center.copy()

    for iteration in tqdm(range(iters)):

        door.step()

        new_score = f(fp, sp)
        df = new_score - old_score

        # Accept or reject proposal
        alpha = np.exp(-df / T)
        if df < 0 or np.random.rand() < alpha:
            old_score = new_score
            if new_score < best_score:
                best_x = door.center.copy()
                best_e = door.bind_edge
                best_score = new_score
        else:
            door.load_history()

        samples.append([door.center, new_score])
        T *= 0.99  # Annealing

    door.load_manually(best_e, best_x)

    return best_x, best_score, samples


if __name__ == "__main__":
    # Initialize
    case_id = 4
    n_sp = 200
    iters = 200
    T = 0.01

    fp, vis = init(case_id)

    # vis.draw_mesh(fp, show=True, draw_text="vef", axis_show=False, axis_equal=True)

    e0 = fp.get_by_eid(0)
    door = ODoor(fp=fp, edge=e0)
    door.activate()

    # vis.draw_mesh(fp, show=True, draw_text="vef")

    # Sample points
    sp = make_sample_points(n_sp)

    best_x, best_s, samples = metropolis_hasting(fp, door, T=T, iters=16)

    xx = [s[0][0] for s in samples]
    yy = [s[0][1] for s in samples]
    ss = [s[1] for s in samples]
    plt.scatter(xx, yy, c=ss, cmap="viridis", s=40)

    vis.draw_mesh(fp, show=True, draw_text="ve")
