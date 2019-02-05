"""
Basic classes for MAS-DFAB 2018-19 T2 GKR Project
"""

__author__ = "masdfab students"
__status__ = "development"
__version__ = "0.0.1"
__date__    = "15 January 2019"

import Rhino.Geometry as rg
import Grasshopper.Kernel.Data.GH_Path as ghpath
import Grasshopper.DataTree as datatree
import System
import math
import beam
import hole

class Dowel(object):
    """
    Dowel class with connected beams
    """

    def __init__(self, base_plane=None, line=None, dowel_radius=12.0, hole_radius=None):
        """
        initialization
        base_plane and line are exclusive!

        :param base_plane: base plane which the dowel is along with
        :param line: line object that corresponds to the dowel itself
        :param dowel_radius: dowel radius
        :param hole_radius: hole radius (if not specified, equal to dowel radius)
        """

        if base_plane and line:
            # TODO throw error
            return

        self.base_plane = base_plane
        self.line = line
        self.dowel_radius = dowel_radius
        self.hole_radius  = hole_radius if hole_radius else dowel_radius
        self.beam_list  = []

    def __eq__(self, other):

        if not isinstance(other, Dowel):
            return False

        base_plane = self.get_plane()
        other_base_plane = self.get_plane()

        # whether the planes are colinear or not
        vec = rg.Vector3d.Subtract(rg.Vector3d(base_plane.Origin), rg.Vector3d(other_base_plane.Origin))
        normal = base_plane.Normal
        angle = rg.Vector3d.VectorAngle(vec, normal)
        return angle == 0 or angle == math.pi


    def remove_duplicates_in_beam_list(self):
        """
        resolve beam duplication
        """

        return list(set(self.beam_list))

    def get_plane(self):
        """
        get the plane on this dowel

        :return: rg.Vector3d
        """

        if self.base_plane:

            return self.base_plane

        else:

            p1 = self.line.PointAt(0)
            pc = self.line.PointAt(0.5)
            p2 = self.line.PointAt(1)
            return rg.Plane(pc, rg.Vector3d.Subtract(rg.Vector3d(p1),
                rg.Vector3d(p2)))


    def get_calculated_line(self):
        """
        get the line with the actual length

        :return: rg.Line
        """

        if self.line:
            return self.line

        # get an infinite line
        diff = self.base_plane.Normal * 9999
        p1 = rg.Point3d.Subtract(self.base_plane.Origin, diff)
        p2 = rg.Point3d.Subtract(self.base_plane.Origin, -diff)

        dowel_line = rg.Line(p1, p2)

        smallest_val  = 9999
        biggest_val   = -9999
        smallest_beam = None
        biggest_beam  = None

        dowel_plane  = self.get_plane()
        dowel_normal = dowel_plane.Normal

        if len(self.beam_list) < 2:
            return self.get_line()

        # get both ends of this dowel
        for beam in self.beam_list:

            beam_line = beam.get_baseline()

            _, dowel_v, beam_v = rg.Intersect.Intersection.LineLine(dowel_line, beam_line)

            if dowel_v < smallest_val:
                smallest_val = dowel_v
                smallest_beam = beam

            if biggest_val < dowel_v:
                biggest_val = dowel_v
                biggest_beam = beam

        actual_dowel_line = rg.Line(dowel_line.PointAt(smallest_val), dowel_line.PointAt(biggest_val))

        # entend the dowel
        angle = rg.Vector3d.VectorAngle(dowel_normal, smallest_beam.base_plane.XAxis)
        exntension_1 = smallest_beam.dz * 0.5 / math.sin(angle)

        angle = rg.Vector3d.VectorAngle(dowel_normal, biggest_beam.base_plane.XAxis)
        exntension_2 = biggest_beam.dz * 0.5 / math.sin(angle)

        actual_dowel_line.Extend(exntension_1, exntension_2)

        return actual_dowel_line

    def brep_representation(self):
        """
        make a brep of this dowel (for now with pseudo end points)

        :return: cylinder object of this dowel
        """

        return self.get_hole_pipe()

    def get_line(self, scale_value = 1.0):
        """
        get a line object of this dowel

        :param scale_value: scales the line according to a certain value (default = 1.0)
        :return: line object
        """

        if (self.line and scale_value == 1.0):
            # print "jack shit"
            return self.line
        elif (self.line and not(scale_value == 1.0)):
            # print "scaled"
            pt_0, pt_1 = self.line.PointAt(0.0), self.line.PointAt(1.0)
            mid_pt = (pt_0 + pt_1) / 2.0
            scale = rg.Transform.Scale(mid_pt, scale_value)
            scaled_line = rg.Line(pt_0, pt_1)
            scaled_line.Transform(scale)
            return scaled_line
        else:
            # get an infinite line
            # print "da fuck"
            diff = self.base_plane.Normal * 999
            p1 = self.base_plane.Origin + diff
            p2 = self.base_plane.Origin - diff

            return rg.Line(p1, p2)

    def get_angle_between_beam_and_dowel(self):
        """
        get maximum angle between the dowel and connected beams

        :return: angle in radian
        """
        angles = []

        dowel_vector = self.get_plane().Normal

        for beam in self.beam_list:

            beam_vector = beam.base_plane.Normal

            angle = rg.Vector3d.VectorAngle(beam_vector, dowel_vector)
            if math.pi * 0.5 < angle and angle < math.pi * 1.5:
                angle = math.pi - angle
            angles.append(angle)

        return max(angles)

    def get_distance_from_edges(self):
        """
        get minimum distance from the connected beams' edge

        :return: distance
        """

        line = self.get_line()

        distances = []

        for beam in self.beam_list:

            top_frame    = rg.Plane(beam.base_plane)
            bottom_frame = rg.Plane(beam.base_plane)

            top_frame.Translate(beam.base_plane.ZAxis * 0.5 * beam.dz)
            bottom_frame.Translate(-beam.base_plane.ZAxis * 0.5 * beam.dz)

            interval_x = rg.Interval(-beam.dx * 0.5, beam.dx * 0.5)
            interval_y = rg.Interval(-beam.dy * 0.5, beam.dy * 0.5)

            top_rectangle    = rg.Rectangle3d(top_frame, interval_x, interval_y)
            bottom_rectangle = rg.Rectangle3d(bottom_frame, interval_x, interval_y)

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
                distance = min(top_distance - self.dowel_radius, bottom_distance - self.dowel_radius)
                distances.append(distance)

        return min(distances)

    def get_hole_pipe(self, line = None):
        """
        get a cylinder drilled

        :param line: which line to pipe (default None line, which while result in the default line representation of the dowel)
        :return: cylinder object
        """

        return self.__get_pipe(self.hole_radius, line)

    def get_dowel_pipe(self):
        """
        get a cylinder of dowel

        :return: cylinder object
        """

        return self.__get_pipe(self.dowel_radius)

    def __get_pipe(self, radius, line = None):
        """
        private method to create a cylinder
        """
        if (line == None):
            line = self.get_line()

        _, plane = line.ToNurbsCurve().PerpendicularFrameAt(0)
        circle = rg.Circle(plane, radius)
        return rg.Cylinder(circle, line.Length)
