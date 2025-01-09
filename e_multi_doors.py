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
    # ld.load_closed_rooms_case(case_id)
    ld.load_final_case(case_id)

    fp = FLayout()
    fp.create_mesh(ld.vertices, ld.edges, 0)
    fp.init_rooms()
    fp.set_room_connections()

    # Visualization
    vis = Visualizer()
    vis.draw_mesh(fp, show=False, draw_text="e")

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


def metropolis_hasting(fp, doors, T=0.01, iters=200, vis=None):
    # Metropolis-Hastings settings
    old_score = f(fp, sp)
    samples = []
    losses = []
    best_score = old_score
    best_e = []
    best_x = [door.center.copy() for door in doors]

    for iteration in tqdm(range(iters)):

        for door in doors:
            door.step()

        new_score = f(fp, sp)
        df = new_score - old_score

        # Accept or reject proposal
        alpha = np.exp(-df / T)
        if df < 0 or np.random.rand() < alpha:
            old_score = new_score
            if new_score < best_score:
                best_x = [door.center.copy() for door in doors]
                best_e = [door.bind_edge for door in doors]
                best_score = new_score
        else:
            for door in doors:
                door.load_history()

        if vis and iteration % 10 == 0:
            vis.draw_mesh(
                fp,
                show=True,
                draw_text="",
                clear=True,
                fig_title=f"Loss: {new_score:.3f} | Best Loss: {best_score:.3f}",
            )

        T *= 0.99  # Annealing
        losses.append(new_score)

    for door, e, x in zip(doors, best_e, best_x):
        door.load_manually(e, x)

    return best_x, best_score, losses


if __name__ == "__main__":
    # Initialize
    case_id = 1
    n_sp = 100
    iters = 100
    T = 0.001

    fp, vis = init(case_id)

    vis.draw_mesh(
        fp, show=True, draw_text="ve", axis_show=False, axis_equal=True
    )
    vis.draw_floor_plan(fp, show=True, draw_connection=True)

    # door.set_rooms(*())
    # door.activate(np.array([0.6, 0.7]))

    r0 = fp.get_by_rid(0)
    r1 = fp.get_by_rid(1)
    r2 = fp.get_by_rid(2)
    r3 = fp.get_by_rid(3)
    r4 = fp.get_by_rid(4)

    # e1 = fp.get_by_eid(1)
    # e9 = fp.get_by_eid(9)

    # door1.bind_edge = e9
    # door2.bind_edge = e1
    # door1.activate(np.array([0.8, 0.5]))
    # door2.activate(np.array([0.5, 0.4]))

    door13 = ODoor(fp)
    door03 = ODoor(fp)

    doors = [door13, door03]

    door13.auto_activate(r1, r3)
    door03.auto_activate(r0, r3)

    # vis.draw_mesh(fp, show=True, draw_text="e", clear=True)

    #
    for door in doors:
        print(f"Door {door.did}: {[e.eid for e in door.shared_edges]}")
    # vis.draw_mesh(fp, show=True, draw_text="vef")

    sp = make_sample_points(n_sp)
    #
    best_x, best_s, losses = metropolis_hasting(
        fp, doors, T=T, iters=iters, vis=vis
    )
    #
    # # # Visualize results
    # vis.draw_mesh(fp, show=False, draw_text="f")
    # for room in fp.rooms:
    #     print(f"Room {room.rid}: {[f.fid for f in room.faces]}")
    #
    vis.draw_mesh(fp, show=False, draw_text="", clear=True)
    for door in doors:
        vis.draw_door(door)

    # vis.draw_mesh(
    #     fp, show=True, draw_text="", clear=True, fig_title="Final Result"
    # )

    # for v, s in samples:
    #     plt.scatter(v[0], v[1], c=s, s=30, alpha=1, marker="s")

    # plt.colorbar()

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

    vis.show(f"Result {case_id} | Loss: {best_s:.3f}")

    plt.plot(losses)
    plt.show()
