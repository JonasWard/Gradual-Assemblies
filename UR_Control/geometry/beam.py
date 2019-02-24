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

    def brep_representation(self, make_holes=True, box = None):
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

    def check_boundary_constraints(self, side_buf = 10, end_buf = 70, mid_buf = 500, angle_correction = 1.1):
        """
        checks where the beam | dowel intersection events are problematic based on where (or where not), the beams can go based on the dowel radius

            :param side_buf: how much wood covering you need on the side of the beams (default = 10)
            :param end_buf: how much wood covering you want at the ends of the beams (default = 70)
            :param mid_buf: how much clearance there has to be for the picking plane (default = 250)
            :param angle_correction: correction for dowel comming at an angle (default = 1.1 ~ angle of 60 deg)
            :return: list of holes that are problematic
        """
        
        # getting a radius of a dowel
        if not(len(self.dowel_list) == 0):
            dowel_rad = self.dowel_list[0].dowel_radius * angle_correction

        # setting up the rectangle intervals
        # checking whether there have to be two rec's or just one
        if (mid_buf > .001):
            two_rectangles = True
            # this means you need to create two different rectangles
            # width of the rectangle
            x_value_1 = self.dx * .5 - dowel_rad - end_buf
            x_value_2 = .5 * mid_buf + dowel_rad
            int_x_1 = rg.Interval( - x_value_1, - x_value_2)
            int_x_2 = rg.Interval(x_value_2, x_value_1)
            # height of the rectangle
            y_value = .5 * self.dy - (dowel_rad + side_buf)
            int_y = rg.Interval( - y_value, y_value)

        else:
            two_rectangles = False
            # there's only need for one rectangle
            # width of the rectangle
            x_value = self.dx - dowel_rad - end_buf
            # height of the rectangle
            y_value = .5 * self.dy - (dowel_rad + side_buf)
            int_x = rg.Interval( - x_value, x_value)
            int_y = rg.Interval( - y_value, y_value)

        # initialization
        top_frame    = rg.Plane(self.base_plane)
        bottom_frame = rg.Plane(self.base_plane)

        # translation
        top_frame.Translate(self.base_plane.ZAxis * 0.5 * self.dz)
        bottom_frame.Translate(-self.base_plane.ZAxis * 0.5 * self.dz)

        # calculating point intersections
        temp_top_pts = []
        temp_bottom_pts = []

        count = len(self.dowel_list)

        for dowel in self.dowel_list:

            line = dowel.get_line()

            succeeded, v = rg.Intersect.Intersection.LinePlane(line, top_frame)
            top_pt = line.PointAt(v)

            succeeded, v = rg.Intersect.Intersection.LinePlane(line, bottom_frame)
            bottom_pt = line.PointAt(v)

            temp_top_pts.append(top_pt)
            temp_bottom_pts.append(bottom_pt)

        # generating the rectangles and doing the containment checks, represented by spheres
        boundary_constraints = []

        # setting coincident parameters
        inside = rg.PointContainment.Inside
        coincident = rg.PointContainment.Coincident
        outside = rg.PointContainment.Outside

        if (two_rectangles):

            top_rectangle_1     = rg.Rectangle3d(top_frame, int_x_1, int_y)
            top_rectangle_2     = rg.Rectangle3d(top_frame, int_x_2, int_y)
            bottom_rectangle_1  = rg.Rectangle3d(bottom_frame, int_x_1, int_y)
            bottom_rectangle_2  = rg.Rectangle3d(bottom_frame, int_x_2, int_y)

            # checking for all holes whether there's an issue or not

            for i in range(count):
                local_top_pt = temp_top_pts[i]
                local_bottom_pt = temp_bottom_pts[i]
                mid_point = (local_top_pt + local_bottom_pt) / 2

                containment_value = top_rectangle_1.Contains(local_top_pt)
                if (containment_value == inside or containment_value == coincident):
                    containment_value = bottom_rectangle_1.Contains(local_bottom_pt)
                    if (containment_value == inside or containment_value == coincident):
                        pass
                    elif (containment_value == outside):
                        # print "level_1"
                        error_sphere = rg.Sphere(mid_point, self.dz)
                        boundary_constraints.append(error_sphere)
                    else:
                        print "error"
                elif (containment_value == outside):
                    containment_value = top_rectangle_2.Contains(local_top_pt)
                    if (containment_value == inside or containment_value == coincident):
                        containment_value = bottom_rectangle_2.Contains(local_bottom_pt)
                        if (containment_value == inside or containment_value == coincident):
                            pass
                        elif (containment_value == outside):
                            # print "level_4"
                            error_sphere = rg.Sphere(mid_point, self.dz)
                            boundary_constraints.append(error_sphere)
                        else:
                            print "error"
                    elif (containment_value == outside):
                        # print "level_3"
                        error_sphere = rg.Sphere(mid_point, self.dz)
                        boundary_constraints.append(error_sphere)
                    else:
                        print "error"
                else:
                    print "error"

        else:
            top_rectangle    = rg.Rectangle3d(top_frame, int_x, int_y)
            bottom_rectangle = rg.Rectangle3d(top_frame, int_x, int_y)

            for i in range(count):
                local_top_pt = temp_top_pts[i]
                local_bottom_pt = temp_bottom_pts[i]
                mid_point = (local_top_pt + local_bottom_pt) / 2

                containment_value = top_rectangle.Contains(local_top_pt)
                if (containment_value == inside or containment_value == coincident):
                    containment_value = bottom_rectangle.Contains(local_bottom_pt)
                    if (containment_value == inside or containment_value == coincident):
                        pass
                    elif (containment_value == outside):
                        error_sphere = rg.Sphere(mid_point, self.dz)
                        boundary_constraints.append(error_sphere)
                    else:
                        print "error"
                elif (containment_value == outside):
                    error_sphere = rg.Sphere(mid_point, self.dz)
                    boundary_constraints.append(error_sphere)
                else:
                    print "error"

        if (two_rectangles):
            self.top_recs = [top_rectangle_1, top_rectangle_2]
            self.bottom_recs = [bottom_rectangle_1, bottom_rectangle_2]
        else:
            self.top_recs = [top_rectangle]
            self.bottom_recs = [bottom_rectangle]

        return boundary_constraints

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
        """

        if not target_frame:
            target_frame = beam.base_plane

        transform = rg.Transform.PlaneToPlane(source_frame, target_frame)

        beam.base_plane.Transform(transform)

        for dowel in beam.dowel_list:

            if dowel.base_plane:
                dowel.base_plane.Transform(transform)

            if dowel.line:
                dowel.line.Transform(transform)

        return beam

    def end_frames(self):
        """ method that returns the start and end frame of the beam """

        self.get_baseline()

        pt_0 = self.base_plane.Origin

        mVector_start = rg.Vector3d(self.beam_start_pt - pt_0)
        mVector_end = rg.Vector3d(self.beam_end_pt - pt_0)

        translate_start = rg.Transform.Translation(mVector_start)
        translate_end = rg.Transform.Translation(mVector_end)

        self.start_plane = rg.Plane(base_plane).Transform(translate_start)
        self.end_plane = rg.Plane(base_plane).Transform(translate_end)

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
