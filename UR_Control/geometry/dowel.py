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

class Dowel:
    """
    Dowel class with connected beams
    """

    def __init__(self, base_plane=None, line=None, dowel_radius=1.0, hole_radius=1.2):
        """
        initialization
        base_plane and line are exclusive!

        :param base_plane: base plane which the dowel is along with
        :param line: line object that corresponds to the dowel itself
        :param dowel_radius: dowel radius
        :param hole_radius: hole radius
        """

        if base_plane and line:
            # TODO throw error
            return

        self.base_plane = base_plane
        self.line = line
        self.dowel_radius = dowel_radius
        self.hole_radius  = hole_radius
        self.beam_list  = []

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

        return self.get_inner_pipe()

    def get_line(self):
        """
        get a line object of this dowel

        :return: line object
        """

        if self.line:
            return self.line

        # get an infinite line
        diff = self.base_plane.Normal * 999
        p1 = rg.Point3d.Subtract(self.base_plane.Origin, diff)
        p2 = rg.Point3d.Subtract(self.base_plane.Origin, -diff)

        return rg.Line(p1, p2)

    def get_outer_pipe(self):
        """
        get a cylinder drilled

        :return: cylinder object
        """

        return self.__get_pipe(self.hole_radius)

    def get_inner_pipe(self):
        """
        get a cylinder of dowel

        :return: cylinder object
        """

        return self.__get_pipe(self.dowel_radius)

    def __get_pipe(self, radius):
        """
        private method to create a cylinder
        """

        line = self.get_line()

        _, plane = line.ToNurbsCurve().PerpendicularFrameAt(0)
        circle = rg.Circle(plane, radius)
        return rg.Cylinder(circle, line.Length)
