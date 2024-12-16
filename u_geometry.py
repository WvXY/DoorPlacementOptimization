import matplotlib.pyplot as plt

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
    p_cut.set_half_edges([edge, edge.twin, e_new, e_new_t, e0, e0_t, e1, e1_t])

    # update faces
    f0.set_half_edges([e_new, e0_t, edge.next][::-1])
    f1.set_half_edges([e_new_t, edge.twin.prev, e1_t][::-1])

    if edge.next.twin is not None:
        f_adj_0 = edge.next.twin.face
        f_adj_0.replace_adj_face(edge.face, f0)
        f0.set_adjs([edge.face, f1, f_adj_0])
    else:
        f0.set_adjs([edge.face, f1])

    if edge.twin.prev.twin is not None:
        f_adj_1 = edge.twin.prev.twin.face
        f_adj_1.replace_adj_face(edge.twin.face, f1)
        f1.set_adjs([edge.twin.face, f0, f_adj_1])
    else:
        f1.set_adjs([edge.twin.face, f0])

    edge.face.replace_edge(edge.next, e0)
    edge.twin.face.replace_edge(edge.twin.prev, e1)

    # update edge.next and edge.twin.prev
    edge.twin.ori = p_cut
    edge.twin.prev = e1
    edge.to = p_cut
    edge.next = e0

    print(f"f0: {f0.fid}, f1: {f1.fid}")
    print(f"f: {edge.face.fid}, f_twin: {edge.twin.face.fid}")

    # newly added Points, Edges, Faces
    return [p_cut], [e_new, e_new_t, e0, e0_t, e1, e1_t], [f0, f1]
