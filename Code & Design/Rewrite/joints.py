# joint class definitions


class TripleJoint(object):
    """
        Describing the relations and dowel placement between 3 beams.
    """
    def ___init___(self, beam_set, type_def, loc_para = 0):
        """
        Initialization of a triple-joint isinstance

        :param beam_set:        Which beams to consider
        :param type_def:        Type and functions that controle the hole locs.
        :param loc_para:        Where to consider them to be connected (0 or 1)
        """

        self.beam_set = beam_set
        self.joint_type = joint_type
        self.loc_para = loc_para

        self.__location_setting()

    def __location_setting(self):
        """ Internal Method that set's up the location parameters of the beam """
        a = (0 + self.loc_para) % 2
        b = (1 + self.loc_para) % 2
        c = (0 + self.loc_para) % 2

        self.type_loc_para = self.type_def.Triple.locations[a, b, c]

    def get_connections(self):
        """ Internal Method that uses the functions defined in the joint types """
        pt0, pt1, pt2 = self.joint_type.triple_dowel_execution()

class DoubleJoint(object):
    """
        Describing the relations and dowel placement between 2 beams, according
        to the Triple-Dowel-Beam logic.
    """
    def __init__(self, beam_set, joint_type, loc_para = 0, left_or_right = 0):
        """
        Initialization of a double-joint isinstance

        :param beam_set:        Which beams to consider
        :param joint_type:      Type and functions that controle the hole locs.
        :param loc_para:        Where to consider them to be connected (0 or 1)
        :param left_or_right:   Left or right set (0 or 1)
        """

        self.beam_set = beam_set
        self.joint_type = joint_type
        self.loc_para = loc_para
        self.left_or_right = left_or_right

    def __location_setting(self):
        """
        Internal Method that set's up the location parameters of the beam
        """
        # double only logic
        if self.left_or_right:
            # which locations to consider from the type
            self.rel_locations = [(0 + self.loc_para) % 2, (1 + self.loc_para) % 2]
            self.type_loc_para = self.type_def.Triple.locations()

        elif not(self.left_or_right):
            self.rel_locations = [(1 + self.loc_para) % 2, (0 + self.loc_para) % 2]
            self.type_loc_para = self.type_def.Triple.locations(self)

class EndSeams(object):
    """ Class defining the joints at the v-ends of the system """
    def __init__(self, beam_set, location_parameters, joint_type):
        self.left_beam = beam_set[0]
        self.middle_beam = beam_set[1]
        self.right_beam = beam_set[2]
        self.loc_para = location_parameters
        self.joint_type = joint_type

class Foundation(object):
    """ Class defining the joints connecting with the floor """
    def __init__(self, beam_set, location_parameters, joint_type):
        self.left_beam = beam_set[0]
        self.middle_beam = beam_set[1]
        self.right_beam = beam_set[2]
        self.loc_para = location_parameters
        self.joint_type = joint_type
