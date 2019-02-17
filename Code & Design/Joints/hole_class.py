# class that generates connections between beams

import sys
sys.path.append("/Users/jonas/Dropbox/0.dfab/Trimester 2/Project I - Gradual Assemblies/Gradual-Assemblies/UR_Control")
import geometry.beam as beam

import Rhino.Geometry as rg

class Hole(object):
    """ Hole class that defines some hole positions baded on a beam """
    def __init__(self, beam, locations = [0, 1], type = 0, type_arguments = []):
        """ initialization

            :param beam:            Beam that's being considered
            :param locations:       Iterable list containg the locations on the beam where you expect to need holes, based on the t_parameter on the line_repr of the beam (default = [0, 1])
            :param type:            Topological type of the joint (default = 0)
            :param type_arguments:  Iterable list containing parametrs defining the position of the joint holes in relationship to the joint type
        """

        self.beam = beam
        self.type = type
        self.locs = locations
        self.type_args = type_parameters

        self.__type_definitions()
        if(self.type_completed_flag):
            pass
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

            if not(len(self.type_args) == type_input_count):
                self.error_message = ''.join(["You should've given ", str(type_input_count), " values, but you only gave ", str(len(self.type_args)))
                self.type_completed_flag = False

            else
                self.type_completed_flag = True
                x0_ext, cover_h, x1_ext, symmetry_flag, invert_flag = type_parameters
                unit_x = beam.base_plane.XAxis
                unit_y = beam.base_plane.YAxis
                # setting directions according to flags
                if (summetry_flag):
                    v1_switch = -1
                else:
                    v1_switch = 1

                if (invert_flag):
                    v2_switch = -1
                else:
                    v2_switch = 1

                self.vec_0 = rg.Vector3d(unit_x) * x0_ext
                self.vec_1 = rg.Vector3d(unit_y) * (beam.dx / 2 - cover_h) * v1_switch
                self.vec_2_a = rg.Vector3d(unit_x) * x1_ext
                self.vec_2_b = v1_switch * self.vec_2_a

                self.beam_extension_l = x0_ext + x1_ext

    def type_transform(self, point):
        """ method that returns the joint points at a certain point on the beam

            :param point:   The point on the beam to consider.
            :return:        The beam hole locations & reference points.

        """
        if (self.type == 0):
            local_point = rg.Point3d(point)

            # translating to the mid_points
            mv_0 = rg.Transform.Translation(self.vec_0)
            mv_1 = rg.Transform.Translation(-self.vec_0)
            mid_0 = rg.Point3d(local_point).Transform(mv_0)
            mid_1 = rg.Point3d(local_point).Transform(mv_1)

            # translating to the end_points set_0
            v_top = self.vec_1 + self.vec_2_a
            v_bottom = - v_top
            mv_0 = rg.Transform.Translation(v_top)
            mv_1 = rg.Transform.Translation(v_bottom)
            top_0 = rg.Point3d(mid_0).Transform(mv_0)
            bot_0 = rg.Point3d(mid_0).Transform(mv_1)

            # translating to the end_points set_1
            v_top = self.vec_1 + self.vec_2_b
            v_bottom = - v_top
            mv_0 = rg.Transform.Translation(v_top)
            mv_1 = rg.Transform.Translation(v_bottom)
            top_1 = rg.Point3d(mid_1).Transform(mv_0)
            bot_1 = rg.Point3d(mid_1).Transform(mv_1)

            return [[local_point],[top_0, mid_0, bot_0],[top_1, mid_1, bot_1]]

    def __joint_point_calculation(self):
        """ Internal method that executes the joint_point_calculations """
        local_line = self.beam.get_baseline()
        b_pts = []
        joint_pts = []
        for t_val in self.locs:
            b_pt = local_line.PointAt(t_val)
            b_pts.append(b_pt)
            joint_pts.append(type_transform(b_pt))
