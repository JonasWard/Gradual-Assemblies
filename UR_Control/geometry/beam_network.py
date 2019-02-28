from geometry.joint_holes import JointHoles
import itertools
import copy as c

# beam network functions
class BeamNetwork(object):
    def __init__(self, surfaces, start_condition = True, loop = False):
        self.loop = loop
        self.start_condition = start_condition

        self.srfs = surfaces
        self.srf_count = len(self.srfs)
        self.u_div = self.srfs[0].u_div
        self.v_div = self.srfs[0].v_div * self.srf_count

        for i, srf in enumerate(self.srfs):
            srf.div_counter = (i * self.v_div + int(self.start_condition))

    def construct_beam_sets(self):
        self.srfs[0].instantiate_beams()
        self.beam_list = c.deepcopy(self.srfs[0].beams)

        for i in range(1, self.srf_count, 1):
            self.srfs[i].instantiate_beams()
            local_beam_list = c.deepcopy(self.srfs[i].beams)
            for j in range(len(self.beam_list)):
                self.beam_list[j].extend(c.deepcopy(local_beam_list[j]))

        self.dowels = []

    def beam_network(self):
        # first condition, are your list long enough to do anything with?

        if not(self.u_div > 1 and self.v_div > 1):
            print "there are not enough beams in your list to do anything with. "
            joint_operations = False

        elif (self.u_div == 2 or self.v_div == 2):
            print "this is a list with only double-dowel connections! "
            joint_operations = True
            triples = False
            doubles = True
        else:
            print "this is a regular grid. "
            self.triple_joints()
            triples = True

        # if (joint_operations):
        #     # first do all the double joint operations

    def triple_joints(self):

        if self.start_condition:
            a = int(self.start_condition + 1) % 2
            b = int(self.start_condition) % 2
        else:
            a = int(self.start_condition) % 2
            b = int(self.start_condition + 1) % 2

        u_count = self.u_div - 2
        v_count = self.v_div - 1 + int(self.loop)

        for raw_v in range(v_count):
            raw_v = int(raw_v)
            v_list_val_1 = (int( ( raw_v + (raw_v + a) % 2) / 2)) % v_count
            v_list_val_2 = (int( ( raw_v + (raw_v + b) % 2) / 2)) % v_count


            for u in range(u_count):

                type = (u * v_count + raw_v + self.start_condition) % 2

                left_beam = self.beam_list[u][v_list_val_1]
                middle_beam = self.beam_list[u + 1][v_list_val_2]
                right_beam = self.beam_list[u + 2][v_list_val_1]

                joint_holes = JointHoles([left_beam, middle_beam, right_beam], 0, 0)
                self.dowels.append(joint_holes.dowel)

        def doube_joints(beam_list, u_div, v_div, start_condition, loop = False):
            pass
