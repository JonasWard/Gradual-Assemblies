from geometry.surface import Surface
from geometry.local_network import LocalNetwork
from geometry.shared_edge import SharedEdge

class GlobalNetwork(object):

    def __init__(self, surfaces, u_div=3, v_div=5, offset_value=20):

        self.surfaces = [Surface(s, u_div, v_div, offset_value) for s in surfaces]

        print [srf.beams for srf in self.surfaces]

        u_shared_edges, v_shared_edges = SharedEdge.generate(self.surfaces)
        self.u_shared_edges = u_shared_edges
        self.v_shared_edges = v_shared_edges

        ###
        ### find sequences
        ###

        if len(self.u_shared_edges) == 0:

            u_sequence_list = []

        else:

            u_pairs = self.u_shared_edges[0]
            u_sequence_list = [[u_pairs.surface_2, u_pairs.surface_1]]

            u_shared_edges = list(u_shared_edges)[1:]

            while u_shared_edges:

                found_pair = False

                for i, shared_edge in enumerate(u_shared_edges):

                    left, right = shared_edge.surface_2, shared_edge.surface_1

                    for sequence in u_sequence_list:

                        index = sequence.index(left) if left in sequence else -1

                        if index > -1:

                            if not right in sequence:
                                sequence.insert(index + 1, right)
                            found_pair = True

                        index = sequence.index(right) if right in sequence else -1

                        if index > -1:

                            if not left in sequence:
                                sequence.insert(index, left)
                            found_pair = True

                        if found_pair:
                            break

                    if found_pair:
                        del u_shared_edges[i]
                        break

                if not found_pair and u_shared_edges:

                    shared_edge = u_shared_edges[0]
                    left, right = shared_edge.surface_2, shared_edge.surface_1
                    u_sequence_list.append([left, right])

                    u_shared_edges = u_shared_edges[1:]


        if len(self.v_shared_edges) == 0:

            v_sequence_list = []

        else:

            v_pairs = self.v_shared_edges[0]
            v_sequence_list = [[v_pairs.surface_2, v_pairs.surface_1]]

            v_shared_edges = list(v_shared_edges)[1:]

            while v_shared_edges:

                found_pair = False

                for i, shared_edge in enumerate(v_shared_edges):

                    bottom, top = shared_edge.surface_2, shared_edge.surface_1

                    for sequence in v_sequence_list:

                        index = sequence.index(bottom) if bottom in sequence else -1

                        if index > -1:

                            if not top in sequence:
                                sequence.insert(index + 1, top)
                            found_pair = True

                        index = sequence.index(top) if top in sequence else -1

                        if index > -1:

                            if not bottom in sequence:
                                sequence.insert(index, bottom)
                            found_pair = True

                        if found_pair:
                            break

                    if found_pair:
                        del v_shared_edges[i]
                        break

                if not found_pair and v_shared_edges:

                    shared_edge = v_shared_edges[0]
                    bottom, top = shared_edge.surface_2, shared_edge.surface_1
                    v_sequence_list.append([bottom, top])

                    v_shared_edges = v_shared_edges[1:]

        uv_pairs = []
        pair_index_list = []

        for i, v_sequence_1 in enumerate(v_sequence_list):

            for j, v_sequence_2 in enumerate(v_sequence_list[i+1:]):

                surface_1 = v_sequence_1[0]
                surface_2 = v_sequence_2[0]

                for shared_edge in surface_1.shared_edges:

                    if shared_edge.surface_1 == surface_1 and \
                        shared_edge.surface_2 == surface_2:

                            uv_pairs.append([v_sequence_2, v_sequence_1])
                            pair_index_list.extend([i, i + 1 + j])

                    if shared_edge.surface_1 == surface_2 and \
                        shared_edge.surface_2 == surface_1:

                            uv_pairs.append([v_sequence_1, v_sequence_2])
                            pair_index_list.extend([i, i + 1 + j])

        pair_index_list = list(reversed(list(set(pair_index_list))))

        # the surfaces which have no connection toward u-direction
        no_pairs = list(v_sequence_list)
        for pair_index in pair_index_list:
            del no_pairs[pair_index]

        surface_networks = [uv_pairs[0]] if len(uv_pairs) > 0 else []
        uv_pairs = uv_pairs[1:]

        while uv_pairs:

            for i, pair in enumerate(uv_pairs):

                found_pair = False

                for surface_network in surface_networks:

                    if surface_network[-1][0] == pair[0][0]:

                        surface_network.append(pair[1])

                        del uv_pairs[i]
                        found_pair = True
                        break

                if found_pair:
                    break

            if not found_pair and uv_pairs:
                surface_networks.append(uv_pairs[0])
                uv_pairs = uv_pairs[1:]

        for no_pair in no_pairs:

            surface_networks.append([no_pair])

        # in case only feeding single surfaces
        if len(surface_networks) == 0:
            for s in self.surfaces:
                surface_networks.append([[s]])

        self.local_networks = []

        for surface_network in surface_networks:

            if len(surface_network) > 1 and surface_network[0][0] == surface_network[-1][0]:

                has_loop = True
                surface_network = surface_network[:-1]

            else:

                has_loop = False

            local_network = LocalNetwork(surface_network, has_loop)
            self.local_networks.append(local_network)
