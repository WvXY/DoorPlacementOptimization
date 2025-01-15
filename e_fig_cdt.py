from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt

# Basic Primitives
from f_layout import FLayout
from g_primitives import Point

# DOOR SYSTEM
from s_ecs import ECS
from s_door_system import DoorSystem
from s_door_component import DoorComponent

# Optimization
from o_loss_func import loss_func
from u_data_loader import Loader
from u_visualization import Visualizer


def init_fp_vis(case_id, np_seed=0):
    # Settings
    np.random.seed(np_seed)

    # Load data
    ld = Loader(".")
    # ld.load_closed_rooms_case(case_id)
    ld.load_w_walls_case(case_id)

    fp = FLayout()
    fp.create_mesh(ld.vertices, ld.edges, 0)
    fp.init_rooms()
    fp.set_room_connections()

    # Visualization
    vis = Visualizer()
    vis.draw_mesh(fp, show=False, draw_text="e")

    return fp, vis


# def create_door_system(fp):
#     r0 = fp.get_by_rid(0)
#     r1 = fp.get_by_rid(1)
#
#     ecs = ECS()
#     door_system = DoorSystem(ecs, fp)
#     door_cmp = DoorComponent(r0, r1)
#     ecs.add_door_component(door_cmp)
#
#     door_system.activate_all()
#
#     return door_system


def make_sample_points(n=300):
    return [Point(np.random.rand(2)) for _ in range(n)]


def f(fp, sp, batch_size=50):
    # indices = np.random.choice(range(0, 500, 2), batch_size, replace=False)

    loss = 0
    valid_paths = 0
    # agents = [Agent(fp) for _ in range(batch_size)]
    # agent.init()
    # for i in range(0, len(sp) - 1):
    for i in range(0, len(sp), 2):
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


# def metropolis_hasting(fp, door_system, T=0.1, iters=200):
#     # Metropolis-Hastings settings
#     old_score = f(fp, sp)
#     losses = []
#
#     best_score = old_score
#     best_x, best_r = door_system.get_states()
#     door_comp = door_system.ecs.get_door_component(0)
#
#     for i in tqdm(range(iters)):
#
#         door_system.propose(0.05)
#
#         new_score = f(fp, sp)
#         df = new_score - old_score
#
#         # Accept or reject proposal
#         alpha = np.exp(-df / T)
#         if np.random.rand() < alpha:
#             old_score = new_score
#             if new_score < best_score:
#                 best_x, best_r = door_system.get_states()
#                 best_score = new_score
#         else:
#             door_system.reject()
#
#         # print(f"History {door_comp.history}")
#
#     door_system.load_manually(best_x, best_r)
#
#     return best_score, losses


if __name__ == "__main__":
    # Initialize
    case_id = 6
    n_sp = 200

    fp, vis = init_fp_vis(case_id)

    vis.draw_mesh(fp, show=True, draw_text="", axis_show=False, axis_equal=True)

    # door_system = create_door_system(fp)

    sp = make_sample_points(n_sp)

    vis.draw_mesh(
        fp,
        show=False,
        draw_text="",
        axis_show=False,
        axis_equal=True,
        clear=True,
    )
    for i in range(0, len(sp), 10):
        start = sp[i]
        end = sp[i + 1]
        vis.draw_point(start, c="b", s=20)
        vis.draw_point(end, c="b", s=20)
    plt.savefig("./sample_points.svg")
    plt.show()

    # visualize
    vis.draw_mesh(
        fp,
        show=False,
        draw_text="",
        axis_show=False,
        axis_equal=True,
        clear=True,
    )
    # vis.draw_floor_plan(fp, show=True, draw_connection=True)
    #
    # xx = [x[0][0] for x in losses]
    # yy = [x[0][1] for x in losses]
    # ss = [x[1] for x in losses]

    for i in range(0, len(sp), 10):
        start = sp[i]
        end = sp[i + 1]
        tripath = fp.find_tripath(start, end)
        if tripath:
            path = fp.simplify(tripath, start, end)
            vis.draw_linepath(path, c="g", lw=3)
            vis.draw_point(start, c="g", s=20)
            vis.draw_point(end, c="g", s=20)
        else:
            plt.plot([start.x, end.x], [start.y, end.y], "r--", lw=3)
            vis.draw_point(start, c="r", s=20)
            vis.draw_point(end, c="r", s=20)

    # plt.scatter(xx, yy, c=ss, cmap="viridis")
    # plt.colorbar()
    plt.savefig("./sample_path.svg")
    plt.show()
