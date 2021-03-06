import itertools
import copy as c
import geometry.joint_holes
reload (geometry.joint_holes)
from geometry.joint_holes import JointHoles

global default_f_args_set
default_f_args_set = [[100, 50, 40, True, False, False], [100, 500, .2, 30, 70, .5, 50, 150, .3, False, True, False]]

class LocalNetwork(object):

    def __init__(self, surfaces, has_v_loop=False, top_priority_v_index=0, parametric = False, type_args = default_f_args_set, start_even = True, flip = False):

        self.has_v_loop = has_v_loop
        self.u_dimension = 1
        self.v_dimension = len(surfaces)
        self.type_args_hole_class = type_args
        self.start_even = start_even

        if parametric:
            self.joint_f_type_add = 3
        else:
            self.joint_f_type_add = 0

        curve_count = int(start_even)

        surfaces[0].instantiate_beams(uneven_start = curve_count % 2)
        self.beams = surfaces[0].beams

        self.u_div = surfaces[0].u_div
        self.v_div = surfaces[0].v_div
        self.global_v_div = self.v_div * self.v_dimension

        if (self.v_dimension > 1):

            for v_index in range(1, self.v_dimension):
                curve_count += self.v_div

                print "curve_count : ", curve_count

                surfaces[v_index].instantiate_beams(uneven_start = curve_count % 2)

                beams = list(surfaces[v_index].beams)

                for i, beam_list in enumerate(beams):

                    self.beams[i].extend(beam_list)

        if flip:
            self.beams.reverse()

        self.dowels = []
        self.joints = []

    def get_flatten_beams(self):

        return list(itertools.chain.from_iterable(self.beams))

    def add_end_seams_connection(self):

        # initzializing which beams to connect
        even_swap = int(self.start_even)

        # v_indexes
        bot_v_val = 0
        top_v_val = int( (self.global_v_div - (self.u_div + 1) % 2) / 2 )

        bot_u_vals = []
        top_u_vals = []
        for i in range(self.u_div):
            # top row u indexes
            if not((i + even_swap) % 2 == 0):
                bot_u_vals.append((i + even_swap) % 2 * i)

            # bot row u indexes
            if not(((i + self.global_v_div - 1 + even_swap) % 2) % 2 == 0):
                top_u_vals.append((i + self.global_v_div - 1 + even_swap) % 2 * i)

        print bot_v_val, bot_u_vals
        print top_v_val, top_u_vals

        bot_beam_pairs = [[self.beams[bot_u_vals[i]][bot_v_val], self.beams[bot_u_vals[i + 1]][bot_v_val]] for i in range(len(bot_u_vals) - 1)]
        top_beam_pairs = [[self.beams[top_u_vals[i]][top_v_val], self.beams[top_u_vals[i + 1]][top_v_val]] for i in range(len(top_u_vals) - 1)]

        print bot_beam_pairs
        print top_beam_pairs

        print "I'm in end seams"

        # the bot_beams:
        for i in range(len(bot_beam_pairs)):
            joint_holes = JointHoles(bot_beam_pairs[i], location_index = 0, type = 6, type_args = [[100, 70, 40, False, False, False], []])
            self.dowels.append(joint_holes.dowel)
            self.joints.append(c.deepcopy(joint_holes))

            print "I did this!"

            joint_holes = JointHoles(bot_beam_pairs[i], location_index = 1, type = 6, type_args = [[100, 70, 40, False, False, False], []])
            self.dowels.append(joint_holes.dowel)
            self.joints.append(c.deepcopy(joint_holes))

            print "And then this!"

        for i in range(len(top_beam_pairs)):
            joint_holes = JointHoles(top_beam_pairs[i], location_index = 2, type = 6, type_args = [[100, 70, 40, False, False, False], []])
            self.dowels.append(joint_holes.dowel)
            self.joints.append(c.deepcopy(joint_holes))

            print "And now also this!"

            joint_holes = JointHoles(top_beam_pairs[i], location_index = 3, type = 6, type_args = [[100, 70, 40, False, False, False], []])
            self.dowels.append(joint_holes.dowel)
            self.joints.append(c.deepcopy(joint_holes))

            print "And now I'm done!"

    def add_foundation_connection(self):
        # initzializing which beams to connect
        even_swap = int(self.start_even)

        # v_indexes
        bot_v_val = 0
        top_v_val = int( (self.global_v_div - (self.u_div + 1) % 2) / 2 )

        bot_u_vals = []
        top_u_vals = []
        for i in range(self.u_div):
            # top row u indexes
            if not((i + even_swap) % 2 == 0):
                bot_u_vals.append((i + even_swap) % 2 * i)

            # bot row u indexes
            if not(((i + self.global_v_div - 1 + even_swap) % 2) % 2 == 0):
                top_u_vals.append((i + self.global_v_div - 1 + even_swap) % 2 * i)

        print bot_v_val, bot_u_vals
        print top_v_val, top_u_vals

        top_beams = [self.beams[top_u_vals[i]][top_v_val] for i in range(len(top_u_vals))]

        self.foundations = []
        for beam in top_beams:
            foundations = [JointHoles([beam], type = 7, type_args = [[], [], [], [250]]).foundations for beam in top_beams]
            self.foundations.extend(foundations)

    def add_three_beams_connection(self):

        beams = []
        for tmp in self.beams:
                beams.append(list(tmp))

        if self.has_v_loop:
            for tmp in beams:
                tmp.append(tmp[0])

        for i in range(len(beams) - 2):

            left_beams   = beams[i]
            middle_beams = beams[i + 1]
            right_beams  = beams[i + 2]

            case_1 = (not self.start_even and i % 2 == 1) or (self.start_even and i % 2 == 0)

            if case_1:

                for j in range(len(left_beams)):

                    if j < len(middle_beams):
                        left   = left_beams[j]      #    _____
                        middle = middle_beams[j]    # _____
                        right  = right_beams[j]     #    _____

                        joint_holes = JointHoles([left, middle, right], 0, self.joint_f_type_add, type_args = self.type_args_hole_class)
                        self.dowels.append(joint_holes.dowel)
                        self.joints.append(c.deepcopy(joint_holes))

                    if j > 0:
                        left   = left_beams[j]      # _____
                        middle = middle_beams[j-1]  #    _____
                        right  = right_beams[j]     # _____

                        joint_holes = JointHoles([left, middle, right], 1, self.joint_f_type_add, type_args = self.type_args_hole_class)
                        self.dowels.append(joint_holes.dowel)
                        self.joints.append(c.deepcopy(joint_holes))

            else:

                for j in range(len(left_beams)):

                    left   = left_beams[j]      #    _____
                    middle = middle_beams[j]    # _____
                    right  = right_beams[j]     #    _____

                    joint_holes = JointHoles([left, middle, right], 1, self.joint_f_type_add, type_args = self.type_args_hole_class)
                    self.dowels.append(joint_holes.dowel)
                    self.joints.append(c.deepcopy(joint_holes))

                    if j < len(middle_beams) - 1:

                        left   = left_beams[j]      # _____
                        middle = middle_beams[j+1]  #    _____
                        right  = right_beams[j]     # _____


                        joint_holes = JointHoles([left, middle, right], 0, self.joint_f_type_add, type_args = self.type_args_hole_class)
                        self.dowels.append(joint_holes.dowel)
                        self.joints.append(c.deepcopy(joint_holes))

    def add_two_beams_connection(self):

        beams = []
        for tmp in self.beams:
            beams.append(list(tmp))

        if self.has_v_loop:
            for tmp in beams:
                tmp.append(tmp[0])

        # starting side

        left_beams  = beams[0]
        right_beams = beams[1]

        for i in range(max(len(left_beams), len(right_beams))):

            if  self.start_even and len(left_beams) > i and  len(right_beams) > i:
                left  = left_beams[i]           # _____
                right = right_beams[i]          #    _____

                joint_holes = JointHoles([left, right], 1, 1 + self.joint_f_type_add, type_args = self.type_args_hole_class)
                self.dowels.append(joint_holes.dowel)
                self.joints.append(c.deepcopy(joint_holes))

            if not self.start_even and len(right_beams) > i + 1:

                    left  = left_beams[i]
                    right = right_beams[i+1]

                    joint_holes = JointHoles([left, right], 1, 1 + self.joint_f_type_add, type_args = self.type_args_hole_class)
                    self.dowels.append(joint_holes.dowel)
                    self.joints.append(c.deepcopy(joint_holes))

            if self.start_even and len(left_beams) > i + 1:

                    left  = left_beams[i+1]     #    _____
                    right = right_beams[i]      # _____

                    joint_holes = JointHoles([left, right], 0, 1 + self.joint_f_type_add, type_args = self.type_args_hole_class)
                    self.dowels.append(joint_holes.dowel)
                    self.joints.append(c.deepcopy(joint_holes))

            if not self.start_even and len(left_beams) > i and  len(right_beams) > i:

                    left  = left_beams[i]
                    right = right_beams[i]

                    joint_holes = JointHoles([left, right], 0, 1 + self.joint_f_type_add, type_args = self.type_args_hole_class)
                    self.dowels.append(joint_holes.dowel)
                    self.joints.append(c.deepcopy(joint_holes))

        # ending side

        right_beams = beams[-1]
        left_beams  = beams[-2]

        flipped = (self.u_div * self.u_dimension) % 2 == 1

        if not flipped and not self.start_even:
            flipped = True

        for i in range(max(len(left_beams), len(right_beams))):

            if not flipped and len(left_beams) > i and  len(right_beams) > i:
                print(1)
                left  = left_beams[i]           # _____
                right = right_beams[i]          #    _____

                joint_holes = JointHoles([left, right], 0, 2 + self.joint_f_type_add, type_args = self.type_args_hole_class)
                self.dowels.append(joint_holes.dowel)
                self.joints.append(c.deepcopy(joint_holes))

            if flipped and len(right_beams) > i + 1:
                    print(2)

                    left  = left_beams[i]
                    right = right_beams[i+1]

                    joint_holes = JointHoles([left, right], 0, 2 + self.joint_f_type_add, type_args = self.type_args_hole_class)
                    self.dowels.append(joint_holes.dowel)
                    self.joints.append(c.deepcopy(joint_holes))

            if not flipped and len(left_beams) > i + 1:

                    left  = left_beams[i+1]     #    _____
                    right = right_beams[i]      # _____

                    joint_holes = JointHoles([left, right], 1, 2 + self.joint_f_type_add, type_args = self.type_args_hole_class)
                    self.dowels.append(joint_holes.dowel)
                    self.joints.append(c.deepcopy(joint_holes))

            if flipped and len(left_beams) > i and  len(right_beams) > i:

                    left  = left_beams[i]
                    right = right_beams[i]

                    joint_holes = JointHoles([left, right], 1, 2 + self.joint_f_type_add, type_args = self.type_args_hole_class)
                    self.dowels.append(joint_holes.dowel)
                    self.joints.append(c.deepcopy(joint_holes))
