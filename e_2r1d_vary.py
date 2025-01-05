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
    ld.optimize()

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

        # print(
        #     f"edge: {door.bind_edge.eid} | df: {df:.3f}  | center: {door.center}"
        #     f"| score: {new_score:.3f} | alpha: {alpha:.3f}"
        # )
        samples.append([door.center, new_score])
        T *= 0.99  # Annealing

    door.load_manually(best_e, best_x)
    return best_x, best_score, samples


if __name__ == "__main__":
    # Initialize
    case_id = 4
    n_sp = 100
    iters = 200
    T = 0.1

    fp, vis = init(case_id)

    # vis.draw_mesh(fp, show=True, draw_text="vef", axis_show=False, axis_equal=True)

    e0 = fp.get_by_eid(0)
    door = ODoor(fp=fp)
    # door.set_rooms(*())
    # door.activate(np.array([0.6, 0.7]))

    r0 = fp.get_by_rid(0)
    r1 = fp.get_by_rid(1)
    r2 = fp.get_by_rid(2)

    door.auto_activate([r1, r0])
    print(door.get_room_rids())

    sp = make_sample_points(n_sp)

    best_x, best_s, samples = metropolis_hasting(fp, door, T=T, iters=iters)

    # # Visualize results
    vis.draw_mesh(fp, show=False, draw_text="f")
    for room in fp.rooms:
        print(f"Room {room.rid}: {[f.fid for f in room.faces]}")

    vis.draw_floor_plan(fp, door, show=False, draw_connection=True)

    # for v, s in samples:
    #     plt.scatter(v[0], v[1], c=s, s=30, alpha=1, marker="s")

    # plt.colorbar()

    # agent = Agent(fp)
    # agent.init()
    for i in range(0, 50, 2):
        start = sp[i]
        end = sp[i + 1]
        tripath = fp.find_tripath(start, end)
        path = fp.simplify(tripath, start, end)
        if path:
            c = np.random.rand(3)
            vis.draw_point(start, c=c, s=50)
            vis.draw_point(end, c=c, s=50)
            vis.draw_linepath(path, c=c, lw=1, a=1)
        # agent.next()

    vis.show(f"Result {case_id} | Best Center: {best_x}")

    # #
    # # # # Plot histogram
    # fig, ax1 = plt.subplots()
    # ax1.hist(samples, bins=36, density=True, alpha=0.6, label="Samples")
    # ax1.set_ylabel("Number of Samples")
    #
    # ndiv = 100
    # door.deactivate()
    # door.activate(np.array([0.5, 0.05]))
    #
    # ax2 = ax1.twinx()
    # gt_scores = []
    # xx = []
    # for i in tqdm(range(ndiv)):
    #     door.step(-1/ndiv)
    #     gt_scores.append(f(fp, sp))
    #     xx.append(door.center[1])
    #
    # ax2.plot(xx, gt_scores, label="Ground Truth", color="red")
    # ax2.set_ylabel("Traffic Flow Cost")
    # ax2.tick_params(axis="y", labelcolor="red")
    #
    # ax1.set_title("Metropolis-Hastings Sampling")
    # ax1.set_xlabel("y-coordinate")
    #
    # plt.legend()
    # plt.show()
