# simple brick_stack class
# BeamNetworks

class BrickStack(object):
    """
    Simple Timber Assemblies class that allows for simple relational operations
    on a beam_network that behaves as if it were a Beam Stack.

    A keystone itself also follows this logic!
    """

    def __init__(self, beam_network, loop = False, start_value = 0):
        """
        Simplest Timbers Assemblies class, is basically a 2D nested list

        :param beam_network:    Input beam_network
        :param loop:            Whether the stack touches itself
        """

        self.start_value = start_value

        self.u_dimension =      # should be set some how - inherented from the network
        self.v_dimension =      # should be set some how - inherented from the network

    def get_top_row(self):
        """ Returns the double beam relations in top row of the stack """

    def get_bottom_row(self):
        """ Returns the double beam relations in bottom row of the stack """

    def get_main(self):
        """ Returns the triple beam relations in middle of the system """

    def get_side_left(self):
        """ Returns the beam relations on the left side """

    def get_right_side(self):
        """ Returns the beam relations on the right side """


class Patch(object):
    """
    More complex beam relation pattern, resulting from patchign a keystone

    Can be partly a patch, should mostly be following a branchign logic.
    """

    def __init__(self, keystone_network):
        """
        Simplest Timbers Assemblies class, is basically a 2D nested list

        :param beam_network:    Input beam_network
        :param loop:            Whether the stack touches itself
        """

    def get_main(self):
        """ Returns the triple beam relations in middle of the system """

    def get_ovelap(self):
        """ Returns the branch relations with neighbouring surface """
