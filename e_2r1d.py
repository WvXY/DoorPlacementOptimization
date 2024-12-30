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

# Settings
case_id = 0
np.random.seed(0)

# Load data
ld = Loader(".")
ld.load_closed_rooms_case(case_id)
ld.optimize()

nm = FLayout()
nm.set_default_types(FPoint, FEdge, FFace)
nm.create_mesh(ld.vertices, ld.edges, 0)

# Initialize door
e0 = nm.get_by_eid(0)
door = FDoor(e0)
door.activate(np.array([0.5, 0.1]))
nm.append(door.new_verts, door.new_edges, door.new_faces)

sp = np.random.rand(500, 2)
sp = [Point(p) for p in sp]

# Visualization
vis = Visualizer()


def f(batch_size=50):
    # indices = np.random.choice(range(0, 500, 2), batch_size, replace=False)
    score = 0
    valid_paths = 0
    for i in range(0, 200, 2):
        start = sp[i]
        end = sp[i + 1]
        tripath = nm.find_tripath(start, end)
        path = nm.simplify(tripath, start, end)
        if path:
            valid_paths += 1
            score += loss_func(path)
    return score / valid_paths if valid_paths > 0 else float('inf')

# Metropolis-Hastings settings
T = 0.01
old_score = f()
samples = []
best_x = door.center.copy()
best_score = old_score

for iteration in range(200):
    old_pos = door.center.copy()

    door.step()

    new_score = f()
    df = new_score - old_score

    # Accept or reject proposal
    alpha = np.exp(-df / T)
    if  df < 0 or np.random.rand() < alpha:
        old_score = new_score
        if new_score < best_score:
            best_x = door.center.copy()
            best_score = new_score
    else:
        door.set_pos(old_pos)  # Reject proposal

    samples.append(door.center[1])
    T *= 0.99  # Annealing

    print(f"Iteration: {iteration}, door: {door.center}, "
          f"Old Score: {old_score:.3f}, New Score: {new_score:.3f}, Alpha: {alpha:.3f}")

door.set_pos(best_x)

# Visualize results
vis.draw_mesh(nm, show=False, draw_text="")
vis.show(f"Result {case_id} | Best Center: {best_x}")

# # Plot samples
plt.hist(samples, bins=100, density=True, alpha=0.5, label="Samples")
# yy = np.linspace(0.4, 1, 100)
# for y in yy:
#     door.set_pos(np.array([0.46875, y]))
#     plt.plot(y, f(), 'ro')
plt.legend()
plt.show()
