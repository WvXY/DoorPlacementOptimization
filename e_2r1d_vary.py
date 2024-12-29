import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy

from g_primitives import Point
from f_primitives import FPoint, FEdge, FFace
from u_data_loader import Loader
from u_visualization import Visualizer
from f_layout import FLayout
from o_door import FDoor
from o_loss_func import loss_func

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



def f(fp, sp, batch_size=50):
    # indices = np.random.choice(range(0, 500, 2), batch_size, replace=False)
    score = 0
    valid_paths = 0
    for i in range(0, 200, 2):
        start = sp[i]
        end = sp[i + 1]
        tripath = fp.find_tripath(start, end)
        path = fp.simplify(tripath, start, end)
        if path:
            valid_paths += 1
            score += loss_func(path)
    return score / valid_paths if valid_paths > 0 else float('inf')


if __name__ == "__main__":
    # Initialize
    case_id = 1
    fp, vis = init(case_id)

    e0 = fp.get_by_eid(0)
    agent = FDoor(e0, fp)
    agent.activate(np.array([0.1, 0.2]))

    # vis.draw_mesh(fp, show=True, draw_text="ve")

    sp = np.random.rand(500, 2)
    sp = [Point(p) for p in sp]


    # Metropolis-Hastings settings
    T = 0.1
    old_score = f(fp, sp)
    samples = []
    best_score = old_score
    best_x = agent.center.copy()

    for iteration in range(200):
        old_pos = agent.center.copy()

        print(f"************Iter: {iteration}************")

        agent.step()

        new_score = f(fp, sp)
        df = new_score - old_score

        # Accept or reject proposal
        alpha = np.exp(-df / T)
        # if delta_f < 0 or np.random.rand() < np.exp(-delta_f / T):  # Accept criterion
        if  df < 0 or np.random.rand() < alpha:
            old_score = new_score
            if new_score < best_score:
                best_x = agent.center.copy()
                best_score = new_score
        else:
            agent.load_history()

        samples.append(agent.center)
        T *= 0.99  # Annealing

        print(f"Agent: {agent.center}, "
              f"Old Score: {old_score:.3f}, New Score: {new_score:.3f}, Alpha: {alpha:.3f}")

    agent.set_door_center(best_x)
    #
    # # Visualize results
    vis.draw_mesh(fp, show=False)
    for v in samples:
        plt.scatter(v[0], v[1], c="r", s=20, alpha=0.1, marker="s")

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
