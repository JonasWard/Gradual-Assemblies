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

class Beam:
    """ Beam class containing its size and connecting dowels
    """

    def __init__(self, base_plane, dx, dy, dz):
        """ initialization

            :param base_plane: base plane which the beam is along with
            :param dx:  the length along the local x-axis (= the length of this beam)
            :param dy:  the length along the local y-axis
            :param dz:  the length along the local z-axis
        """

        self.base_plane = base_plane
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.dowel_list = []

    def add_dowel(self, dowel):
        """ add a dowel to this beam

            :param dowel:  the new dowel to be added
        """

        self.dowel_list.append(dowel)
        dowel.beam_list.append(self)

    def remove_duplicates_in_dowel_list(self):
        """ resolve dowel duplication
        """

        self.dowel_list = list(set(self.dowel_list))

    def brep_representation(self, make_holes=True):
        """ make a brep of this beam with holes

            :param make_holes:  boolean value to make holes in the beam (making holes requires some computation time)
            :return: brep object of this beam
        """

        # create a beam
        box = rg.Box(self.base_plane,
            rg.Interval(-self.dx*0.5, self.dx*0.5),
            rg.Interval(-self.dy*0.5, self.dy*0.5),
            rg.Interval(-self.dz*0.5, self.dz*0.5)
            )

        box = box.ToBrep()

        if not make_holes:
            return box

        # create a dowels
        for dowel in self.dowel_list:

            pipe = dowel.get_hole_pipe()

            pipe = pipe.ToBrep(True, True)

            tmp_box = rg.Brep.CreateBooleanDifference(box, pipe, 0.1)

            if len(tmp_box) > 0:
                box = tmp_box[0]

        return box

    def get_baseline(self):
        """ get a line along with z-axis

            :return: line object of this beam
        """

        diff = self.base_plane.XAxis * self.dx * 0.5
        p1 = rg.Point3d.Subtract(self.base_plane.Origin, diff)
        p2 = rg.Point3d.Subtract(self.base_plane.Origin, -diff)

        return rg.Line(p1, p2)

    def get_angle_between_beam_and_dowel(self):
        """
        returns the smallest angle between the beam plane and the dowels

        :return: list of angles in radian
        """
        angles = []

        beam_vector = self.base_plane.Normal

        for dowel in self.dowel_list:

            dowel_vector = dowel.get_plane().Normal
            angle = rg.Vector3d.VectorAngle(beam_vector, dowel_vector)
            angles.append(angle)

        return angles

    def constraint_beam_dowel_checker(self, side_buf = 10, end_buf = 70, mid_buf = 250, angle_correction = 1.1):
        """
        checks where the beam | dowel intersection events are problematic based on where (or where not), the beams can go based on the dowel radius

        :param side_buf: how much wood covering you need on the side of the beams (default = 10)
        :param end_buf: how much wood covering you want at the ends of the beams (default = 70)
        :param mid_buf: how much clearance there has to be for the picking plane (default = 250)
        :param angle_correction: correction for dowel comming at an angle (default = 1.1 ~ angle of 60 deg)
        :return: list of holes

        """


        # getting a radius of a dowel
        if not(len(self.dowel_list) == 0):
            dowel_rad = self.dowel_list[0].dowel_radius * angle_correction
        else:
            break

        # setting up the rectangle intervals
        # checking whether there have to be two rec's or just one
        if (mid_buf > .001):
            two_rectangles = True
            # this means you need to create two different rectangles
            # width of the rectangle
            x_value_1 = self.dx - dowel_rad - end_buf
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
        self.boundary_constraints = []

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
                print containment_value
                if (containment_value == inside or containment_value == coincident):
                    containment_value = bottom_rectangle_1.Contains(local_bottom_pt)
                    if (containment_value == inside or containment_value == coincident):
                        self.boundary_constraints.append(containment_value)
                    elif (containment_value == outside):
                        # print "level_1"
                        error_sphere = rg.Sphere(mid_point, self.dz)
                        self.boundary_constraints.append(error_sphere)
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
                            self.boundary_constraints.append(error_sphere)
                        else:
                            print "error"
                    elif (containment_value == outside):
                        # print "level_3"
                        error_sphere = rg.Sphere(mid_point, self.dz)
                        self.boundary_constraints.append(error_sphere)
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
                        self.boundary_constraints.append(error_sphere)
                    else:
                        print "error"
                elif (containment_value == outside):
                    error_sphere = rg.Sphere(mid_point, self.dz)
                    self.boundary_constraints.append(error_sphere)
                else:
                    print "error"

    def get_distance_from_edges(self):
        """
        returns the distance from the edge of the centerline of a beam | dowel
        intersection

        :return: list of distances
        """

        distances = []

        # initialization
        top_frame    = rg.Plane(self.base_plane)
        bottom_frame = rg.Plane(self.base_plane)

        # translation
        top_frame.Translate(self.base_plane.ZAxis * 0.5 * self.dz)
        bottom_frame.Translate(-self.base_plane.ZAxis * 0.5 * self.dz)

        # rectangle properties
        interval_x = rg.Interval(-self.dx * 0.5, self.dx * 0.5)
        interval_y = rg.Interval(-self.dy * 0.5, self.dy * 0.5)

        top_rectangle    = rg.Rectangle3d(top_frame, interval_x, interval_y)
        bottom_rectangle = rg.Rectangle3d(bottom_frame, interval_x, interval_y)

        for dowel in self.dowel_list:

            line = dowel.get_line()

            succeeded, v = rg.Intersect.Intersection.LinePlane(line, top_frame)
            top_pt = line.PointAt(v)

            succeeded, v = rg.Intersect.Intersection.LinePlane(line, bottom_frame)
            bottom_pt = line.PointAt(v)

            top_closest_pt    = top_rectangle.ClosestPoint(top_pt, False)
            bottom_closest_pt = bottom_rectangle.ClosestPoint(bottom_pt, False)

            top_distance    = top_pt.DistanceTo(top_closest_pt)
            bottom_distance = bottom_pt.DistanceTo(bottom_closest_pt)

            # see if the dowel is outside of the dowel
            if top_rectangle.Contains(top_pt) == rg.PointContainment.Outside or \
                bottom_rectangle.Contains(bottom_pt) == rg.PointContainment.Outside:

                # if outside, just add a pretty small value
                distances.append(-9999)

            else:

                # is inside
                distance = min(top_distance - dowel.dowel_radius, bottom_distance - dowel.dowel_radius)
                distances.append(distance)

        return distances

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
