# simple brick_stack class


class BrickStack(object):
    """
    Simple Timber Assemblies class that allows for simple relational operations
    on a beam_network that behaves as if it were a Beam Stack.
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

    def get_mid_part(self):
        """ Returns the triple beam relations in middle of the system """
