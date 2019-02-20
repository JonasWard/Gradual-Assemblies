# class that generates connections between beams

import sys

# existing beam class
double_parent = "/Users/jonas/Dropbox/0.dfab/Trimester 2/Project I - Gradual Assemblies/Gradual-Assemblies"
path_to_append = ''.join([double_parent, "/UR_Control"])
sys.path.append(path_to_append)

import geometry.beam as beam
reload(beam)

import Rhino.Geometry as rg

class Hole(object):
    """ Hole class that defines some hole positions baded on a beam """
    def __init__(self, ref_beam, location=0, type=0, type_args=[120, 20, 30, False, False]):
        """ initialization

            :param beam:        Beam that's being considered
            :param locations:   Iterable list or float indicating the t_vals on the beam baseline where you need the holes (default = 0)
            :param type:        Topological type of the joint (default = 0)
            :param type_args:   Iterable list containing parametrs defining the position of the joint holes in relationship to the joint type
        """

        self.beam = ref_beam
        self.beam_line = self.beam.get_baseline()
        self.type = type
        self.locs = location
        self.type_args = type_args

        self.__type_definitions()
        if(self.type_completed_flag):
            self.__joint_point_calculation()
        else:
            print self.error_message

    def __type_definitions(self):
        """ internal method that defines the different joint types

            type = 0 -> default type, takes the args:
                x0_ext          - first shift along the beams axis, resulting into a new middle point
                cover_h         - how much the second point should lay underneath the edge of the beam
                x1_ext          - second shfit along the beams axis, resulting into the new top (or bottom) point
                symmetry_flag   - whether the dowel hole connections are axis symmetrical (True) or point symmetrical (False)
                invert_flag     - whether the direction should be inverted or not
        """
        if (self.type == 0):
            type_input_count = 5

            type_args_count = len(self.type_args)
            if not(type_args_count == type_input_count):
                self.error_message = ''.join(["You should've given ", type_input_count, " values, but you only gave ", type_args_count])
                self.type_completed_flag = False

            else:
                self.type_completed_flag = True
                x0_ext, cover_h, x1_ext, symmetry_flag, invert_flag = self.type_args
                unit_x = self.beam.base_plane.XAxis
                unit_y = self.beam.base_plane.YAxis
                # setting directions according to flags
                if (symmetry_flag):
                    v1_switch = -1
                else:
                    v1_switch = 1

                if (invert_flag):
                    v2_switch = -1
                else:
                    v2_switch = 1

                self.vec_0 = rg.Vector3d(unit_x) * x0_ext
                self.vec_1 = rg.Vector3d(unit_y) * (self.beam.dy / 2 - cover_h) * v1_switch
                self.vec_2_a = rg.Vector3d(unit_x) * x1_ext
                self.vec_2_b = v1_switch * self.vec_2_a

                self.beam_extension_l = x0_ext + x1_ext

    def type_transform(self, point_val):
        """ method that returns the joint points at a certain point on the beam

            :param point:   The t_val of the point on the beam to consider.
            :return:        The beam hole locations & reference points.

        """
        if (self.type == 0):
            local_point = self.beam_line.PointAt(point_val)

            # translating to the mid_points
            mv_0 = rg.Transform.Translation(self.vec_0)
            mv_1 = rg.Transform.Translation(-self.vec_0)
            mid_0, mid_1 = rg.Point3d(local_point), rg.Point3d(local_point)
            mid_0.Transform(mv_0)
            mid_1.Transform(mv_1)

            # translating to the end_points set_0
            v_top = rg.Vector3d(self.vec_1 + self.vec_2_a)
            v_bottom = rg.Vector3d(- v_top)
            mv_0 = rg.Transform.Translation(v_top)
            mv_1 = rg.Transform.Translation(v_bottom)
            top_0, bot_0 = rg.Point3d(mid_0), rg.Point3d(mid_0)
            top_0.Transform(mv_0)
            bot_0.Transform(mv_1)

            # translating to the end_points set_1
            v_top = self.vec_1 + self.vec_2_b
            v_bottom = - v_top
            mv_0 = rg.Transform.Translation(v_top)
            mv_1 = rg.Transform.Translation(v_bottom)
            top_1, bot_1 = rg.Point3d(mid_1), rg.Point3d(mid_1)
            top_1.Transform(mv_0)
            bot_1.Transform(mv_1)

            hole_list = [[local_point], [top_0, mid_0, bot_0], [top_1, mid_1, bot_1]]
            return hole_list

    def __joint_point_calculation(self):
        """ Internal method that executes the joint_point_calculations """
        local_line = self.beam_line
        b_pts = []
        self.joint_pts = []
        if (type(self.locs) == float or type(self.locs) == int):
            b_pt = local_line.PointAt(self.locs)
            b_pts.append(b_pt)
            self.joint_pts = self.type_transform(self.locs)
        elif (type(self.locs) == list):
            for t_val in self.locs:
                b_pt = local_line.PointAt(t_val)
                b_pts.append(b_pt)
                self.joint_pts.append(self.type_transform(self.locs))
