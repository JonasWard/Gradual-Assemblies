from geometry.joint_holes import JointHoles
import itertools

class LocalNetwork(object):

    def __init__(self, surface_network, has_loop = False, will_reverse=False, type_args=[40, 20, 20, True, False, False]):

        self.beams = []
        self.has_loop = has_loop
        self.u_div = surface_network[0][0].u_div
        self.v_div = surface_network[0][0].v_div
        self.type_args = type_args

        for v_index, v_sequence in enumerate(surface_network):

            beams_2d = []

            for u_index, surface in enumerate(v_sequence):

                vvv = 1 if not will_reverse else 0
                will_flip = True if u_index % 2 == vvv else False

                surface.instantiate_beams(will_flip)

                beams = list(surface.beams)

                if len(beams_2d) == 0:

                    beams_2d = list(beams)

                else:

                    for src_beams, new_beams in zip(beams_2d, beams):

                        src_beams.extend(new_beams)
                
            self.beams.extend(beams_2d)
 
        if will_reverse:
            self.beams = list(reversed(self.beams))


    def get_flatten_beams(self):

        return list(itertools.chain.from_iterable(self.beams))

    def add_three_beams_connection(self):

        dowels = []

        beams = self.beams

        # looping
        if self.has_loop:
            beams.append(beams[0])

        for i in range(len(beams) - 2):

            left_beams   = beams[i]
            middle_beams = beams[i + 1]
            right_beams  = beams[i + 2]

            if i % 2 == 0:

                for j in range(len(left_beams)):

                    if j < len(middle_beams):
                        left   = left_beams[j]      #    _____
                        middle = middle_beams[j]    # _____
                        right  = right_beams[j]     #    _____

                        joint_holes = JointHoles([left, middle, right], 0, type_args=self.type_args)
                        dowels.append(joint_holes.dowel)

                    if j > 0:

                        left   = left_beams[j]      # _____
                        middle = middle_beams[j-1]  #    _____
                        right  = right_beams[j]     # _____

                        joint_holes = JointHoles([left, middle, right], 1, type_args=self.type_args)
                        dowels.append(joint_holes.dowel)

            else:

                for j in range(len(left_beams)):

                    left   = left_beams[j]      #    _____
                    middle = middle_beams[j]    # _____
                    right  = right_beams[j]     #    _____

                    joint_holes = JointHoles([left, middle, right], 1, type_args=self.type_args)
                    dowels.append(joint_holes.dowel)

                    if j < len(middle_beams) - 1:

                        left   = left_beams[j]      # _____
                        middle = middle_beams[j+1]  #    _____
                        right  = right_beams[j]     # _____


                        joint_holes = JointHoles([left, middle, right], 0, type_args=self.type_args)
                        dowels.append(joint_holes.dowel)

        return dowels

    def add_two_beams_connection(self):

        dowels = []

        beams = self.beams

        # looping
        if self.has_loop:

            return dowels

        # starting side

        left_beams  = beams[0]
        right_beams = beams[1]

        for i in range(len(right_beams)):

            left  = left_beams[i]
            right = right_beams[i]

            joint_holes = JointHoles([left, right], 1, 1, type_args=self.type_args)
            dowels.append(joint_holes.dowel)

            if len(left_beams) > i + 1:
                left  = left_beams[i+1]
                right = right_beams[i]

                joint_holes = JointHoles([left, right], 0, 1, type_args=self.type_args)
                dowels.append(joint_holes.dowel)

        # ending side

        right_beams = beams[-1]
        left_beams  = beams[-2]

        is_odd_division = bool(self.u_div % 2)

        for i in range(len(right_beams)):

            left  = left_beams[i]
            right = right_beams[i]

            joint_holes = JointHoles([left, right], 0 if is_odd_division else 1, 2, type_args=self.type_args)
            dowels.append(joint_holes.dowel)

            if len(left_beams) > i + 1:
                left  = left_beams[i+1]
                right = right_beams[i]

                joint_holes = JointHoles([left, right], 1 if is_odd_division else 0, 2, type_args=self.type_args)
                dowels.append(joint_holes.dowel)

        return dowels