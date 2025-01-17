import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

# Basic Primitives
from f_layout import FLayout
from g_primitives import Vertex as Point

# DOOR SYSTEM
from s_ecs import ECS
from s_door_system import DoorSystem
from s_door_component import DoorComponent

# Optimization
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
    vis.draw_mesh(fp, show=False, draw_text="")
    # plt.savefig("./case_2doors_mesh.svg")

    return fp, vis


def create_door_system(fp):
    vis.draw_floor_plan(fp, show=True, draw_connection=True)

    r0 = fp.get_by_rid(0)
    r1 = fp.get_by_rid(1)
    r2 = fp.get_by_rid(2)
    r3 = fp.get_by_rid(3)
    r4 = fp.get_by_rid(4)
    r5 = fp.get_by_rid(5)

    e14 = fp.get_by_eid(14)

    ecs = ECS()
    door_system = DoorSystem(ecs, fp)

    vis.draw_mesh(fp, show=True, clear=True, draw_text="e")
    #
    # door31 = DoorComponent(r3, r1, door_length=0.18)
    # ecs.add_door_component(door31)
    # # door_system.activate(door21)

    door02 = DoorComponent(r0, r2)
    ecs.add_door_component(door02)

    door12 = DoorComponent(r1, r2)
    ecs.add_door_component(door12)

    door23 = DoorComponent(r2, r3)
    ecs.add_door_component(door23)

    door24 = DoorComponent(r2, r4)
    ecs.add_door_component(door24)

    door25 = DoorComponent(r2, r5, door_length=0.2)
    ecs.add_door_component(door25)

    # front door
    front_door = DoorComponent(None, None)
    front_door.need_optimization = False
    front_door.bind_edge = e14
    front_door.e_len = e14.get_length()
    front_door.ratio = 0.8
    ecs.add_door_component(front_door)

    door_system.activate_all()

    vis.draw_mesh(fp, show=False, clear=True, draw_text="")
    for door in door_system.ecs.doors.values():
        pos = door_system._ratio_to_pos(door, door.ratio)
        vis.draw_point(Point(pos), c="r", s=50)
    vis.show("Door System")

    return door_system


def make_sample_points(fp, n=300):
    sp = []
    while n > 0:
        p = Point(np.random.rand(2))
        if fp.is_inside(p):
            sp.append(p)
            n -= 1
    return sp


def f(fp, sp, batch_size=50):
    # indices = np.random.choice(range(0, 500, 2), batch_size, replace=False)

    traffic_loss = 0
    for i in range(0, len(sp) - 1):
        # for i in range(0, len(sp), 2):
        start = sp[i]
        end = sp[i + 1]
        tripath = fp.find_tripath(start, end)
        path = fp.simplify(tripath, start, end)
        if path:
            traffic_loss += loss_func(path)

    # entrance loss
    entrance_loss = 0
    st, end = None, []
    for door in door_system.ecs.doors.values():
        pos = door_system._ratio_to_pos(door, door.ratio)
        if not door.need_optimization:
            st = Point(pos)
        else:
            end.append(Point(pos))

    for e in end:
        tripath = fp.find_tripath(st, e)
        path = fp.simplify(tripath, st, e)
        if path:
            entrance_loss += 2 * loss_func(path) / len(end)

    return entrance_loss


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
                fig_title=f"Iteration: {iteration} | Score: {new_score:.3f} | Best Score: {best_score:.3f}",
            )

            # vis.draw_mesh(
            #     fp,
            #     show=True,
            #     draw_text="vf",
            #     clear=True,
            #     fig_title=f"Iteration: {iteration} | Score: {new_score} | Best Score: {best_score}",
            # )

        T *= 0.99  # Annealing
        # losses.append(new_score)

    door_system.load_manually(best_e, best_r)

    return best_e, best_r, losses


if __name__ == "__main__":
    # Initialize
    case_id = 2
    n_sp = 100
    iters = 100
    T = 0.001

    fp, vis = init(case_id)

    # vis.draw_mesh(
    #     fp, show=True, draw_text="ve", axis_show=False, axis_equal=True
    # )
    # vis.draw_floor_plan(fp, show=True, draw_connection=True)

    door_system = create_door_system(fp)

    vis.draw_mesh(fp, show=False, draw_text="", clear=True)
    # plt.savefig("./case_2doors_init.svg")
    plt.show()

    sp = make_sample_points(fp, n_sp)
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
    vis.draw_mesh(fp, show=False, draw_text="", clear=True)
    for door in door_system.ecs.doors.values():
        pos = door_system._ratio_to_pos(door, door.ratio)
        vis.draw_point(Point(pos), c="r", s=50)

    # start = Point(np.array([0.4, 0.6]))
    # end = Point(np.array([0.3, 0.35]))
    # tripath = fp.find_tripath(start, end)
    # path = fp.simplify(tripath, start, end)
    # c = np.random.rand(3)
    # vis.draw_point(start, c=c, s=50)
    # vis.draw_point(end, c=c, s=50)
    # vis.draw_linepath(path, c=c, lw=1, a=1)

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
        else:
            plt.plot([start.x, end.x], [start.y, end.y], "r--", lw=1)

    # vis.show(f"Result {case_id}")
    #
    # plt.plot(losses)
    # plt.savefig("./case_2doors_res.svg")
    plt.show()
