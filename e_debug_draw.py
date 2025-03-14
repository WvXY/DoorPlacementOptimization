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
    # vis.draw_mesh(fp, debug_text="vef").set_axis(axis_off=True).show() # for debug

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

if __name__ == "__main__":
    # Initialize
    case_id = 0

    fp, vis, config = init(case_id)
    fig = vis.get_fig()
    door_system = create_door_system(fp, config)

    frames = []

    def draw_frame(i):
        door_system.move_all_by(0.01)
        vis.clear()

        if i == -1:
            vis.draw_mesh(fp, debug_text="vef").set_axis(title=f"End")
        else:
            vis.draw_mesh(fp, debug_text="vef").set_axis(
                title=f"Iteration: {i} "
            )

    def update(i):
        if i != config.iterations:
            draw_frame(i)
        else:
            draw_frame(-1)

        if i % 10 == 0:
            print(f"Iteration: {i}")

        return (vis.get_fig(),)

    ani = FuncAnimation(
        fig, update, frames=config.iterations + 1, interval=100, repeat=False
    )
    os.makedirs("./results", exist_ok=True)
    ani.save(f"./results/dbg-{config.file_name}.gif", writer="pillow")
    # plt.show()
