# from pathfinder import navmesh_baker as nmb
# # create baker object
# baker = nmb.NavmeshBaker()
# # add geometry, for example a simple plane
# # the first array contains vertex positions, the second array contains polygons of the geometry
# baker.add_geometry([(-4.0, 0.0, -4.0), (-4.0, 0.0, 4.0), (4.0, 0.0, 4.0), (4.0, 0.0, -4.0)], [[0, 1, 2, 3]])
# # bake navigation mesh
# baker.bake()
# # obtain polygonal description of the mesh
# vertices, polygons = baker.get_polygonization()
#
# import pathfinder as pf
#
# pathfinder = pf.PathFinder(vertices, polygons)
# start = (1.0, 0.0, 1.0)
# finish = (3.0, 0.0, 3.0)
# path = pathfinder.search_path(start, finish)
# print(path)
#
