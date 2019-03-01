#
# Basic classes for MAS-DFAB 2018-19 T2 GKR Project
#

__author__ = "masdfab students"
__status__ = "development"
__version__ = "0.0.1"
__date__    = "15 January 2019"

import Rhino.Geometry as rg
import Grasshopper.Kernel.Data.GH_Path as ghpath
import Grasshopper.DataTree as datatree
import System
import math

class Beam(object):
    """ Beam class containing its size and connecting dowels
    """

    def __init__(self, base_plane, dx, dy, dz, end_cover = 70):
        """ initialization

            :param base_plane:  base plane which the beam is along with
            :param dx:          the length along the local x-axis (= the length of this beam)
            :param dy:          the length along the local y-axis
            :param dz:          the length along the local z-axis
            :param end_cover:   the extra extenions at the end of the beams
        """

        self.base_plane = base_plane

        self.dx = dx
        self.dy = dy
        self.dz = dz

        self.dx_base_line = dx

        self.dowel_list = []
        self.extension = 0
        self.end_cover = end_cover

    def add_dowel(self, dowel):
        """ add a dowel to this beam

            :param dowel:  the new dowel to be added
        """

        self.dowel_list.append(dowel)
        dowel.beam_list.append(self)

    def remove_duplicates_in_dowel_list(self):
        """ resolve dowel duplication
        """

        removed_dowel_list = []
        for i, d1 in enumerate(self.dowel_list):

            if i < len(self.dowel_list) - 1:

                duplicated = False
                for j, d2 in enumerate(self.dowel_list[i+1:]):

                    if d1 == d2:
                        duplicated = True
                        break

            if not duplicated:
                removed_dowel_list.append(d1)

        self.dowel_list = removed_dowel_list

    def brep_representation(self, make_holes=False, box = None):
        """ make a brep of this beam with holes

            :param make_holes:  boolean value to make holes in the beam (making holes requires some computation time)
            :paran box:  box object in the case one has been created through another function
            :return: brep object of this beam
        """
        total_extension = self.end_cover + self.extension

        if (box == None):
            # create a box in case one hasn't been fed in
            box = rg.Box(self.base_plane,
                rg.Interval(-self.dx*0.5 - total_extension, self.dx*0.5 + total_extension),
                rg.Interval(-self.dy*0.5, self.dy*0.5),
                rg.Interval(-self.dz*0.5, self.dz*0.5)
                )

        box = box.ToBrep()

        if not make_holes:
            return box

        # create a dowels
        for dowel in self.dowel_list:

            scale_value = 2.0
            line = rg.Line(dowel.get_line(scale_value).PointAt(0.0), dowel.get_line(scale_value).PointAt(1.0))
            pipe = dowel.get_hole_pipe(line)

            pipe = pipe.ToBrep(True, True)

            tmp_box = rg.Brep.CreateBooleanDifference(box, pipe, 0.1)

            if tmp_box and len(tmp_box) > 0:
                box = tmp_box[0]

        return box

    def get_baseline(self):
        """ get a line along with z-axis

            :return: line object of this beam
        """

        diff = self.base_plane.XAxis * self.dx_base_line * 0.5
        self.beam_start_pt = rg.Point3d.Subtract(self.base_plane.Origin, diff)
        self.beam_end_pt = rg.Point3d.Subtract(self.base_plane.Origin, -diff)

        return rg.Line(self.beam_start_pt, self.beam_end_pt)

    def get_angle_between_beam_and_dowel(self):
        """
        get angles between the beam and connected dowels

            :return: list of angles in radian
        """
        angles = []

        beam_vector = self.base_plane.Normal

        for dowel in self.dowel_list:

            dowel_vector = dowel.get_plane().Normal
            angle = rg.Vector3d.VectorAngle(beam_vector, dowel_vector)
            if math.pi * 0.5 < angle and angle < math.pi * 1.5:
                angle = math.pi - angle
            angles.append(angle)

        return angles

    def extend(self, x_change):
        """
        extends the brep representation of your beam b a certain value

            :param x_change:    amount to be checked for whether it's smaller or larger than the current brep extension value at BOTH sides (default = 0)
            :return: returns brep representation
        """
        # maybe to-do -> variying overlaps at varying sides
        if x_change > self.extension:
            self.extension = x_change

    def reset_length(self, new_length):
        """
        internal method that changes the length of the beam

        :param new_length:  The new length of the beam
        """
        
        self.dx = new_length

    def check_angle_constraints(self, angle = 55):
        """
        checks where the beam | dowel intersection events are problematic based on the angle between beam and dowel

            :param angle: cut off angle after which the intersection becomes problematic - ! in radians ! (default = 60)
            :return: list of holes that are problematic

        """
        angle = math.pi / 2 - math.radians(angle)

        angle_constraints = []

        angles = self.get_angle_between_beam_and_dowel()
        angle_count = int(len(angles))
        if not(angle_count == 0):
            for i in range (angle_count):
                if (angles[i] > angle):
                    line = self.dowel_list[i].get_line()
                    s, v = rg.Intersect.Intersection.LinePlane(line, self.base_plane)
                    error_sphere = rg.Sphere(line.PointAt(v), self.dz)
                    angle_constraints.append(error_sphere)

        return angle_constraints

    def check_boundary_constraints(self, side_buf = 10, end_buf = 70, mid_buf = 500, mid_open = 450, angle_correction = 1.1):
        """
        checks where the beam | dowel intersection events are problematic based on where (or where not), the beams can go based on the dowel radius
            :param side_buf:            how much wood covering you need on the side of the beams (default = 10)
            :param end_buf:             how much wood covering you want at the ends of the beams (default = 70)
            :param mid_buf:             how much clearance there has to be for the picking plane (default = 500)
            :param mid_open:            if relevant, how much clearance there is between the picking rods (default = 450)
            :param angle_correction:    correction for dowel comming at an angle (default = 1.1 ~ angle of 60 deg)
            :return:                    list of holes that are problematic
        """

        # getting a radius of a dowel
        if not(len(self.dowel_list) == 0):
            dowel_rad = self.dowel_list[0].dowel_radius * angle_correction

            # height of all rectangles
            y_value = .5 * self.dy - (dowel_rad + side_buf)

            top_frame    = rg.Plane(self.base_plane)
            bot_frame = rg.Plane(self.base_plane)

            top_frame.Translate(self.base_plane.ZAxis * 0.5 * self.dz)
            bot_frame.Translate(-self.base_plane.ZAxis * 0.5 * self.dz)

            self.top_recs = []
            self.bot_recs = []

            # setting up the rectangle intervals
            # checking whether there have to be two rec's or just one
            if (mid_open < mid_buf and mid_open > .001):
                # there's need for a third rectangle
                x_val = mid_open * .5 - dowel_rad
                int_x = rg.Interval( - x_val, x_val)
                int_y = rg.Interval( - y_value, y_value)
                # adding the rectangles to the list
                self.top_recs.append(rg.Rectangle3d(top_frame, int_x, int_y))
                self.bot_recs.append(rg.Rectangle3d(bot_frame, int_x, int_y))

            if (mid_buf > .001):
                # this means you need to create two different rectangles
                # width of the rectangle
                x_value_1 = self.dx * .5 - dowel_rad - end_buf
                x_value_2 = .5 * mid_buf + dowel_rad
                int_x_1 = rg.Interval( - x_value_1, - x_value_2)
                int_x_2 = rg.Interval(x_value_2, x_value_1)
                # height of the rectangle
                int_y = rg.Interval( - y_value, y_value)
                # adding the rectangles to the list
                self.top_recs.append(rg.Rectangle3d(top_frame, int_x_1, int_y))
                self.bot_recs.append(rg.Rectangle3d(bot_frame, int_x_1, int_y))
                self.top_recs.append(rg.Rectangle3d(top_frame, int_x_2, int_y))
                self.bot_recs.append(rg.Rectangle3d(bot_frame, int_x_2, int_y))

            elif (mid_buf < .001):
                # there's only need for one rectangle
                # width of the rectangle
                x_value = self.dx - dowel_rad - end_buf
                # height of the rectangle
                int_x = rg.Interval( - x_value, x_value)
                int_y = rg.Interval( - y_value, y_value)
                # adding the rectangles to the list
                self.top_recs.append(rg.Rectangle3d(top_frame, int_x, int_y))
                self.bot_recs.append(rg.Rectangle3d(bot_frame, int_x, int_y))

            # calculating point intersections
            temp_top_pts = []
            temp_bot_pts = []

            count = len(self.dowel_list)

            for dowel in self.dowel_list:

                line = dowel.get_line()

                succeeded, t = rg.Intersect.Intersection.LinePlane(line, top_frame)
                top_pt = line.PointAt(t)

                succeeded, t = rg.Intersect.Intersection.LinePlane(line, bot_frame)
                bot_pt = line.PointAt(t)

                temp_top_pts.append(top_pt)
                temp_bot_pts.append(bot_pt)

            # generating the rectangles and doing the containment checks, represented by spheres
            boundary_constraints = []

            # setting coincident parameters
            inside = rg.PointContainment.Inside
            coincident = rg.PointContainment.Coincident
            outside = rg.PointContainment.Outside

            for top_pt in temp_top_pts:
                pt_is_problem = True
                for top_rec in self.top_recs:
                    containment_val = top_rec.Contains(top_pt)
                    print containment_val
                    if (containment_val == inside or containment_val == coincident):
                        pt_is_problem = False
                        break
                if (pt_is_problem):
                    error_sphere = rg.Sphere(top_pt, self.dz)
                    boundary_constraints.append(error_sphere)

            for bot_pt in temp_bot_pts:
                pt_is_problem = True
                for bot_rec in self.bot_recs:
                    containment_val = bot_rec.Contains(bot_pt)
                    if (containment_val == inside or containment_val == coincident):
                        pt_is_problem = False
                        break
                if (pt_is_problem):
                    error_sphere = rg.Sphere(bot_pt, self.dz)
                    boundary_constraints.append(error_sphere)

            return boundary_constraints
        else:
            print "this beam doesn't have any dowels linked to it!"

    def move_to_origin(self):
        """ in-place transform to move it to the origin of world coordinate system
        """

        source_plane = rg.Plane(self.base_plane)
        source_plane.Translate(rg.Vector3d(0, 0, -self.dz * 0.5))

        Beam.__move_to_frame(self, source_plane, rg.Plane.WorldXY)

    def transform_instance_to_frame(self, target_frame=None):
        """ in-place transform

            :param target_frame:  target frame to transform according to this base_plane
        """

        Beam.__move_to_frame(self, self.base_plane, target_frame)

    def transform_instance_from_frame_to_frame(self, source_frame, target_frame=None):
        """ in-place transform

            :param source_frame:  source_frame frame to transform
            :param target_frame:  target frame  to be transformed
        """

        Beam.__move_to_frame(self, source_frame, target_frame)

    def __move_to_frame(beam, source_frame, target_frame=None):
        """ private method to transform

            :param source_frame:    Frame to transform from
            :param target_frame:    Frame to transform to
            :return beam:           Returns the transformed beam object
        """

        if not target_frame:
            target_frame = rg.Plane(beam.base_plane)

        transform = rg.Transform.PlaneToPlane(source_frame, target_frame)

        beam.base_plane.Transform(transform)

        for dowel in beam.dowel_list:

            if dowel.base_plane:
                dowel.base_plane.Transform(transform)

            if dowel.line:
                dowel.line.Transform(transform)

        if beam.top_bot_line:
            beam.top_line.Transform(transform)
            beam.bot_line.Transform(transform)

        return beam

    def top_bot_line(self):
        """ method that add a line a the top and bottom of the beam plane """

        # self.top_bot_line = True
        # x_ax = self.base_plane.XAxis
        # y_ax = self.base_plane.YAxis
        # x_ax = rg.Point3d(x_ax * .5 * self.dx)
        # y_ax = rg.Point3d(y_ax * .5 * self.dy)
        # o_pt = rg.Point3d(self.base_plane.Origin)
        # x_val, y_val = x_ax + o_pt, y_ax + o_pt
        # pt_0, pt_1 = rg.Point3d(- x_val + y_val), rg.Point3d(x_val + y_val)
        # pt_2, pt_3 = rg.Point3d(- x_val - y_val), rg.Point3d(x_val - y_val)
        # self.top_line = rg.Line(pt_0, pt_1)
        # self.bot_line = rg.Line(pt_2, pt_3)

        # STUPID FFING RHINO POITN LISTS >>>>>
        x_ax_0, y_ax_0, z_ax_0 = self.base_plane.XAxis.X, self.base_plane.XAxis.Y, self.base_plane.XAxis.Z
        x_ax_1, y_ax_1, z_ax_1 = self.base_plane.YAxis.X, self.base_plane.YAxis.Y, self.base_plane.YAxis.Z
        x_ax_2, y_ax_2, z_ax_2 = self.base_plane.Origin.X, self.base_plane.Origin.Y, self.base_plane.Origin.Z
        l_0 = math.sqrt(x_ax_0 ** 2 + y_ax_0 ** 2 + z_ax_0 ** 2)
        l_1 = math.sqrt(x_ax_1 ** 2 + y_ax_1 ** 2 + z_ax_1 ** 2)
        pt_0_list = [x_ax_0, y_ax_0, z_ax_0]
        pt_1_list = [x_ax_1, y_ax_1, z_ax_1]
        pt_0_list = [val * .5 * self.dx for val in pt_0_list]
        pt_1_list = [val * .5 * self.dy for val in pt_1_list]
        pt_2_list = [x_ax_2, y_ax_2, z_ax_2]
        pt_0 = [(-pt_0_list[i] + pt_1_list[i] + pt_2_list[i]) for i in range(3)]
        pt_1 = [(+pt_0_list[i] + pt_1_list[i] + pt_2_list[i]) for i in range(3)]
        pt_2 = [(-pt_0_list[i] - pt_1_list[i] + pt_2_list[i]) for i in range(3)]
        pt_3 = [(+pt_0_list[i] - pt_1_list[i] + pt_2_list[i]) for i in range(3)]
        pt_0, pt_1 = rg.Point3d(pt_0[0], pt_0[1], pt_0[2]), rg.Point3d(pt_1[0], pt_1[1], pt_1[2])
        pt_2, pt_3 = rg.Point3d(pt_2[0], pt_2[1], pt_2[2]), rg.Point3d(pt_3[0], pt_3[1], pt_3[2])
        self.top_line = rg.Line(pt_0, pt_1)
        self.bot_line = rg.Line(pt_2, pt_3)

    def end_frames(self):
        """ method that returns the start and end frame of the beam """

        self.get_baseline()

        pt_0 = self.base_plane.Origin

        mVector_start = rg.Vector3d(self.beam_start_pt - pt_0)
        mVector_end = rg.Vector3d(self.beam_end_pt - pt_0)

        translate_start = rg.Transform.Translation(mVector_start)
        translate_end = rg.Transform.Translation(mVector_end)

        self.start_plane = rg.Plane(self.base_plane).Transform(translate_start)
        self.end_plane = rg.Plane(self.base_plane).Transform(translate_end)

    @staticmethod
    def get_strucutured_data(beams):
        """ get a data tree of lines with the actual length of each dowel

            :param beams:  beams to be structured
            :return: DataTree
        """

        tree = datatree[System.Object]()

        for i, beam in enumerate(beams):

            path = ghpath(i)

            for dowel in beam.dowel_list:

                tree.Add(dowel.get_calculated_line(), path)

        return tree
