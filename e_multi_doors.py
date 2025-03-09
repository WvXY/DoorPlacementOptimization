import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
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
from o_loss_func import loss_func, traffic_loss_func
from o_optimizer import MHOptimizer
from u_data_loader import Loader
from u_visualization import Visualizer


def init(case_id, np_seed=0):
    # Settings
    np.random.seed(np_seed)

    # Load data
    ld = Loader(".")
    # ld.load_closed_rooms_case(7)
    ld.load_w_walls_case(case_id)
    # ld.load_final_case(0)

    fp = FLayout()
    fp.create_mesh(ld.vertices, ld.edges, 0)
    fp.init_rooms()
    fp.set_room_connections()

    # Visualization
    vis = Visualizer()

    return fp, vis


def create_door_system(fp):

    r0 = fp.get_by_rid(0)
    r1 = fp.get_by_rid(1)
    r2 = fp.get_by_rid(2)

    ecs = ECS()
    door_system = DoorSystem(ecs, fp)

    door02 = DoorComponent(r2, r0)
    ecs.add_door_component(door02)
    #
    door12 = DoorComponent(r1, r2)
    ecs.add_door_component(door12)

    # front door
    e_d = fp.get_by_eid(21)
    front_door = DoorComponent(None, None)
    front_door.need_optimization = False
    front_door.bind_edge = e_d
    front_door.e_len = e_d.get_length()
    front_door.ratio = 0.5
    ecs.add_door_component(front_door)

    door_system.activate_all()

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
            traffic_loss += traffic_loss_func(path)
    traffic_loss /= len(sp) / 2

    # entrance loss
    entrance_loss = 0
    st, end = None, []
    for door in door_system.ecs.doors.values():
        pos = door_system.ratio_to_xy(door, door.ratio)
        # pos = pos + 0.01
        if not door.need_optimization:
            pos[1] -= 0.01
            # print(f"Front door pos: {pos}")
            st = Point(pos)
        else:
            end.append(Point(pos))

    for e in end:
        tripath = fp.find_tripath(st, e)
        path = fp.simplify(tripath, st, e)
        if path is None:
            print(f"Entrance path not found: {st.xy} -> {e.xy}")
            entrance_loss += np.sqrt((st.xy - e.xy) @ (st.xy - e.xy)) / len(end)
        else:
            entrance_loss += loss_func(path) / len(end)

    return traffic_loss + 2 * entrance_loss


if __name__ == "__main__":
    # Initialize
    case_id = 7
    n_sp = 100
    iters = 20
    T = 0.1

    fp, vis = init(case_id)
    fig = vis.get_fig()

    door_system = create_door_system(fp)

    sp = make_sample_points(fp, n_sp)
    # Metropolis-Hastings
    frames = []
    mh = MHOptimizer(fp, door_system, f, T, sp)
    mh.init()

    def draw_frame(i):
        mh.step()
        vis.clear().draw_mesh(fp, debug_text="")
        if i == -1:
            vis.set_axis(title=f"Result | Best Score: {mh.best_score:.3f}")
        else:
            vis.set_axis(
                title=f"Iteration: {i} "
                f"| Score: {mh.prev_score:.3f} "
                f"| Best Score: {mh.best_score:.3f}"
            )

    def update(i):
        global iters
        if i != iters:
            mh.step()
            draw_frame(i)
        else:
            mh.end()
            draw_frame(-1)

        return (vis.get_fig(),)

    ani = FuncAnimation(fig, update, frames=iters + 1, interval=10, repeat=False)
    ani.save("./multi_doors.gif", writer="pillow")
    # plt.show()
