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
import dowel
import beam

class Hole:
    """
    Stores the planes for the drilling process.
    """

    def __init__(self, gripping_plane=None, top_plane=None, bottom_plane=None, middle_plane=None, beam_brep=None):
        """
        initialization

        :param gripping_plane: gripping_plane plane to grab the beam
        :param top_plane:  top_plane plane to be drilled
        :param bottom_plane:  bottom_plane plane to be drilled
        :param middle_plane:  middle_plane plane to be drilled
        :param beam_brep: beam brep to be drilled (for debug purpose only)
        """

        self.gripping_plane = gripping_plane
        self.top_plane = top_plane
        self.bottom_plane = bottom_plane
        self.middle_plane = middle_plane
        self.beam_brep = beam_brep


    @staticmethod
    def create_holes(beam, safe_buffer=2.0):
        """
        instanciates the holes in the beam

        :param beam:  beam plane to be drilled
        :param safe_buffer:  buffer length to drill for each side of the beam
        :return: [Hole]
        """

        holes = []
        
        beam_normal = beam.base_plane.XAxis

        for dowel in beam.dowel_list:

            # can be optimized (for now it holds the very middle part of the beam)
            gripping_plane = rg.Plane(beam.base_plane)

            line = dowel.get_line()

            dowel_plane  = dowel.get_plane()
            dowel_normal = dowel_plane.Normal
            angle = rg.Vector3d.VectorAngle(beam_normal, dowel_normal)

            top_frame    = rg.Plane(beam.base_plane)
            middle_frame = rg.Plane(beam.base_plane)
            bottom_frame = rg.Plane(beam.base_plane)
            
            diff = beam.dz * 0.5 + abs(dowel.dowel_radius / math.tan(angle)) + safe_buffer

            top_frame.Translate(beam.base_plane.ZAxis * diff)
            bottom_frame.Translate(-beam.base_plane.ZAxis * diff)

            hole_plane_list = []

            for f in [top_frame, middle_frame, bottom_frame]:

                succeeded, v = rg.Intersect.Intersection.LinePlane(line, f)

                p = line.PointAt(v)
                plane = rg.Plane(dowel_plane)
                plane.Origin = p
                hole_plane_list.append(plane)

                # to direct normals of holes to that of gripping plane
                angle = rg.Vector3d.VectorAngle(gripping_plane.Normal, plane.Normal)
                if math.pi * 0.5 < angle and angle < math.pi * 1.5:
                    plane.Flip()

            hole = Hole(gripping_plane=gripping_plane,
                top_plane=hole_plane_list[0],
                middle_plane=hole_plane_list[1],
                bottom_plane=hole_plane_list[2],
                beam_brep=beam.brep_representation())

            holes.append(hole)

        return holes

    @staticmethod
    def get_tool_planes_as_tree(beams, target_plane, safe_buffer=5.0, safe_plane_diff=100):
        """
        get planes for its fabrication as a data tree

        :param beams:  beams to be drilled
        :param target_plane:  the plane where a drill locates
        :param safe_buffer:  the buffer distance from the very edges of the beam
        :return: tuple of (a data tree of safes, a data tree of top planes, a data tree of bottom planes, a data tree of beam breps)
        """

        if not target_plane:
            target_plane = rg.Plane.WorldXY

        safe_plane_tree   = datatree[System.Object]()
        top_plane_tree    = datatree[System.Object]()
        bottom_plane_tree = datatree[System.Object]()
        beam_brep_tree    = datatree[System.Object]()
        
        for i, beam in enumerate(beams):
            
            holes = Hole.create_holes(beam, safe_buffer=safe_buffer)
            
            path = ghpath(i)
            
            for hole in holes:
                
                hole.orient_to_drilling_station(target_plane)
                safe_plane, top_plane, bottom_plane = hole.get_tool_planes(safe_plane_diff=safe_plane_diff)
                
                safe_plane_tree.Add(safe_plane, path)
                top_plane_tree.Add(top_plane, path)
                bottom_plane_tree.Add(bottom_plane, path)
                beam_brep_tree.Add(hole.beam_brep, path)
         
        return safe_plane_tree, top_plane_tree, bottom_plane_tree, beam_brep_tree
                
    def orient_to_drilling_station(self, target_frame):
        """
        orient a bottom plane to a given frame

        :param target_frame:  the plane to be oriented
        """
        
        transform = rg.Transform.PlaneToPlane(self.middle_plane, target_frame)
        self.gripping_plane.Transform(transform)
        self.top_plane.Transform(transform)
        self.bottom_plane.Transform(transform)
        self.middle_plane.Transform(transform)

        if self.beam_brep:
            self.beam_brep.Transform(transform)

    def get_tool_planes(self, safe_plane_diff=100):
        """
        get planes to be sent to the robotic arm 

        :param safe_plane_diff:  offset for the safe plane
        :return: (safe plane, top plane, bottom plane)
        """
        
        top_diff = self.top_plane.Origin.Z - self.middle_plane.Origin.Z
        bottom_diff = self.bottom_plane.Origin.Z - self.middle_plane.Origin.Z
        
        top_gripping_plane = rg.Plane(self.gripping_plane)
        top_gripping_plane.Translate(rg.Vector3d(0, 0, top_diff))

        bottom_gripping_plane = rg.Plane(self.gripping_plane)
        bottom_gripping_plane.Translate(rg.Vector3d(0, 0, bottom_diff))

        safe_gripping_plane = rg.Plane(top_gripping_plane)
        safe_gripping_plane.Translate(rg.Vector3d(0, 0, safe_plane_diff))
        
        return safe_gripping_plane, top_gripping_plane, bottom_gripping_plane