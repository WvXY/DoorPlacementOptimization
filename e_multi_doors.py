import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
import numpy as np
from tqdm import tqdm
from functools import partial
import imageio

# Basic Primitives
from f_layout import FLayout
from g_primitives import Vertex as Point

# DOOR SYSTEM
from s_ecs import ECS
from s_door_system import DoorSystem
from s_door_component import DoorComponent

# Optimization
from o_loss_func import loss_func
from o_optimizer import MHOptimizer
from u_data_loader import Loader
from u_visualization import Visualizer


def init(case_id, np_seed=0):
    # Settings
    np.random.seed(np_seed)

    # Load data
    ld = Loader(".")
    # ld.load_closed_rooms_case(7)
    ld.load_w_walls_case(7)
    # ld.load_final_case(0)

    fp = FLayout()
    fp.create_mesh(ld.vertices, ld.edges, 0)
    fp.init_rooms()
    fp.set_room_connections()

    # Visualization
    vis = Visualizer()
    # vis.draw_mesh(
    #     fp, show=False, draw_text="e", axis_show=False, axis_equal=True
    # )
    # plt.savefig("./case_fp_init.svg")

    return fp, vis


def create_door_system(fp):
    # vis.draw_floor_plan(fp, show=False, draw_connection=True)
    # plt.axis("equal")
    # plt.axis("off")
    # plt.title("Room Initialization")
    # plt.savefig("./case_room_init.svg")
    # plt.show()

    r0 = fp.get_by_rid(0)
    r1 = fp.get_by_rid(1)
    r2 = fp.get_by_rid(2)
    # r3 = fp.get_by_rid(3)
    # r4 = fp.get_by_rid(4)
    # r5 = fp.get_by_rid(5)

    ecs = ECS()
    door_system = DoorSystem(ecs, fp)

    door02 = DoorComponent(r2, r0)
    ecs.add_door_component(door02)
    #
    door12 = DoorComponent(r1, r2)
    ecs.add_door_component(door12)
    #
    # door20 = DoorComponent(r2, r0, 0.3)
    # ecs.add_door_component(door20)
    # #
    # door04 = DoorComponent(r0, r4)
    # ecs.add_door_component(door04)
    #
    # door25 = DoorComponent(r2, r5, door_length=0.2)
    # ecs.add_door_component(door25)

    # front door
    e_d = fp.get_by_eid(21)
    front_door = DoorComponent(None, None)
    front_door.need_optimization = False
    front_door.bind_edge = e_d
    front_door.e_len = e_d.get_length()
    front_door.ratio = 0.5
    ecs.add_door_component(front_door)

    door_system.activate_all()

    # vis.draw_mesh(fp, show=False, clear=True, draw_text="")
    # for door in door_system.ecs.doors.values():
    #     pos = door_system._ratio_to_pos(door, door.ratio)
    #     vis.draw_point(Point(pos), c="r", s=50)
    # plt.axis("equal")
    # plt.title("Door System")
    # plt.axis("off")
    # plt.savefig("./abl_door_init.svg")
    # vis.show("Door System")

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
    traffic_loss /= len(sp) / 2

    # entrance loss
    entrance_loss = 0
    st, end = None, []
    for door in door_system.ecs.doors.values():
        pos = door_system._ratio_to_pos(door, door.ratio)
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


# def metropolis_hasting(fp, door_system, T=0.01, iters=200, vis=None):
#     # Metropolis-Hastings settings
#     old_score = f(fp, sp)
#     samples = []
#     frames = []
#     losses = []
#     best_score = old_score
#     best_e, best_r = door_system.get_states()
#     fig = vis.get_fig()
#
#     for iteration in tqdm(range(iters)):
#
#         door_system.propose(0.05)
#
#         new_score = f(fp, sp)
#         df = new_score - old_score
#
#         # Accept or reject proposal
#         alpha = np.exp(-df / T)
#         if df < 0 or np.random.rand() < alpha:
#             old_score = new_score
#             losses.append(new_score)
#             if new_score < best_score:
#                 best_e, best_r = door_system.get_states()
#                 best_score = new_score
#         else:
#             door_system.reject()
#
#         if vis and iteration % 1 == 0:
#             fig.gca().cla()
#             vis.draw_mesh(
#                 fp,
#                 show=False,
#                 draw_text="",
#                 clear=True,
#                 fig_title=f"Iteration: {iteration} | Score: {new_score:.3f} | Best Score: {best_score:.3f}",
#             )
#
#             # vis.draw_mesh(
#             #     fp,
#             #     show=True,
#             #     draw_text="vf",
#             #     clear=True,
#             #     fig_title=f"Iteration: {iteration} | Score: {new_score} | Best Score: {best_score}",
#             # )
#
#             fig.canvas.draw()
#             image = np.frombuffer(fig.canvas.tostring_argb(), dtype="uint8")
#             image = image.reshape(fig.canvas.get_width_height()[::-1] + (4,))[
#                 ..., 1:
#             ]
#             frames.append(image)
#             plt.close(fig)
#
#         T *= 0.99  # Annealing
#         # losses.append(new_score)
#
#     door_system.load_manually(best_e, best_r)
#
#     # draw result
#     fig.gca().cla()
#     vis.draw_mesh(
#         fp,
#         show=False,
#         draw_text="",
#         clear=True,
#         fig_title=f"Result | Best Score: {best_score:.3f}",
#     )
#
#     fig.canvas.draw()
#     image = np.frombuffer(fig.canvas.tostring_argb(), dtype="uint8")
#     image = image.reshape(fig.canvas.get_width_height()[::-1] + (4,))[..., 1:]
#     frames.append(image)
#     plt.close(fig)
#
#     return (best_e, best_r, losses, frames)
#

if __name__ == "__main__":
    # Initialize
    case_id = 1
    n_sp = 200
    iters = 12
    T = 0.1

    fp, vis = init(case_id)
    fig = vis.get_fig()

    door_system = create_door_system(fp)

    sp = make_sample_points(fp, n_sp)
    # Metropolis-Hastings
    frames = []
    mh = MHOptimizer(fp, door_system, f, T, sp)
    mh.init()
    for i in tqdm(range(iters)):
        mh.step()

        # fig.gca().cla()
        vis.draw_mesh(
            mh.layout,
            show=True,
            draw_text="",
            clear=True,
            fig_title=f"Iteration: {i} ",
            # f"| Score: {mh.prev_score:.3f} "
            # f"| Best Score: {mh.best_score:.3f}",
        )

        # fig.canvas.draw()
        # image = np.frombuffer(fig.canvas.tostring_argb(), dtype="uint8")
        # image = image.reshape(fig.canvas.get_width_height()[::-1] + (4,))[
        #     ..., 1:
        # ]
        # frames.append(image.copy())
        # plt.close(fig)

    mh.end()
    # print(frames)

    # save gif
    # def create_gif(frames, filename):
    #     imageio.mimsave(filename, frames, fps=60)
    #
    # create_gif(frames, "anim2.gif")
