# class that generates connections between beams

import sys

# existing beam class
double_parent = "/Users/jonas/Dropbox/0.dfab/Trimester 2/Project I - Gradual Assemblies/Gradual-Assemblies"
path_to_append = ''.join([double_parent, "/UR_Control"])
sys.path.append(path_to_append)

import geometry.beam as beam
import geometry.dowel as dowel
reload(beam)
reload(dowel)

import Rhino.Geometry as rg

class JointHoles(object):
    """ Hole class that defines some hole positions baded on a beam """
    def __init__(self, beam_set, location_index = None, type = 0, type_args=[120, 20, 30, False, False, False]):
        """ initialization

            :param beam:            Beam that's being considered
            :param location_index:  Index that indicating which t_vals on the beam baseline curve to consider, should take int (default = None)
            :param type_args:       Iterable list containing parametrs defining the position of the joint holes in relationship to the joint type, first value is always the type!
        """

        self.beam_set = beam_set
        self.beam_set_len = len(beam_set)
        self.loc_index = location_index
        self.type = type
        self.type_args = type_args

        self.__type_definitions()
        if(self.type_completed_flag):
            self.__location_mapping()
            self.__joint_point_calculation()
            self.__beam_linking()
        else:
            print self.error_message

    def __location_mapping(self):
        if self.type == 0:
            # the triple joint
            if (self.loc_index == 0) :
                self.t_locs_beam = [1, 0, 1]
                self.dow_pts_i = [[0], [0, 1, 2]]
            elif (self.loc_index == 1):
                self.t_locs_beam = [0, 1, 0]
                self.dow_pts_i = [[1], [0, 1, 2]]
            else:
                print "wrong input, but here's a result anyway (:"
                self.t_locs_beam = [1, 0, 1]
                self.dow_pts_i = [[1], [0, 1, 2]]
        if self.type == 1:
            # the starting naked edge
            if (self.loc_index == 0) :
                self.t_locs_beam = [0, 1]
                self.dow_pts_i = [[0], [1, 2]]
            elif (self.loc_index == 1):
                self.t_locs_beam = [1, 0]
                self.dow_pts_i = [[1], [1, 2]]
            else:
                print "wrong input, but here's a result anyway (:"
                self.t_locs_beam = [1, 0]
                self.dow_pts_i = [[1], [1, 2]]
        if self.type == 2:
            # the end naked edge
            if (self.loc_index == 0) :
                self.t_locs_beam = [1, 0]
                self.dow_pts_i = [[0], [0, 1]]
            elif (self.loc_index == 1):
                self.t_locs_beam = [0, 1]
                self.dow_pts_i = [[1], [0, 1]]
            else:
                print "wrong input, but here's a result anyway (:"
                self.t_locs_beam = [1, 0]
                self.dow_pts_i = [[0], [0, 1]]

    def __beam_linking(self):
        if self.type == 0:
            # the triple joint
            if self.fit_line_flag:
                self.dowel_line = rg.Line.TryFitLineToPoints(self.dowel_pts)
            else:
                self.dowel_line = rg.Line(self.dowel_pts[0], self.dowel_pts[2])
        if (self.type == 1 or self.type == 2):
            # the naked edges
            self.dowel_line = rg.Line(self.dowel_pts[0], self.dowel_pts[1])

        for local_beam in self.beam_set:
            local_dowel = dowel.Dowel(None, self.dowel_line)
            local_beam.add_dowel(local_dowel)
            self.dowel = local_dowel.brep_representation()

    def __type_definitions(self):
        """ internal method that defines the different joint types

            type = 0 -> default type, takes the args:
                x0_ext          - first shift along the beams axis, resulting into a new middle point
                cover_h         - how much the second point should lay underneath the edge of the beam
                x1_ext          - second shfit along the beams axis, resulting into the new top (or bottom) point
                symmetry_flag   - whether the dowel hole connections are axis symmetrical (True) or point symmetrical (False)
                invert_flag     - whether the direction should be inverted or not
                fit_line_flag   - whether you consider the middle beam as well or not (default = False)
        """
        if (self.type == 0):
            type_input_count = 6

            type_args_count = len(self.type_args)
            if not(type_args_count == type_input_count):
                self.error_message = ''.join(["You should've given ", str(type_input_count), " values, but you only gave ", str(type_args_count)])
                self.type_completed_flag = False

            else:
                self.type_completed_flag = True
                x0_ext, cover_h, x1_ext, symmetry_flag, invert_flag, self.fit_line_flag = self.type_args

                if (symmetry_flag):
                    self.v1_sw = -1
                else:
                    self.v1_sw = 1

                if (invert_flag):
                    self.v2_sw = -1
                else:
                    self.v2_sw = 1

                self.translation_variables = [x0_ext, cover_h, x1_ext]
        if (self.type == 1 or self.type == 2):
            type_input_count = 6

            type_args_count = len(self.type_args)
            if not(type_args_count == type_input_count):
                self.error_message = ''.join(["You should've given ", str(type_input_count), " values, but you only gave ", str(type_args_count)])
                self.type_completed_flag = False

            else:
                self.type_completed_flag = True
                x0_ext, cover_h, x1_ext, symmetry_flag, invert_flag, self.fit_line_flag = self.type_args

                if (symmetry_flag):
                    self.v1_sw = -1
                else:
                    self.v1_sw = 1

                if (invert_flag):
                    self.v2_sw = -1
                else:
                    self.v2_sw = 1

                self.translation_variables = [x0_ext, cover_h, x1_ext]

    def __transformation_vecs(self, local_beam):
        if (self.type < 3):
            unit_x = local_beam.base_plane.XAxis
            unit_y = local_beam.base_plane.YAxis

            x0_ext, cover_h, x1_ext = self.translation_variables
            # setting directions according to flags

            x1_ext *= self.v2_sw

            vec_0 = rg.Vector3d(unit_x) * x0_ext
            vec_1 = rg.Vector3d(unit_y) * (local_beam.dy / 2 - cover_h) * self.v1_sw
            vec_2_a = rg.Vector3d(unit_x) * x1_ext
            vec_2_b = self.v1_sw * vec_2_a

            beam_extension_l = x0_ext + x1_ext
            local_beam.extend(beam_extension_l)

            return vec_0, vec_1, vec_2_a, vec_2_b

    def type_hole_pt_transform(self, beam_index):
        """ method that returns the joint points at a certain point on the beam

            :param beam_index:  The index of the beam to consider.
            :return:            The beam hole locations.

        """
        if (self.type < 3):
            vec_0, vec_1, vec_2_a, vec_2_b = self.__transformation_vecs(self.beam_set[beam_index])
            t_val = self.t_locs_beam[beam_index]
            beam_line = self.beam_set[beam_index].get_baseline()
            local_point = beam_line.PointAt(t_val)

            # translating to the mid_points
            mv_0 = rg.Transform.Translation(vec_0)
            mv_1 = rg.Transform.Translation(-vec_0)
            mid_0, mid_1 = rg.Point3d(local_point), rg.Point3d(local_point)
            mid_0.Transform(mv_0)
            mid_1.Transform(mv_1)

            # translating to the end_points set_0
            v_top = rg.Vector3d(vec_1 + vec_2_a)
            v_bottom = rg.Vector3d(- v_top)
            mv_0 = rg.Transform.Translation(v_top)
            mv_1 = rg.Transform.Translation(v_bottom)
            top_0, bot_0 = rg.Point3d(mid_0), rg.Point3d(mid_0)
            top_0.Transform(mv_0)
            bot_0.Transform(mv_1)

            # translating to the end_points set_1
            v_top = vec_1 + vec_2_b
            v_bottom = - v_top
            mv_0 = rg.Transform.Translation(v_top)
            mv_1 = rg.Transform.Translation(v_bottom)
            top_1, bot_1 = rg.Point3d(mid_1), rg.Point3d(mid_1)
            top_1.Transform(mv_0)
            bot_1.Transform(mv_1)

            hole_list = [[top_0, mid_0, bot_0], [top_1, mid_1, bot_1]]
            return hole_list

    def __joint_point_calculation(self):
        """ Internal method that executes the joint_point_calculations """
        self.dowel_pts = []
        for i in range(self.beam_set_len):
            loc_hole_pts = self.type_hole_pt_transform(i)
            loc_dowel_pt = loc_hole_pts[self.dow_pts_i[0]][self.dow_pts_i[i]]
            self.dowel_pts.append(loc_dowel_pt)
