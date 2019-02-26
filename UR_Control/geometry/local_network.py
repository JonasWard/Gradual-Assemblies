from geometry.joint_holes import JointHoles
import itertools

class LocalNetwork(object):

    def __init__(self, surface_network, has_loop=False, top_priority_v_index=0):

        self.beams = []
        self.has_loop = has_loop
        self.u_div = surface_network[0][0].u_div
        self.v_div = surface_network[0][0].v_div
        self.flipped = top_priority_v_index % 2
        self.u_dimension = len(surface_network)
        self.v_dimension = len(surface_network[0])

        for v_index, v_sequence in enumerate(surface_network):

            beams_2d = []

            for u_index, surface in enumerate(v_sequence):

                will_flip = True if (top_priority_v_index - u_index) % 2 == 1 else False

                surface.instantiate_beams(will_flip)

                beams = list(surface.beams)

                if len(beams_2d) == 0:

                    beams_2d = list(beams)

                else:

                    for src_beams, new_beams in zip(beams_2d, beams):

                        src_beams.extend(new_beams)
                
            self.beams.extend(beams_2d)


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

            case_1 = (not self.flipped and i % 2 == 0) or (self.flipped and i % 2 == 1)

            if case_1:

                for j in range(len(left_beams)):

                    if j < len(middle_beams):
                        left   = left_beams[j]      #    _____
                        middle = middle_beams[j]    # _____
                        right  = right_beams[j]     #    _____

                        joint_holes = JointHoles([left, middle, right], 0)
                        dowels.append(joint_holes.dowel)

                    if j > 0:

                        left   = left_beams[j]      # _____
                        middle = middle_beams[j-1]  #    _____
                        right  = right_beams[j]     # _____

                        joint_holes = JointHoles([left, middle, right], 1)
                        dowels.append(joint_holes.dowel)

            else:

                for j in range(len(left_beams)):

                    left   = left_beams[j]      #    _____
                    middle = middle_beams[j]    # _____
                    right  = right_beams[j]     #    _____

                    joint_holes = JointHoles([left, middle, right], 1)
                    dowels.append(joint_holes.dowel)

                    if j < len(middle_beams) - 1:

                        left   = left_beams[j]      # _____
                        middle = middle_beams[j+1]  #    _____
                        right  = right_beams[j]     # _____


                        joint_holes = JointHoles([left, middle, right], 0)
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

        for i in range(max(len(left_beams), len(right_beams))):

            #   |
            # |-|
            # |

            if not self.flipped and len(left_beams) > i and  len(right_beams) > i:
                left  = left_beams[i]
                right = right_beams[i]

                joint_holes = JointHoles([left, right], 1, 1)
                dowels.append(joint_holes.dowel)

            if self.flipped and len(right_beams) > i + 1:

                    left  = left_beams[i]
                    right = right_beams[i+1]

                    joint_holes = JointHoles([left, right], 1, 1)
                    dowels.append(joint_holes.dowel)

            # |
            # |-|
            #   |
            if not self.flipped and len(left_beams) > i + 1:

                    left  = left_beams[i+1]
                    right = right_beams[i]

                    joint_holes = JointHoles([left, right], 0, 1)
                    dowels.append(joint_holes.dowel)

            if self.flipped and len(left_beams) > i and  len(right_beams) > i:

                    left  = left_beams[i]
                    right = right_beams[i]

                    joint_holes = JointHoles([left, right], 0, 1)
                    dowels.append(joint_holes.dowel)

        # ending side

        right_beams = beams[-1]
        left_beams  = beams[-2]

        flipped = ((self.u_div + 1) * self.u_dimension) % 2 == 1

        if not flipped and self.flipped:
            flipped = True

        for i in range(max(len(left_beams), len(right_beams))):

            #   |
            # |-|
            # |

            if not flipped and len(left_beams) > i and  len(right_beams) > i:
                print(1)
                left  = left_beams[i]
                right = right_beams[i]
        
                joint_holes = JointHoles([left, right], 0, 2)
                dowels.append(joint_holes.dowel)

            if flipped and len(right_beams) > i + 1:
                    print(2)

                    left  = left_beams[i]
                    right = right_beams[i+1]

                    joint_holes = JointHoles([left, right], 0, 2)
                    dowels.append(joint_holes.dowel)

            # |
            # |-|
            #   |
            if not flipped and len(left_beams) > i + 1:

                    left  = left_beams[i+1]
                    right = right_beams[i]

                    joint_holes = JointHoles([left, right], 1, 2)
                    dowels.append(joint_holes.dowel)

            if flipped and len(left_beams) > i and  len(right_beams) > i:

                    left  = left_beams[i]
                    right = right_beams[i]

                    joint_holes = JointHoles([left, right], 1, 2)
                    dowels.append(joint_holes.dowel)

        return dowels