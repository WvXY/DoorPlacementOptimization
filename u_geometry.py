from g_primitives import Vertex, Edge, Face


def split_edge(edge, position, Point=Vertex, Edge=Edge, Face=Face):
    """Split edge into two edges by a point"""

    p_cut = Point(position)
    e_new = Edge(p_cut, edge.to)
    e_new_t = Edge(edge.to, p_cut)
    diag, diag_t = edge.diagonal_vertex, edge.twin.diagonal_vertex
    e0, e0_t = Edge(p_cut, diag), Edge(diag, p_cut)
    e1, e1_t = Edge(diag_t, p_cut), Edge(p_cut, diag_t)
    f0, f1 = Face(), Face()

    # set properties[face, twin, prev, next, diag]
    e_new.set_properties(f0, e_new_t, edge, edge.next, diag)
    e_new_t.set_properties(f1, e_new, edge.twin.prev, edge.twin, diag_t)
    e0.set_properties(edge.face, e0_t, edge, edge.prev, edge.ori)
    e0_t.set_properties(f0, e0, edge.next, e_new, edge.to)
    e1.set_properties(edge.twin.face, e1_t, edge.twin.next, edge.twin, edge.ori)
    e1_t.set_properties(f1, e1, e_new_t, edge.twin.prev, edge.to)

    e_new.is_blocked = edge.is_blocked
    e_new_t.is_blocked = edge.twin.is_blocked

    # set vertices
    p_cut.edges = [e_new, e_new_t, e0, e0_t, e1, e1_t]
    p_cut.faces = [f0, f1, edge.face, edge.twin.face]

    # set faces
    f0.half_edges = [edge.next, e0_t, e_new]
    f1.half_edges = [e1_t, edge.twin.prev, e_new_t]
    f1.adj_faces = [f0, edge.twin.prev.face, edge.twin.face]
    f0.adj_faces = [f1, edge.next.face, edge.face]
    f0.verts = [edge.to, diag, p_cut]
    f1.verts = [edge.to, p_cut, diag_t]

    # # update edge.face and edge.twin.face
    # if edge.next.twin is not None:
    #     f_adj_1 = edge.next.twin.face
    #     f_adj_1.adj_faces = [f0, f_adj_1.adj_faces[1], f_adj_1.adj_faces[2]]

    edge.face.adj_faces = [f0, edge.twin.face, edge.prev.twin.face]
    edge.twin.face.adj_faces = [f1, edge.face, edge.twin.next.twin.face]
    edge.face.half_edges = [edge.prev, edge, e0]
    edge.twin.face.half_edges = [e1, edge.twin, edge.twin.next]
    edge.face.verts = [edge.ori, diag, p_cut]
    edge.twin.face.verts = [edge.ori, p_cut, diag_t]

    # update adj faces
    edge.twin.prev.twin.face.adj_faces = [
        f for f in edge.twin.prev.face.adj_faces if f != edge.twin.prev.face
    ] + [f1]
    edge.next.face.adj_faces = [
        f for f in edge.next.face.adj_faces if f != edge.face
    ] + [f0]

    edge.twin.ori = p_cut
    edge.twin.prev = e1
    edge.to = p_cut
    edge.next = e0

    # newly added Points, Edges, Faces
    return [p_cut], [e_new, e_new_t, e0, e0_t, e1, e1_t], [f0, f1]


# def split_edge(edge, position, Point=Vertex, Edge=Edge, Face=Face):
#     """Split edge into two edges by a point, ensuring counterclockwise order."""
#
#     # Create the new vertex at the given position
#     p_cut = Point(position)
#     # Create the new edges introduced by the cut
#     e_new = Edge(p_cut, edge.to)
#     e_new_t = Edge(edge.to, p_cut)
#     diag, diag_t = edge.diagonal_vertex, edge.twin.diagonal_vertex
#     e0, e0_t = Edge(p_cut, diag), Edge(diag, p_cut)
#     e1, e1_t = Edge(diag_t, p_cut), Edge(p_cut, diag_t)
#     f0, f1 = Face(), Face()
#
#     # Set properties of the new edges (face, twin, prev, next, diag)
#     # Note: These assignments are usually determined by the geometry of your structure
#     e_new.set_properties(f0, e_new_t, edge, edge.next, diag)
#     e_new_t.set_properties(f1, e_new, edge.twin.prev, edge.twin, diag_t)
#     e0.set_properties(edge.face, e0_t, edge, edge.prev, edge.ori)
#     e0_t.set_properties(f0, e0, edge.next, e_new, edge.to)
#     e1.set_properties(edge.twin.face, e1_t, edge.twin.next, edge.twin, edge.ori)
#     e1_t.set_properties(f1, e1, e_new_t, edge.twin.prev, edge.to)
#
#     # Set the vertex properties for p_cut
#     p_cut.edges = [e_new, e_new_t, e0, e0_t, e1, e1_t]
#     p_cut.faces = [f0, f1, edge.face, edge.twin.face]
#
#     # For f0 and f1, reorder half_edges and verts in CCW order.
#     # Assume that edge.next -> e0_t -> e_new forms a triangle; we want them CCW:
#     f0.half_edges = [e_new, e0_t, edge.next]
#     f0.verts = [p_cut, diag, edge.to]
#
#     f1.half_edges = [e_new_t, edge.twin.prev, e1_t]
#     f1.verts = [p_cut, edge.to, diag_t]
#
#     # Update adjacent faces of f0 and f1 accordingly (making sure they are consistent)
#     f0.adj_faces = [f1, edge.next.face, edge.face]
#     f1.adj_faces = [f0, edge.twin.prev.face, edge.twin.face]
#
#     # Update the original faces that were split. Reorder their half-edges and vertices as well.
#     edge.face.half_edges = [e0, edge, edge.prev]  # Reordered for CCW
#     edge.face.verts = [p_cut, diag, edge.ori]  # Match the new order
#
#     edge.twin.face.half_edges = [edge.twin.next, edge.twin, e1]
#     edge.twin.face.verts = [p_cut, diag_t, edge.ori]
#
#     edge.face.adj_faces = [f0, edge.prev.face, edge.twin.face]
#     edge.twin.face.adj_faces = [f1, edge.twin.next.face, edge.face]
#
#     # Update references from the original split edge and its twin
#     edge.twin.ori = p_cut
#     edge.twin.prev = e1
#     edge.to = p_cut
#     edge.next = e0
#
#     # Return the newly created elements
#     return [p_cut], [e_new, e_new_t, e0, e0_t, e1, e1_t], [f0, f1]
