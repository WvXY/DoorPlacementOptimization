import concurrent.futures
import numpy as np

# Your project imports
from f_primitives import FPoint, FEdge, FFace
from f_layout import FLayout
from u_visualization import Visualizer
from u_data_loader import Loader

class Agent:
    def __init__(self, fp=None):
        self.prev_pos = None
        self.curr_pos = None
        self.fp = fp  # reference to shared FloorPlan

    def set_floor_plan(self, floor_plan):
        self.fp = floor_plan

    def init(self):
        # We'll pick two random positions so that prev_pos != curr_pos
        self.next()
        self.next()

    def next(self):
        self.prev_pos = self.curr_pos
        self.curr_pos = FPoint(np.random.rand(2))
        # Keep trying until we find a random position inside the floor plan
        while not self.inside_floor_plan():
            self.curr_pos = FPoint(np.random.rand(2))

    def inside_floor_plan(self):
        return self.fp.get_point_inside_face(self.curr_pos) is not None


def run_agent(agent, steps=100):
    """
    Worker function (run in a thread).
    The agent references the same 'floor_plan' in memory as other agents.
    We collect and return the path data for visualization later.
    """
    all_paths = []
    for _ in range(steps):
        tripath = agent.fp.find_tripath(agent.prev_pos, agent.curr_pos)
        path    = agent.fp.simplify(tripath, agent.prev_pos, agent.curr_pos)
        all_paths.append(path)
        agent.next()
    return all_paths


if __name__ == "__main__":
    import sys, sysconfig

    # Check GIL status
    py_version = float(".".join(sys.version.split()[0].split(".")[0:2]))
    status = sysconfig.get_config_var("Py_GIL_DISABLED")

    if py_version >= 3.13:
        status = sys._is_gil_enabled()
    if status is None:
        print("GIL cannot be disabled for Python version <= 3.12")
    if status == 0:
        print("GIL is currently disabled")
    if status == 1:
        print("GIL is currently active")

    # -------------------------------------
    # 1) Build one FloorPlan in main thread
    # -------------------------------------
    np.random.seed(0)  # for reproducibility

    ld = Loader(".")
    ld.load_w_walls_case(5)
    ld.optimize()

    fp = FLayout()
    fp.set_default_types(FPoint, FEdge, FFace)
    fp.create_mesh(ld.vertices, ld.edges, 0)

    # -------------------------------------
    # 2) Create multiple Agents
    #    All share the SAME floor_plan object
    # -------------------------------------
    num_agents = 12
    agents = []
    for i in range(num_agents):
        agent = Agent()
        agent.set_floor_plan(fp)  # all agents see the same fp
        agent.init()
        agents.append(agent)

    # -------------------------------------
    # 3) Use Threads for concurrency
    # -------------------------------------
    steps_per_agent = 100
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        # Submit each agent to the thread pool
        futures = [executor.submit(run_agent, agent, steps_per_agent) for agent in agents]
        # Gather the results (list of lists of paths)
        results = [f.result() for f in futures]

    # -------------------------------------
    # 4) Visualization in the main thread
    # -------------------------------------
    vis = Visualizer()
    vis.draw_mesh(fp, show=False)

    # 'results[i]' is the list of paths for agent i
    for agent_paths in results:
        for path in agent_paths:
            # Draw each path
            vis.draw_linepath(path, c="k", lw=2)

    vis.show()
