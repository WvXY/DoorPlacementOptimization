# Door Placement Optimization

## Introduction
Door optimization for floor plan or map generation using Navmesh. 
Place doors based on human traffic flow and shortest path.


## Dependencies

- PythonCDT : for generating constrained delaunay triangulation mesh

## Usage

### Clone this repo

```bash
git clone --recurse-submodules https://github.com/WvXY/DoorPlacementOptimization.git
```

### PIP

```bash
python -m venv .venv
.venv\Scripts\activate 
# source .venv/bin/activate # Linux/MacOS
pip install numpy matplotlib
pip install PythonCDT/
```

### Conda Environment

```bash
conda create -n mProj python=3.12 numpy matplotlib
conda activate mProj 
pip install PythonCDT/
```

## Progress

- [X] Fix navmesh
- [X] Generate constraint mesh
- [X] Mesh tweaking functions
- [X] Door optimizer
- [ ] Optimize and test

## Bugs

- [ ] Logger is not working on windows
- [ ] `PythonCDT` is not working on windows

## Notes

### Naming Conventions

- `g_xxx`: Geometry
- `f_xxx`: Floor plan related
- `s_xxx`: ECS System and related
- `o_xxx`: Optimization
- `u_xxx`: Utility functions
- `t_xxx`: Test/unit test
- `e_xxx`: Experiment
