# bugtesting snippet

import copy as c


def __bugtesting_ini(self):
        """ initialization of the variables you need for the bugtesting """

        self.bug_pts = []
        self.bug_lines = []
        self.bug_curves = []
        self.bug_beams = []
        self.bug_surfaces = []
        self.bug_planes = []


def __bugtesting_f(self, pt = None, line = None, curve = None, beam = None, surface = None, plane = None):
    """ method that adds certain values to the buglists
    :param pt:      Points to add (default = None)
    :param line:    Line to add (default = None)
    :param curve:   Curve to add (default = None)
    :param surface: Surface to add (default = None)
    """

    if not(pt is None):
        self.bug_pts.append(c.deepcopy(pt))

    if not(line is None):
        self.bug_lines.append(c.deepcopy(line))

    if not(curve is None):
        self.bug_curves.append(c.deepcopy(curve))

    if not(beam is None):
        self.bug_beams.append(beam.brep_representation())

    if not(surface is None):
        self.bug_surfaces.append(c.deepcopy(surface))

    if not(plane is None):
        self.bug_planes.append(c.deepcopy(plane))
