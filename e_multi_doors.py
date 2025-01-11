import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from f_layout import FLayout
from g_primitives import Point
from ecs import ECS, DoorSystem
from o_door import DoorComponent
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


def create_door_system(fp):
    r0 = fp.get_by_rid(0)
    r1 = fp.get_by_rid(1)
    r2 = fp.get_by_rid(2)
    r3 = fp.get_by_rid(3)
    r4 = fp.get_by_rid(4)

    ecs = ECS()
    door_system = DoorSystem(ecs, fp)
    door_cmp03 = DoorComponent(r0, r3)
    door_cmp13 = DoorComponent(r1, r3)
    ecs.add_door_component(door_cmp03)
    ecs.add_door_component(door_cmp13)

    door_system.activate_all()

    return door_system


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


def metropolis_hasting(fp, door_system, T=0.01, iters=200, vis=None):
    # Metropolis-Hastings settings
    old_score = f(fp, sp)
    samples = []
    losses = []
    best_score = old_score
    best_e, best_r = door_system.get_states()

    for iteration in tqdm(range(iters)):

        door_system.propose()

        new_score = f(fp, sp)
        df = new_score - old_score

        # Accept or reject proposal
        alpha = np.exp(-df / T)
        if df < 0 or np.random.rand() < alpha:
            old_score = new_score
            if new_score < best_score:
                best_e, best_r = door_system.get_states()
                best_score = new_score
        else:
            door_system.reject()

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

    door_system.load_manually(best_e, best_r)

    return best_e, best_r, losses


if __name__ == "__main__":
    # Initialize
    case_id = 1
    n_sp = 100
    iters = 20
    T = 0.01

    fp, vis = init(case_id)

    vis.draw_mesh(
        fp, show=True, draw_text="ve", axis_show=False, axis_equal=True
    )
    vis.draw_floor_plan(fp, show=True, draw_connection=True)

    door_system = create_door_system(fp)

    # vis.draw_mesh(fp, show=True, draw_text="e", clear=True)

    sp = make_sample_points(n_sp)
    #
    best_e, best_r, losses = metropolis_hasting(
        fp, door_system, T=T, iters=iters, vis=vis
    )
    #
    # # # Visualize results
    # vis.draw_mesh(fp, show=False, draw_text="f")
    # for room in fp.rooms:
    #     print(f"Room {room.rid}: {[f.fid for f in room.faces]}")
    #
    # vis.draw_mesh(fp, show=False, draw_text="", clear=True)

    # vis.draw_mesh(
    #     fp, show=True, draw_text="", clear=True, fig_title="Final Result"
    # )

    # for v, s in samples:
    #     plt.scatter(v[0], v[1], c=s, s=30, alpha=1, marker="s")

    # plt.colorbar()

    # vis.draw_floor_plan(fp, show=False, draw_connection=True)
    vis.draw_mesh(fp, show=False, draw_text="vef", clear=True)

    start = Point(np.array([0.4, 0.6]))
    end = Point(np.array([0.3, 0.35]))
    tripath = fp.find_tripath(start, end)
    path = fp.simplify(tripath, start, end)
    c = np.random.rand(3)
    vis.draw_point(start, c=c, s=50)
    vis.draw_point(end, c=c, s=50)
    vis.draw_linepath(path, c=c, lw=1, a=1)

    # for i in range(0, 50, 2):
    #     start = sp[i]
    #     end = sp[i + 1]
    #     tripath = fp.find_tripath(start, end)
    #     path = fp.simplify(tripath, start, end)
    #     if path:
    #         c = np.random.rand(3)
    #         vis.draw_point(start, c=c, s=50)
    #         vis.draw_point(end, c=c, s=50)
    #         vis.draw_linepath(path, c=c, lw=1, a=1)

    vis.show(f"Result {case_id}")

    plt.plot(losses)
    plt.show()
