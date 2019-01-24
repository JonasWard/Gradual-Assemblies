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
        get angles between the beam and connected dowels

        :return: list of angles in radian
        """
        angles = []

        beam_vector = self.base_plane.Normal

        for dowel in self.dowel_list:
            
            dowel_vector = dowel.get_plane().Normal
            angle = rg.Vector3d.VectorAngle(beam_vector, dowel_vector)
            angles.append(angle)

        return angles

    def get_distance_from_edges(self):
        """
        get distance from the beam's edge

        :return: list of distances
        """

        distances = []

        top_frame    = rg.Plane(self.base_plane)
        bottom_frame = rg.Plane(self.base_plane)

        top_frame.Translate(self.base_plane.ZAxis * 0.5 * self.dz)
        bottom_frame.Translate(-self.base_plane.ZAxis * 0.5 * self.dz)

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
