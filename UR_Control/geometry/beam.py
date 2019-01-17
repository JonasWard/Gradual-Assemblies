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

class Beam:

    """
    Beam class containing its size and connecting dowels
    """

    def __init__(self, base_plane, dx, dy, dz):

        """
        initialization
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

        """
        add a dowel to this beam
        :param dowel:  the new dowel to be added
        """

        self.dowel_list.append(dowel)
        dowel.beam_list.append(self)

    def remove_duplicates_in_dowel_list(self):

        """
        resolve dowel duplication
        """

        self.dowel_list = list(set(self.dowel_list))

    def brep_representation(self):

        """
        make a brep of this beam with holes
        :return brep object of this beam
        """

        # create a beam
        box = rg.Box(self.base_plane,
            rg.Interval(-self.dx*0.5, self.dx*0.5),
            rg.Interval(-self.dy*0.5, self.dy*0.5),
            rg.Interval(-self.dz*0.5, self.dz*0.5)
            )

        box = box.ToBrep()

        # create a dowels
        for dowel in self.dowel_list:

            pipe = dowel.get_outer_pipe()

            pipe = pipe.ToBrep(True, True)

            tmp_box = rg.Brep.CreateBooleanDifference(box, pipe, 0.1)

            if len(tmp_box) > 0:
                box = tmp_box[0]

        return box

    def get_baseline(self):

        """
        get a line along with z-axis
        :return line object of this beam
        """

        diff = self.base_plane.XAxis * self.dx * 0.5
        p1 = rg.Point3d.Subtract(self.base_plane.Origin, diff)
        p2 = rg.Point3d.Subtract(self.base_plane.Origin, -diff)

        return rg.Line(p1, p2)

    def transform_instance_to_frame(self, target_frame=None):

        """
        in-place transform
        :param target_frame:  target frame to transform according to this base_plane
        """

        Beam.__move_to_frame(self, self.base_plane, target_frame)

    def transform_instance_from_frame_to_frame(self, source_frame, target_frame=None):

        """
        in-place transform
        :param source_frame:  source_frame frame to transform
        :param target_frame:  target frame  to be transformed
        """

        Beam.__move_to_frame(self, source_frame, target_frame)

    def __move_to_frame(beam, source_frame, target_frame=None):

        """
        private method to transform
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

        """
        get a data tree of lines with the actual length of each dowel
        :param beams:  beams to be structured
        :return DataTree
        """

        tree = datatree[System.Object]()

        for i, beam in enumerate(beams):
            
            path = ghpath(i)
            
            for dowel in beam.dowel_list:
                
                tree.Add(dowel.get_calculated_line(), path)

        return tree
