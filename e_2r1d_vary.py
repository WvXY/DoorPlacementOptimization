import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy, copy

from g_primitives import Point
from f_primitives import FPoint, FEdge, FFace
from u_data_loader import Loader
from u_visualization import Visualizer
from f_layout import FLayout
from o_door import FDoor
from o_loss_func import loss_func
from o_agent import Agent

def init(case_id, np_seed=0):
    # Settings
    np.random.seed(np_seed)

    # Load data
    ld = Loader(".")
    ld.load_closed_rooms_case(case_id)
    ld.optimize()

    fp = FLayout()
    fp.set_default_types(FPoint, FEdge, FFace)
    fp.create_mesh(ld.vertices, ld.edges, 0)

    # Visualization
    vis = Visualizer()
    # vis.draw_mesh(fp, show=False, draw_text="e")

    return fp, vis



def f(fp, sp=None, batch_size=50):
    # indices = np.random.choice(range(0, 500, 2), batch_size, replace=False)

    score = 0
    valid_paths = 0
    # agents = [Agent(fp) for _ in range(batch_size)]
    # agent.init()
    for i in range(0, 300, 2):
        start = Point(np.random.rand(2))
        end = Point(np.random.rand(2))
        # start = agent.prev_pos
        # end = agent.curr_pos
        tripath = fp.find_tripath(start, end)
        path = fp.simplify(tripath, start, end)
        if path:
            valid_paths += 1
            score += loss_func(path)
        # agent.next()
    return score / valid_paths if valid_paths > 0 else float('inf')


if __name__ == "__main__":
    # Initialize
    case_id = 1
    fp, vis = init(case_id)

    e0 = fp.get_by_eid(0)
    door = FDoor(e0, fp)
    door.activate(np.array([0.1, 0.2]))

    # vis.draw_mesh(fp, show=True, draw_text="ve")

    # sp = np.random.normal(0.8, 0.2, (500, 2))
    # sp = np.append(sp, np.random.normal(0.2, 0.2, (500, 2)), axis=0)
    # sp = np.clip(sp, 0, 1)
    # np.random.shuffle(sp)
    # # sp = np.random.rand(1000, 2)
    # sp = [Point(p) for p in sp]


    # Metropolis-Hastings settings
    T = 0.1
    old_score = f(fp)
    samples = []
    best_score = old_score
    best_x = door.center.copy()

    for iteration in range(100):
        old_pos = door.center.copy()

        print(f"************Iter: {iteration}************")

        door.step()

        new_score = f(fp)
        df = new_score - old_score

        # Accept or reject proposal
        alpha = np.exp(-df / T)
        if  df < 0 or np.random.rand() < alpha:
            old_score = new_score
            if new_score < best_score:
                best_x = door.center.copy()
                best_e = door.bind_edge
                print(f"New Best: at {best_x}, edge: {best_e.eid}")
                best_score = new_score
        else:
            door.load_history()

        samples.append(door.center)
        T *= 0.99  # Annealing

        print(f"Door: {door.center}, "
              f"Old: {old_score:.4f}, New: {new_score:.4f}, Best: {best_score:.4f}, "
              f"Alpha: {alpha:.3f}")


    door.load_manually(best_e, best_x)
    # # Visualize results
    vis.draw_mesh(fp, show=False, draw_text="e")
    for v in samples:
        plt.scatter(v[0], v[1], c="r", s=30, alpha=0.5, marker="s")

    # agent = Agent(fp)
    # agent.init()
    # for i in range(0, 50, 2):
    #     start = agent.prev_pos
    #     end = agent.curr_pos
    #     tripath = fp.find_tripath(start, end)
    #     path = fp.simplify(tripath, start, end)
    #     if path:
    #         c = "g"#np.random.rand(3)
    #         vis.draw_point(start, c=c, s=50)
    #         vis.draw_point(end, c=c, s=50)
    #         vis.draw_linepath(path, c=c, lw=1, a=1)
    #     agent.next()


    vis.show(f"Result {case_id} | Best Center: {best_x} | Final T: {T:.3f}")
    #
    # # # Plot samples
    # plt.hist(samples, bins=100, density=True, alpha=0.5, label="Samples")
    # yy = np.linspace(0.4, 1, 100)
    # # for y in yy:
    # #     agent.set_pos(np.array([0.46875, y]))
    # #     plt.plot(y, f(), 'ro')
    # plt.legend()
    # plt.show()
