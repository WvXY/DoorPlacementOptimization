import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

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
    ld.load_custom("/assets/2r1d_loss.obj")

    fp = FLayout()
    fp.create_mesh(ld.vertices, ld.edges, 0)
    fp.init_rooms()
    fp.set_room_connections()

    # Visualization
    vis = Visualizer()
    vis.draw_mesh(fp, debug_text="e")

    return fp, vis


def create_door_system(fp):
    r0 = fp.get_by_rid(0)
    r1 = fp.get_by_rid(1)
    e12 = fp.get_by_eid(35)

    ecs = ECS()
    door_system = DoorSystem(ecs, fp)
    door_cmp = DoorComponent(r0, r1)
    ecs.add_door_component(door_cmp)
    # manually set the ratio
    door_cmp.ratio = 0.16
    door_cmp.bind_edge = e12

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


def metropolis_hasting(fp, door_system, iters=200):
    # Metropolis-Hastings settings
    old_score = f(fp, sp)
    losses = []

    best_score = old_score
    best_e, best_r = door_system.get_states()

    door_comp = door_system.ecs.get_door_component(0)

    for iteration in range(iters):

        door_system.move_all_by(0.02)
        print(iteration, door_comp)

        new_score = f(fp, sp)

        center = door_system.ratio_to_xy(door_comp, door_comp.ratio)
        losses.append([center, new_score])

    door_system.deactivate(door_comp)

    return best_e, best_r, losses


if __name__ == "__main__":
    # Initialize
    case_id = 3
    n_sp = 400
    iters = 80

    fp, vis = init_fp_vis(case_id)

    vis.draw_mesh(fp, debug_text="ve")
    vis.draw_floor_plan(fp, draw_connection=True)

    door_system = create_door_system(fp)

    sp = make_sample_points(n_sp)

    best_e, best_r, losses = metropolis_hasting(fp, door_system, iters=iters)

    # visualize
    vis.draw_mesh(fp)
    # vis.draw_floor_plan(fp, show=True, draw_connection=True)

    xx = [x[0][0] for x in losses]
    yy = [x[0][1] for x in losses]
    ss = [x[1] for x in losses]

    plt.scatter(xx, yy, c=ss, cmap="viridis")
    plt.colorbar()
    plt.savefig("./2r1d_loss.svg")
    plt.show()

    plt.plot(ss)
    plt.savefig("./loss_func_plot.svg")
    plt.show()
