import numpy as np


def split_half_edge(edge, position):
    """Split edge into two edges by a point"""
    if edge.is_outer:
        return [], [], []

    # auto-detect types
    Point = type(edge.ori)
    Edge = type(edge)
    Face = type(edge.face)

    v_cut = Point(position)
    e_new = Edge(v_cut, edge.to)
    e_new_t = Edge(edge.to, v_cut)
    v_diag, v_diag_t = edge.diagonal_vertex, edge.twin.diagonal_vertex

    e0, e0_t = Edge(v_cut, v_diag), Edge(v_diag, v_cut)
    e1, e1_t = Edge(v_diag_t, v_cut), Edge(v_cut, v_diag_t)
    f0, f1 = Face(), Face()

    # set properties[face, twin, prev, next]
    e_new.set_properties(f0, e_new_t, e0_t, edge.next)
    e_new_t.set_properties(f1, e_new, edge.twin.prev, e1_t)
    e0.set_properties(edge.face, e0_t, edge, edge.prev)
    e0_t.set_properties(f0, e0, edge.next, e_new)
    e1.set_properties(edge.twin.face, e1_t, edge.twin.next, edge.twin)
    e1_t.set_properties(
        f1,
        e1,
        e_new_t,
        edge.twin.prev,
    )
    # update existing edges
    edge.next.prev = e_new
    edge.next.next = e0_t
    edge.prev.prev = e0
    edge.twin.prev.next = e_new_t
    edge.twin.prev.prev = e1_t
    edge.twin.next.next = e1

    e_new.is_blocked = edge.is_blocked
    e_new_t.is_blocked = edge.twin.is_blocked

    # set vertices
    v_cut.set_edges([edge, edge.twin, e_new, e_new_t, e0, e0_t, e1, e1_t])
    edge.to.replace_edge(edge, e_new)
    edge.to.replace_edge(edge.twin, e_new_t)
    v_diag.edges.update([e0, e0_t])
    v_diag_t.edges.update([e1, e1_t])

    # update faces
    f0.set_edges([e_new, e0_t, edge.next][::-1])
    f1.set_edges([e_new_t, edge.twin.prev, e1_t][::-1])

    edge.face.replace_edge(edge.next, e0)
    edge.twin.face.replace_edge(edge.twin.prev, e1)

    edge.next.face = f0
    edge.twin.prev.face = f1

    # update edge.next and edge.twin.prev
    edge.twin.ori = v_cut
    edge.twin.prev = e1
    edge.to = v_cut
    edge.next = e0

    # newly added Points, Edges, Faces
    return [v_cut], [e_new, e_new_t, e0, e0_t, e1, e1_t], [f0, f1]


def remove_vertex(vertex):
    n_edges = len(vertex.half_edges)
    if n_edges != 8:
        print(
            f"ERROR: vertex {vertex.vid} has {n_edges} half edges(8 expected)"
        )
        return False

    # print(f"v{vertex.vid}.half: {[e.eid for e in vertex.half_edges]}")

    # 1. Set the edge to keep
    e_keep = min(vertex.half_edges, key=lambda e: e.eid)
    # Ensure it’s oriented correctly
    if e_keep.ori != vertex:
        e_keep = e_keep.twin
    e_keep_t = e_keep.twin

    # 2. Set the twins and edges to delete
    e_del = e_keep.prev.twin.prev
    e_del_t = e_del.twin
    e0 = e_keep.prev
    e1 = e_keep_t.next
    e0_t = e0.twin
    e1_t = e1.twin

    # 3. Update the start/end vertex of the edges
    e_keep.ori = e_del.ori
    e_keep_t.to = e_del.ori
    # vertex
    e_keep.prev = e_del.prev
    e_keep_t.next = e_del_t.next
    # edges
    e_keep.next.next = e_del.prev
    e_keep_t.prev.prev = e_del_t.next

    # 4. Set the faces
    f0, f0_t = e_keep.face, e_del.face
    f1, f1_t = e_keep_t.face, e_del_t.face

    f0.replace_edge(e0, e0_t.next)
    f1.replace_edge(e1, e1_t.prev)

    # edges in deleting faces
    e_del.prev.face = f0
    e_del.prev.next = e_keep
    e_del.prev.prev = e_keep.next
    e_del_t.next.face = f1
    e_del_t.next.next = e_keep_t.prev
    e_del_t.next.prev = e_keep_t

    # 5. Update the vertex
    e0.ori.remove_edges(e0, e0_t)
    e1.to.remove_edges(e1, e1_t)
    e_del.ori.replace_edge(e_del, e_keep)
    e_del.ori.replace_edge(e_del_t, e_keep_t)

    # return the deleted vertices, edges, faces (1v, 6e, 2f)
    return [vertex], [e_del, e_del_t, e0, e0_t, e1, e1_t], [f0_t, f1_t]


def del_edge(edge):
    v_fixed = edge.ori if edge.ori.is_fixed else edge.to
    v_moving = edge.to if edge.ori.is_fixed else edge.ori
    assert v_fixed != v_moving, f"Edge{edge.eid} cannot be deleted"


def projection_on_edge(edge, point):
    """Find the closest position on edge from point"""
    if edge.is_outer:
        return None

    p0, p1 = np.array(edge.ori.xy), np.array(edge.to.xy)
    v = p1 - p0
    w = point - p0

    c1 = w.dot(v)
    if c1 <= 0:
        return p0

    c2 = v.dot(v)
    if c2 <= c1:
        return p1

    b = c1 / c2
    pb = p0 + b * v

    return pb
