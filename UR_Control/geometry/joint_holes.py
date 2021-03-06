# class that generates connections between beams

import copy as c
import geometry.beam
reload(geometry.beam)
import geometry.beam as beam
import geometry.dowel as dowel
import math as m

import Rhino.Geometry as rg

class JointHoles(object):
    """ Hole class that defines some hole positions baded on a beam """
    def __init__(self, beam_set, location_index = None, type = 0, type_args=[[40, 20, 20, True, False, False], [100, .5, 40], [250]], overextend = 70):
        """ initialization

            :param beam:            Beam that's being considered
            :param location_index:  Index that indicating which t_vals on the beam baseline curve to consider, should take int (default = None)
            :param type:            Which join type you are dealin with     0 - simple triple, 1 & 2 left & right ends ; 3 - parametric triple, 4 & 5 left & right ends ; 6 - foundation ; 7 - top; 8  (construction) seams
            :param type_args:       Iterable list containing parametrs defining the position of the joint holes in relationship to the joint type, first value is always the type!
            :param overextend:      O
        """

        self.beam_set = beam_set
        self.beam_set_len = len(beam_set)
        self.loc_index = location_index
        self.type = type
        self.type_arg_set = type_args
        self.overextend = overextend

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
                height          - length of the beams away from the floor

            type = 7    -> End type
                I Don't Know

            type = 8    -> Seam typology
                I Don't Know
        """
        # normal triple dowel
        self.type_completed_flag = False

        if (self.type < 6):
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
            type_input_count = 2

            self.type_args = self.type_arg_set[1]
            type_args_count = len(self.type_args)
            # if not(type_args_count == type_input_count):
            #     self.type_completed_flag = False
            #
            # else:
            #     self.type_completed_flag = True
            #     self.x0_ext_set = [self.type_args[i] for i in range(3)]
            #     self.cover_h_set = [self.type_args[i] for i in range(3, 6, 1)]
            #     self.x1_ext_set = [self.type_args[i] for i in range(6, 9, 1)]
            #     symmetry_flag, invert_flag, self.fit_line_flag = [self.type_args[i] for i in range(9, 12, 1)]

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

        

        # settings

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

        local_dowel = dowel.Dowel(None, self.dowel_line)

        for local_beam in self.beam_set:
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
            local_beam.extends(beam_extension_l)

            return vec_0, vec_1, vec_2_a, vec_2_b

    # def __arced_parametric_f(self):
    #     """ Parametric triple dowel function based on the angle between beams and the distance between them  """
    #
    #     # beam set
    #     middle_beam
    #     other_beams
    #
    #     spacing =
    #     dz = middle_beam.dz
    #
    #     # getting shortest distance between the middle beam and the other ones
    #     x0 = spacing / 2.5
    #     y_min = dz * .5 - cover_h
    #     r = (x0_max ** 2 + y_min ** 2) / (2 * y_min)
    #     y_r = r - y_min
    #
    #     # rotation in plane
    #     x,

    def foundation_function(self, beam, ref_pl = rg.Plane.WorldXY, overlap = 250):
        """ foundation connection

        :param beam:        Which beam to consider
        :param loc:         Location of the t-val on the line representation of the beam to use as your reference point
        :param ref_pl:      The plane that will be used as the baseplane of the structure
        :param length:      Length away from the floor
        :param overlap:     How much overlap between the feet of the beam and the beam itself
        """
        
        print "height of the beam: ", beam.dy
        
        # finding the orientation of the beam
        beam_line = beam.get_baseline()
        pt_0, pt_1 = beam_line.PointAt(0), beam_line.PointAt(1)
        z_height_pl = ref_pl.Origin.Z
        
        # determining which side is closest to the floor
        parallel_to_the_world_xy = False
        if (pt_0.Z > pt_1.Z):
            line_start_pt = pt_0
            line_end_pt = pt_1
            negative_direction = False
        elif (pt_1.Z > pt_0.Z):
            line_start_pt = pt_1
            line_end_pt = pt_0
            negative_direction = True
        else:
            # none run condition
            parallel_to_the_world_xy = True
            print "This one can't have a foundation"
            
        if not(parallel_to_the_world_xy):
            # finding the new end_pt of the beam
            t_val = rg.Intersect.Intersection.LinePlane(beam_line, ref_pl)[1]
            extended_line_end_pt_on_ref_pl = beam_line.PointAt(t_val)
            
            # how much the new_end_pt has to be moved upwards (beam.extension is value related to the overlap required in the joint designs)
            print beam.extension
            
            angle = rg.Vector3d.VectorAngle(rg.Vector3d(line_start_pt - line_end_pt), ref_pl.Normal)
            shift_length = m.tan(angle) * beam.dy + beam.extension + beam.end_cover
            print "shift length : ", shift_length

            # constructing the new base_pt
            mv = rg.Vector3d(line_start_pt - line_end_pt)
            mv.Unitize()
            new_line_end_pt = extended_line_end_pt_on_ref_pl + (mv * shift_length)
            
            # new beam origin & length
            print "old beam length: ", beam.dx
            print "new beam length: ", rg.Line(new_line_end_pt, line_start_pt).Length
            beam.reset_length(rg.Line(new_line_end_pt, line_start_pt).Length)
            new_beam_o = rg.Point3d((new_line_end_pt + line_start_pt) / 2)
            
            new_beam_line = rg.Line(new_line_end_pt, line_start_pt)
            
            # finding the 3th point defining the new plane
            projected_pt_on_ref_pl = ref_pl.ClosestPoint(line_start_pt)

            # constructing axises
            x_axis = rg.Vector3d(new_line_end_pt - line_start_pt)
            y_axis = rg.Vector3d(projected_pt_on_ref_pl - line_start_pt)

            # checking angles with original beam_plane
            x_axis_o, y_axis_o = beam.base_plane.XAxis, beam.base_plane.YAxis
            x_angle = rg.Vector3d.VectorAngle(x_axis, x_axis_o)
            y_angle = rg.Vector3d.VectorAngle(y_axis, y_axis_o)

            # flipping if need be
            if (x_angle > 1.6):
                x_axis = - x_axis
            if (y_angle > 1.6):
                y_axis = - y_axis

            # defining the new plane
            beam.base_plane = rg.Plane(new_beam_o, x_axis, y_axis)
    
            # defining the footing beams
            mv = rg.Vector3d(beam.base_plane.ZAxis * beam.dz)
            f_pls = [rg.Plane(beam.base_plane) for i in range(2)]
            [f_pl.Translate(rg.Vector3d( (i *2 - 1) * mv + (new_line_end_pt - new_beam_o))) for i, f_pl in enumerate(f_pls)]
    
            dy_foundation, dz_foundation = rg.Interval(-.5 * beam.dy, .5 * beam.dy), rg.Interval(-.5 * beam.dz, .5 * beam.dz)
            if negative_direction:
                dx_foundation = rg.Interval(- 1000, overlap - beam.extension)
            else:
                dx_foundation = rg.Interval(- overlap + beam.extension, 2000)
                
            # creating brep representation
            trimming_plane = rg.Plane.WorldXY
            trimming_plane.Translate(rg.Vector3d(projected_pt_on_ref_pl.X, projected_pt_on_ref_pl.Y, 0))
            bounding_box = rg.Box(rg.Plane(trimming_plane), rg.Interval(-10000.0, 10000.0), rg.Interval(-10000.0, 10000.0), rg.Interval(ref_pl.Origin.Z, 10000.0)) 
            raw_f_breps = [rg.Box(pl, dx_foundation, dy_foundation, dz_foundation) for pl in f_pls]
            foundation_breps = [rg.Brep.CreateBooleanIntersection(r_f_brep.ToBrep(), bounding_box.ToBrep(), 1)[0] for r_f_brep in raw_f_breps]
            
            return foundation_breps

    def __triple_dowel_function(self, beam_index):
        """ method that returns the joint points at a certain point on the beam

            :param beam_index:  The index of the beam to consider.
            :return:            The beam hole locations.
        """

        if (self.type < 3):
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

        if (self.type > 2):
            # normal joint type hole methods
            base_plane = self.beam_set[beam_index].base_plane
            x1, y1, x2, y2 = self.translation_variables
            x_vec = base_plane.XAxis
            y_vec = base_plane.YAxis
            b_o = base_plane.Origin

            top_0 = rg.Point3d(x_vec * x1 + y_vec * y1)
            bot_0 = rg.Point3d(x_vec * x2 + y_vec * y2)
            mid_0 = (top_0 + bot_0) * .5

            set_a = [rg.Point3d(b_o + top_0), rg.Point3d(b_o + mid_0), rg.Point3d(b_o + bot_0)]
            set_b = [rg.Point3d(b_o - top_0), rg.Point3d(b_o - mid_0), rg.Point3d(b_o - bot_0)]
            hole_list = [set_a, set_b]
            return hole_list

            beam_extension_l = abs(x1) + self.overextend

            self.beam_set[beam_index].extends(beam_extension_l)

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

        # making sure that the beams are not parallel
        # if (v_angle > 3.11 or v_angle < 0.03):
        #     print "your angle is too small", v_angle
        #
        #     # otherwise you set it to some static values
        #     x0_ext, cover_h, x1_ext = self.x0_ext_set[1], self.cover_h_set[0], self.x1_ext_set[0]
        #     self.translation_variables = x0_ext, cover_h, x1_ext
        #
        #

        dy = middle_beam.dy
        x0_max, angle_para, cover = self.translation_variables

        if (v_angle > m.pi * .5):
            angle = (m.pi - v_angle) * angle_para
        else:
            angle = v_angle * angle_para

        # informing the points based on angle
        cos = m.cos(angle)
        sin = m.sin(angle)

        distance = 0

        for other_beam in other_beams:
            ignore, a, b = rg.Intersect.Intersection.LineLine(middle_beam.top_line, other_beam.top_line)
            pt_1 = middle_beam.top_line.PointAt(a)
            pt_2 = other_beam.top_line.PointAt(b)
            distance += rg.Line(pt_1, pt_2).Length

        spacing = distance
        x1 = spacing / 2.5

        r = (x0_max ** 2 + (dy * .5 - cover) ** 2) / ( 2 * (dy * .5 - cover))
        y = dy * .5 - cover

        top_pt = rg.Point3d(0, r - y, 0)
        bot_pt = rg.Point3d(0, - y, 0)

        pt_on_circle = rg.Point3d( - r * sin, - r * cos, 0) + top_pt
        pt_0_1 = rg.Point3d( x1 * cos, - x1 * sin, 0) + pt_on_circle
        pt_0_2 = rg.Point3d( - x1 * cos, x1 * sin, 0) + pt_on_circle

        x1, y1 = pt_0_1.X, pt_0_1.Y
        x2, y2 = pt_0_2.X, pt_0_1.Y

        self.translation_variables = [x1, y1, x2, y2]

        #
        # # Code for Daomond
        # # so it's not parallel
        # else:
        #     # rotating the beams to be checked to the xy-plane for easy use
        #     reference_plane = rg.Plane(middle_beam.base_plane)
        #
        #     world_xy = rg.Plane.WorldXY
        #     middle_beam.transform_instance_from_frame_to_frame(reference_plane, world_xy)
        #     [other_beam.transform_instance_from_frame_to_frame(reference_plane, world_xy) for other_beam in other_beams]
        #
        #     # joint point
        #     self.ref_pt = rg.Point3d(middle_beam.dx * .5, 0, 0)
        #
        #     # creating an empty list of pts that define will be used to define the corner pts of the overlap diamond
        #     top_pt, left_pt, right_pt, bot_pt = [rg.Point3d(0, 0, 0) for i in range(4)]
        #
        #     for other_beam in other_beams:
        #         ignore, a, b = rg.Intersect.Intersection.LineLine(middle_beam.top_line, other_beam.top_line)
        #         top_pt += middle_beam.top_line.PointAt(a)
        #         ignore, a, b = rg.Intersect.Intersection.LineLine(middle_beam.top_line, other_beam.bot_line)
        #         left_pt += middle_beam.top_line.PointAt(a)
        #         ignore, a, b = rg.Intersect.Intersection.LineLine(middle_beam.bot_line, other_beam.top_line)
        #         right_pt += middle_beam.bot_line.PointAt(a)
        #         ignore, a, b = rg.Intersect.Intersection.LineLine(middle_beam.bot_line, other_beam.bot_line)
        #         bot_pt += middle_beam.bot_line.PointAt(a)
        #
        #     # diamond pt list
        #     self.pts_set = [top_pt / pt_count, left_pt / pt_count, bot_pt / pt_count, right_pt / pt_count]
        #     self.pts_set.append(rg.Point3d(self.pts_set[0]))
        #
        #     # mid_pt of the diamond
        #     self.avg_pt = rg.Point3d((top_pt + left_pt + bot_pt + right_pt) / 4)
        #
        #     # diamond reference
        #     self.diamond = rg.PolylineCurve(self.pts_set)
        #     self.diamond_offset = self.diamond.Offset(world_xy, -35, .1, rg.CurveOffsetCornerStyle.Sharp)[0]
        #     self.new_pt_set = [self.diamond_offset.PointAt(self.diamond_offset.ClosestPoint(self.pts_set[i], 1000)[1]) for i in range(4)]
        #
        #     # diagonal distances of the corner points
        #     distance_0 = self.new_pt_set[0].DistanceTo(self.new_pt_set[1])  # top - bottom
        #     distance_1 = self.new_pt_set[2].DistanceTo(self.new_pt_set[3])  # left - right
        #
        #     # informing the parameters
        #     x0_ext = self.x0_ext_set[0] + distance_1 * (self.x0_ext_set[1] - self.x0_ext_set[0]) / self.x0_ext_set[2]
        #     cover_h = self.cover_h_set[0] + (self.cover_h_set[1] - self.cover_h_set[0]) * self.cover_h_set[2] / distance_0
        #     x1_ext = self.x1_ext_set[0] + distance_1 * distance_0 * (self.x1_ext_set[1] - self.x1_ext_set[0]) / self.x1_ext_set[2]
        #
        #     # setting back_up constraints
        #     if x0_ext > 1000:
        #         x0_ext = 1000
        #     elif x0_ext < 100:
        #         x0_ext = 100
        #     if cover_h < 30:
        #         cover_h = 30
        #     elif cover_h > 100:
        #         cover_h = 100
        #     if x1_ext > 250:
        #         x1_ext = 250
        #     elif x1_ext < -50:
        #         x1_ext < -50

            # outputting the translation variables

    # def __transform_geo_to_xyplane(self, geo, ref_plane, invert = False):
    #     """
    #         internal method that tranforms some geometry to the xy_plane
    #
    #         :param geo:             Input Geometry
    #         :param ref_plane:       Plane used as a reference
    #         :param invert:          To ref_plane = True, To xy_plane = False
    #         :return new_geo:        Geometries that have been transformed
    #     """
    #     if (invert):
    #         plane_0, plane_1 = rg.Plane.WorldXY, ref_plane
    #     else:
    #         plane_1, plane_0 = rg.Plane.WorldXY, ref_plane
    #     trans_matrix = rg.Transform.PlaneToPlane(plane_0, plane_1)
    #     new_geo = [temp_geo.Transform(trans_matrix) for temp_geo in geo]
    #
    #     return new_geo
