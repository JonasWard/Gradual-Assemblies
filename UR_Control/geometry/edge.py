# definition of U and V
class Direction(object):

    def __init__(self, direction):

        self.direction = direction

U = Direction('u')
V = Direction('v')

# definition of U0, U1, V0, V1 as the edges of surfaces
class Edge(object):

    def __init__(self, direction, value):

        self.direction = direction
        self.value = value

U0 = Edge(U, 0)
U1 = Edge(U, 1)
V0 = Edge(V, 0)
V1 = Edge(V, 1)

class SurfaceJointProperites(object):
    """ Class that constrols the variables that inform the joint design within a surface

    type = 0 (regular triple_dowel) -> default types, takes the args - :
        x0_ext          - first shift along the beams axis, resulting into a new middle point
        cover_h         - how much the second point should lay underneath the edge of the beam
        x1_ext          - second shfit along the beams axis, resulting into the new top (or bottom) point
        symmetry_flag   - whether the dowel hole connections are axis symmetrical (True) or point symmetrical (False)
        invert_flag     - whether the direction should be inverted or not
        fit_line_flag   - whether you consider the middle beam as well or not (default = False)

    type = 1 (parametric triple_dowel first function) - takes the diagonals lengths of the overlap diamond and the distance between beams as parameters
        x0_ext_min      - min range x0_ext
        x0_ext_max      - max range x0_ext
        x0_var_par      - parameter that influences the development of the x0_ext range
        cover_h_min     - min range cover_h
        cover_h_max     - max range cover_h
        cover_h_par     - parameter that influences the development of the cover_h range
        x1_ext_min      - min range x1_ext
        x1_ext_max      - max range x1_ext
        x1_ext_par      - parameter that influences the development of the x1_ext range
        symmetry_flag   - whether the dowel hole connections are axis symmetrical (True) or point symmetrical (False)
        invert_flag     - whether the direction should be inverted or not
        fit_line_flag   - whether you consider the middle beam as well or not (default = False)

    type = 2 (parametric triple_dowel second function) - takes the diagonals lengths of the overlap diamond and the distance between beams as parameters
        p_a             - point spacing control
        p_b             - point spacing control
        p_c             - point spacing control
        p_d             - point spacing control
        offset          - how much the diamond get's offsetted

    """

    def __init__(self):
        # setting the default values
        self.f_0 = [40, 20, 20, True, False, False]
        self.f_1 = [100, 500, .2, 30, 70, .5, 50, 150, .3, False, True, False]
        self.f_2 = [0.2, 0.3, 0.5, 0.6, ]

    def set_function_0(self):
        pass
