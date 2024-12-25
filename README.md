# MasterProject: Door Placement Optimization

## Dependencies
- PythonCDT : for generating constrained delaunay triangulation mesh

## Usage
### Clone this repo
```bash
git clone --recurse-submodules git@github.com:WvXY/MasterProject.git
```

### PIP
```bash
py -m venv .venv
.venv\Scripts\activate 
# source .venv/bin/activate # Linux/MacOS
pip install numpy matplotlib
pip install PythonCDT
```
 
### Conda Environment
```bash
conda create -n mProj python=3.12 numpy matplotlib
conda activate mProj 
pip install PythonCDT
```



## Progress
- [X] Fix navmesh 
- [X] Generate constraint mesh
- [ ] Mesh tweaking functions
- [ ] Door optimizer
- [ ] Optimize and test

## Bugs
- [ ] Logger is not working on windows