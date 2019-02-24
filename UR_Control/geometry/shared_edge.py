from geometry.edge import *

class SharedEdge(object):

    def __init__(self, surface_1, surface_2, edge_1, edge_2):

        self.surface_1 = surface_1
        self.surface_2 = surface_2
        self.edge_1 = edge_1
        self.edge_2 = edge_2

    @staticmethod
    def generate(surfaces):

        u_shared_edges, v_shared_edges = [], []

        THRESHOLD = 1.0

        for i, s1 in enumerate(surfaces):

            for s2 in surfaces[i+1:]:

                if s1.top_pt.DistanceTo(s2.bottom_pt) < THRESHOLD:

                    shared_edge = SharedEdge(s2, s1, V0, V1)
                    v_shared_edges.append(shared_edge)

                elif s1.bottom_pt.DistanceTo(s2.top_pt) < THRESHOLD:

                    shared_edge = SharedEdge(s1, s2, V0, V1)
                    v_shared_edges.append(shared_edge)

                elif s1.right_pt.DistanceTo(s2.left_pt) < THRESHOLD:

                    shared_edge = SharedEdge(s2, s1, U0, U1)
                    u_shared_edges.append(shared_edge)

                elif s1.left_pt.DistanceTo(s2.right_pt) < THRESHOLD:

                    shared_edge = SharedEdge(s1, s2, U0, U1)
                    u_shared_edges.append(shared_edge)

                else:

                    continue

                s1.shared_edges.append(shared_edge)
                s2.shared_edges.append(shared_edge)

        return list(set(u_shared_edges)), list(set(v_shared_edges))