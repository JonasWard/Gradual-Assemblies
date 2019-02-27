# class that generates connections between beams

import sys

import copy as c
import geometry.beam as beam
import geometry.dowel as dowel

import Rhino.Geometry as rg

class JointHoles(object):
    """ Hole class that defines some hole positions baded on a beam """
    def __init__(self, beam_set, location_index = None, type = 0, type_args=[[40, 20, 20, True, False, False], [100, 500, .2, 30, 70, .5, 50, 150, .3, False, True, False]]):
        """ initialization

            :param beam:            Beam that's being considered
            :param location_index:  Index that indicating which t_vals on the beam baseline curve to consider, should take int (default = None)
            :param type:            Which join type you are dealin with     0 - simple triple, 1 & 2 left & right ends ; 3 - parametric triple, 4 & 5 left & right ends ; 6 - foundation ; 7 - top; 8  (construction) seams
            :param type_args:       Iterable list containing parametrs defining the position of the joint holes in relationship to the joint type, first value is always the type!
        """

        self.beam_set = beam_set
        self.beam_set_len = len(beam_set)
        self.loc_index = location_index
        self.type = type
        self.type_arg_set = type_args

        self.__type_definitions()
        if(self.type_completed_flag):
            self.__location_mapping()
            self.__parametric_hole_vars_f()
            if self.param_holes_triple_joint:
                self.__triple_joint_optimisation_f()
            self.__joint_point_calculation()
            self.__beam_linking()
        else:
            print self.error_message

    def __type_definitions(self):
        """ internal method that defines the different joint types

            type = 0, 1, 2 -> default types, takes the args:
                x0_ext          - first shift along the beams axis, resulting into a new middle point
                cover_h         - how much the second point should lay underneath the edge of the beam
                x1_ext          - second shfit along the beams axis, resulting into the new top (or bottom) point
                symmetry_flag   - whether the dowel hole connections are axis symmetrical (True) or point symmetrical (False)
                invert_flag     - whether the direction should be inverted or not
                fit_line_flag   - whether you consider the middle beam as well or not (default = False)

            type = 3, 4, 5 -> parametric joint design, variables change based on the input beams (seam logic as before, only setting ranges):
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

            type = 6    -> Foundation type
                I Don't Know

            type = 7    -> End type
                I Don't Know

            type = 8    -> Seam typology
                I Don't Know
        """
        # normal triple dowel
        if (self.type == 0 or self.type == 1 or self.type == 2):
            type_input_count = 6

            self.type_args = self.type_arg_set[0]
            type_args_count = len(self.type_args)
            if not(type_args_count == type_input_count):
                self.type_completed_flag = False

            else:
                self.type_completed_flag = True
                x0_ext, cover_h, x1_ext, symmetry_flag, invert_flag, self.fit_line_flag = self.type_args

                self.translation_variables = [x0_ext, cover_h, x1_ext]

        # parametric triple dowel
        if (self.type == 3 or self.type == 4 or self.type == 5):
            type_input_count = 12

            self.type_args = self.type_arg_set[1]
            type_args_count = len(self.type_args)
            if not(type_args_count == type_input_count):
                self.type_completed_flag = False

            else:
                self.type_completed_flag = True
                self.x0_ext_set = [self.type_args[i] for i in range(3)]
                self.cover_h_set = [self.type_args[i] for i in range(3, 6, 1)]
                self.x1_ext_set = [self.type_args[i] for i in range(6, 9, 1)]
                symmetry_flag, invert_flag, self.fit_line_flag = [self.type_args[i] for i in range(9, 12, 1)]

        # setting the symmetry flags for both all the triple dowel connections
        if (self.type < 6 and self.type_completed_flag):
            if (symmetry_flag):
                self.v1_sw = -1
            else:
                self.v1_sw = 1

            if (invert_flag):
                self.v2_sw = -1
            else:
                self.v2_sw = 1

        # general error message on type generation
        if not(self.type_completed_flag):
            self.error_message = ''.join(["You should've given ", str(type_input_count), " values, but you only gave ", str(type_args_count)])

    def __location_mapping(self):
        """ based on the inputs, these lists indicate which sets of points will be used to use with the dowel generation """
        if (self.type == 0 or self.type == 3):
            # the triple dowel logic
            if (self.loc_index == 1):
                self.t_locs_beam = [1, 0, 1]
                self.dow_pts_i = [[0], [0, 1, 2]]
            elif (self.loc_index == 0):
                self.t_locs_beam = [0, 1, 0]
                self.dow_pts_i = [[1], [0, 1, 2]]
            else:
                print "wrong input, but here's a result anyway (:"
                self.t_locs_beam = [1, 0, 1]
                self.dow_pts_i = [[1], [0, 1, 2]]
        elif (self.type == 1 or self.type == 4):
            # the starting naked edge
            if (self.loc_index == 1):
                self.t_locs_beam = [0, 1]
                self.dow_pts_i = [[0], [1, 2]]
            elif (self.loc_index == 0):
                self.t_locs_beam = [1, 0]
                self.dow_pts_i = [[1], [1, 2]]
            else:
                print "wrong input, but here's a result anyway (:"
                self.t_locs_beam = [1, 0]
                self.dow_pts_i = [[1], [1, 2]]
        elif (self.type == 2 or self.type == 5):
            # the end naked edge
            if (self.loc_index == 1):
                self.t_locs_beam = [1, 0]
                self.dow_pts_i = [[0], [0, 1]]
            elif (self.loc_index == 0):
                self.t_locs_beam = [0, 1]
                self.dow_pts_i = [[1], [0, 1]]
            else:
                print "wrong input, but here's a result anyway (:"
                self.t_locs_beam = [1, 0]
                self.dow_pts_i = [[0], [0, 1]]

        elif (self.type == 6):
            # the foundation logic
            pass

        elif (self.type == 7):
            # the top beams
            pass

        elif (self.type == 8):
            # the seams - flush condition
            pass

        elif (self.type == 9):
            # the seams with I Don't Know
            pass

    def __beam_linking(self):
        """ the actual dowel generation """
        if (self.type == 0 or self.type == 3):
            # the triple joint
            if self.fit_line_flag:
                ignore, self.dowel_line = rg.Line.TryFitLineToPoints(self.dowel_pts)
            else:
                self.dowel_line = rg.Line(self.dowel_pts[0], self.dowel_pts[2])
        if (self.type == 1 or self.type == 2 or self.type == 4 or self.type == 5):
            # the naked edges
            self.dowel_line = rg.Line(self.dowel_pts[0], self.dowel_pts[1])

        for local_beam in self.beam_set:
            local_dowel = dowel.Dowel(None, self.dowel_line)
            local_beam.add_dowel(local_dowel)
            self.dowel = local_dowel

    def __transformation_vecs(self, local_beam):
        if (self.type < 6):
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

    def __triple_dowel_function(self, beam_index):
        """ method that returns the joint points at a certain point on the beam

            :param beam_index:  The index of the beam to consider.
            :return:            The beam hole locations.
        """

        if (self.type < 6):
            # normal joint type hole methods
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
            loc_hole_pts = self.__triple_dowel_function(i)

            loc_dowel_pt = loc_hole_pts[self.dow_pts_i[0][0]][self.dow_pts_i[1][i]]
            self.dowel_pts.append(loc_dowel_pt)

    def __parametric_hole_vars_f(self):
        """ internal method that sets the stage for parametric variation of the hole locations """
        self.param_holes_triple_joint = False

        if (self.type == 3):
            self.param_holes_triple_joint = True
            self.local_middle_beam = self.beam_set[1]
            self.local_other_beams = [self.beam_set[0], self.beam_set[2]]
        if (self.type == 4):
            self.param_holes_triple_joint = True
            self.local_middle_beam = self.beam_set[1]
            self.local_other_beams = [self.beam_set[0]]
        if (self.type == 5):
            self.param_holes_triple_joint = True
            self.local_middle_beam = self.beam_set[0]
            self.local_other_beams = [self.beam_set[1]]

    def __triple_joint_optimisation_f(self):
        """ gets some constraints related to the joint topology """
        if (self.type == 3):
            # triple beam
            mid_index = 1
            other_indexes = [0, 2]
        elif(self.type == 4):
            # left beam
            mid_index = 1
            other_indexes = [0]
        elif (self.type == 5):
            # right beam
            mid_index = 0
            other_indexes = [1]

        # checking if they are not suuuper close to parallel

        pt_count = len(other_indexes)

        middle_beam = c.deepcopy(self.beam_set[mid_index])
        other_beams = [c.deepcopy(self.beam_set[other_index]) for other_index in other_indexes]
        middle_beam.top_bot_line()
        [other_beam.top_bot_line() for other_beam in other_beams]

        v_0 = rg.Vector3d(other_beam.get_baseline().PointAt(1) - other_beam.get_baseline().PointAt(0))
        v_1 = rg.Vector3d(middle_beam.get_baseline().PointAt(1) - middle_beam.get_baseline().PointAt(0))
        v_angle = rg.Vector3d.VectorAngle(v_0, v_1)

        if (v_angle > 1.53 or v_angle < 0.03):
            print "your angle is too small", v_angle

            x0_ext, cover_h, x1_ext = self.x0_ext_set[1], self.cover_h_set[0], self.x1_ext_set[0]
            self.translation_variables = x0_ext, cover_h, x1_ext

        else:
            reference_plane = rg.Plane(middle_beam.base_plane)

            world_xy = rg.Plane.WorldXY
            middle_beam.transform_instance_from_frame_to_frame(reference_plane, world_xy)
            [other_beam.transform_instance_from_frame_to_frame(reference_plane, world_xy) for other_beam in other_beams]

            top_pt, left_pt, right_pt, bot_pt = [rg.Point3d(0, 0, 0) for i in range(4)]

            ref_pt = rg.Point3d(middle_beam.dx * .5, 0, 0)
            for other_beam in other_beams:
                ignore, a, b = rg.Intersect.Intersection.LineLine(middle_beam.top_line, other_beam.top_line)
                top_pt += middle_beam.top_line.PointAt(a)
                ignore, a, b = rg.Intersect.Intersection.LineLine(middle_beam.top_line, other_beam.bot_line)
                left_pt += middle_beam.top_line.PointAt(a)
                ignore, a, b = rg.Intersect.Intersection.LineLine(middle_beam.bot_line, other_beam.top_line)
                right_pt += middle_beam.bot_line.PointAt(a)
                ignore, a, b = rg.Intersect.Intersection.LineLine(middle_beam.bot_line, other_beam.bot_line)
                bot_pt += middle_beam.bot_line.PointAt(a)

            self.pts_set = [top_pt / pt_count, left_pt / pt_count, bot_pt / pt_count, right_pt / pt_count]
            self.pts_set.append(rg.Point3d(self.pts_set[0]))

            self.ref_pt = ref_pt
            self.avg_pt = rg.Point3d((top_pt + left_pt + bot_pt + right_pt) / 4)

            self.diamond = rg.PolylineCurve(self.pts_set)
            self.diamond_offset = self.diamond.Offset(world_xy, -35, .1, rg.CurveOffsetCornerStyle.Sharp)[0]
            self.new_pt_set = [self.diamond_offset.PointAt(self.diamond_offset.ClosestPoint(self.pts_set[i], 1000)[1]) for i in range(4)]

            distance_0 = self.new_pt_set[0].DistanceTo(self.new_pt_set[1])
            distance_1 = self.new_pt_set[2].DistanceTo(self.new_pt_set[3])

            self.transformed_middle_beam = middle_beam
            self.transformed_other_beam = other_beam

            x0_ext = self.x0_ext_set[0] + distance_1 * (self.x0_ext_set[1] - self.x0_ext_set[0]) / self.x0_ext_set[2]
            cover_h = self.cover_h_set[0] + (self.cover_h_set[1] - self.cover_h_set[0]) * self.cover_h_set[2] / distance_0
            x1_ext = self.x1_ext_set[0] + distance_1 * distance_0 * (self.x1_ext_set[1] - self.x1_ext_set[0]) / self.x1_ext_set[2]

            x0_ext, cover_h, x1_ext = self.x0_ext_set[1], self.cover_h_set[0], self.x1_ext_set[0]
            self.translation_variables = [x0_ext, cover_h, x1_ext]

    def __transform_geo_to_xyplane(self, geo, ref_plane, invert = False):
        """
            internal method that tranforms some geometry to the xy_plane

            :param geo:             Input Geometry
            :param ref_plane:       Plane used as a reference
            :param invert:          To ref_plane = True, To xy_plane = False
            :return new_geo:        Geometries that have been transformed
        """
        if (invert):
            plane_0, plane_1 = rg.Plane.WorldXY, ref_plane
        else:
            plane_1, plane_0 = rg.Plane.WorldXY, ref_plane
        trans_matrix = rg.Transform.PlaneToPlane(plane_0, plane_1)
        new_geo = [temp_geo.Transform(trans_matrix) for temp_geo in geo]

        return new_geo
