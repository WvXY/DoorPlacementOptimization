# Door Placement Optimization

## Introduction

Door optimization for floor plan or map generation using Navmesh.
Place doors based on human traffic flow and shortest path.

## Dependencies

- Python3.11 or higher
- PythonCDT : for generating constrained delaunay triangulation mesh

## Usage

### Clone this repo

```bash
git clone --recurse-submodules https://github.com/WvXY/DoorPlacementOptimization.git
```

### PIP

```bash
cd DoorPlacementOptimization
python -m venv .venv
.venv\Scripts\activate 
# source .venv/bin/activate # Linux/MacOS
pip install numpy matplotlib
pip install PythonCDT/
```

### Conda Environment

```bash
cd DoorPlacementOptimization
conda create -n mProj python=3.12 numpy matplotlib
conda activate mProj 
pip install PythonCDT/
```

## Structure

- `g_xxx`: Geometry
- `f_xxx`: Floor plan related
- `s_xxx`: ECS System and related
- `o_xxx`: Optimization
- `u_xxx`: Utility functions
- `t_xxx`: Test/unit test
- `e_xxx`: Experiment/Execution

--------
## Notes

### Progress & TODOs

- [X] Fix navmesh
- [X] Generate constraint mesh
- [X] Mesh tweaking functions
- [X] Door optimizer
- [X] Optimize and test
- [X] Refactor and improve performance
- [ ] GPU acceleration
- [ ] Refactor#2 for better structure
- [ ] UI
- [ ] 

### Bugs

- [ ] Logger is not working on windows
- [X] Cuts on 2 edges of the same triangle may broke the geometry.
- [ ] When point on the edge, path cannot be found.

### Black Formater Setting

```--line-length=80 --preview```