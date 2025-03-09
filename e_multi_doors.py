import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

# Load Config and Data
from u_loader import ULoader

# Basic Primitives
from f_layout import FLayout
from g_primitives import Vertex as Point

# Optimization
from o_loss_func import loss_func, traffic_loss_func
from o_optimizer import MHOptimizer

# DOOR SYSTEM
from s_ecs import ECS
from s_door_component import DoorComponent
from s_door_system import DoorSystem

# Visualization
from u_visualization import Visualizer


def init(case_id):
    # Load configs and data
    ULoader.load_config()
    config, obj_data = ULoader.get_config_and_obj(case_id)

    np.random.seed(config.random_seed)

    # Create floor plan
    fp = FLayout()
    fp.from_obj_data(obj_data)
    fp.init_rooms()
    fp.set_room_connections()

    # Visualization
    vis = Visualizer()
    # vis.draw_mesh(fp).set_axis().show()

    return fp, vis, config


def create_door_system(fp, config):
    ecs = ECS()
    door_system = DoorSystem(ecs, fp)

    for door_config in config.doors:
        ra = fp.get_by_rid(door_config[0])
        rb = fp.get_by_rid(door_config[1])
        door = DoorComponent(ra, rb)
        if len(door_config) > 2:
            door.d_len = door_config[2]
        door.need_optimization = True
        door.ratio = 0.5
        ecs.add_door_component(door)

    # front door
    e_door = fp.get_by_eid(config.front_door[0])
    front_door = DoorComponent(None, None)
    front_door.need_optimization = False
    front_door.bind_edge = e_door
    front_door.e_len = e_door.get_length()
    front_door.ratio = config.front_door[1]
    ecs.add_door_component(front_door)

    door_system.activate_all()

    return door_system


def make_sample_points(fp, n=300):
    sample_points = []
    while n > 0:
        p = Point(np.random.rand(2))
        if fp.is_inside(p):
            sample_points.append(p)
            n -= 1
    return sample_points


def f(fp, sample_points, batch_size=50):
    # indices = np.random.choice(range(0, 500, 2), batch_size, replace=False)

    traffic_loss = 0
    for i in range(0, len(sample_points) - 1):
        # for i in range(0, len(sample_points), 2):
        start = sample_points[i]
        end = sample_points[i + 1]
        tripath = fp.find_tripath(start, end)
        path = fp.simplify(tripath, start, end)
        if path:
            traffic_loss += traffic_loss_func(path)
    traffic_loss /= len(sample_points) / 2

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
    case_id = 0

    fp, vis, config = init(case_id)
    fig = vis.get_fig()

    door_system = create_door_system(fp, config)

    sample_points = make_sample_points(fp, config.sample_size)
    # Metropolis-Hastings
    frames = []
    mh = MHOptimizer(fp, door_system, f, config.temperature, sample_points)
    mh.init()

    def draw_frame(i):
        mh.step()
        vis.clear().draw_mesh(fp, debug_text="")

        for door in door_system.ecs.doors.values():
            if door.need_optimization:
                pos = door_system.ratio_to_xy(door, door.ratio)
                vis.draw_point(pos, c="r")
            else:
                pos = door_system.ratio_to_xy(door, door.ratio)
                vis.draw_point(pos, c="b")

        if i == -1:
            vis.set_axis(title=f"Result | Best Score: {mh.best_score:.3f}")
        else:
            vis.set_axis(
                title=f"Iteration: {i} "
                f"| Score: {mh.prev_score:.3f} "
                f"| Best Score: {mh.best_score:.3f}"
            )

    def update(i):
        if i != config.iterations:
            mh.step(sigma=config.sigma)
            draw_frame(i)
        else:
            mh.end()
            draw_frame(-1)

        if i % 10 == 0:
            print(f"Iteration: {i} | Score: {mh.prev_score:.3f}")
        return (vis.get_fig(),)

    ani = FuncAnimation(
        fig, update, frames=config.iterations + 1, interval=100, repeat=False
    )
    os.makedirs("./results", exist_ok=True)
    ani.save(f"./results/res-{config.file_name}.gif", writer="pillow")
    # plt.show()
