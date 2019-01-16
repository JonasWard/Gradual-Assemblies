"""
Basic classes for MAS-DFAB 2018-19 T2 GKR Project
"""

__author__ = "masdfab students"
__status__ = "development"
__version__ = "0.0.1"
__date__    = "15 January 2019"

import Rhino.Geometry as rg
import math

tmp = []

class Hole:

    """
    Stores the planes for the drilling process.
    """

    def __init__(self, gripping_plane, top_plane, bottom_plane, beam):

        """
        initialization
        :param gripping_plane: gripping_plane plane to grab the beam
        :param top_plane:  top_plane plane to start drilling
        :param bottom_plane:  bottom_plane plane to end drilling
        :param beam: beam to be drilled (for debug purpose only)
        """

        self.gripping_plane = gripping_plane
        self.top_plane = top_plane
        self.bottom_plane = bottom_plane
        self.beam = beam

    @staticmethod
    def create_holes(beam, safe_buffer=2.0):

        """
        instanciates the holes in the beam
        :param beam:  beam plane to be drilled
        :param safe_buffer:  buffer length to drill for each side of the beam
        :return [Hole]
        """

        holes = []

        # can be optimized (for now it holds the very middle part of the beam)
        gripping_plane = beam.base_plane

        vector_1 = beam.base_plane.XAxis

        for dowel in beam.dowel_list:

            line = dowel.get_line()

            vector_2 = dowel.base_plane.Normal
            angle = rg.Vector3d.VectorAngle(vector_1, vector_2)

            top_frame = rg.Plane(beam.base_plane)
            bottom_frame = rg.Plane(beam.base_plane)

            diff = beam.dy * 0.5 + abs(dowel.inner_radius / math.tan(angle)) + safe_buffer

            top_frame.Translate(beam.base_plane.ZAxis * diff)
            bottom_frame.Translate(-beam.base_plane.ZAxis * diff)

            hole_plane_list = []

            for f in [top_frame, bottom_frame]:

                succeeded, v = rg.Intersect.Intersection.LinePlane(line, f)

                p = line.PointAt(v)
                plane = rg.Plane(dowel.base_plane)
                plane.Origin = p
                hole_plane_list.append(plane)

                # to direct normals of holes to that of gripping plane
                angle = rg.Vector3d.VectorAngle(gripping_plane.Normal, plane.Normal)
                if math.pi * 0.5 < angle and angle < math.pi * 1.5:
                    plane.Flip()

            hole = Hole(gripping_plane=rg.Plane(gripping_plane),
                top_plane=hole_plane_list[0],
                bottom_plane=hole_plane_list[1],
                beam=beam.copy())

            holes.append(hole)

        return holes

    def orient_to_drilling_station(self, target_frame):

        """
        orient a bottom plane to a given frame
        """

        copied = rg.Plane(self.bottom_plane)
        transform = rg.Transform.PlaneToPlane(copied, target_frame)
        self.gripping_plane.Transform(transform)
        self.top_plane.Transform(transform)
        self.bottom_plane.Transform(transform)


        if self.beam:
            self.beam.transform_instance_from_frame_to_frame(copied, target_frame)


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

    def copy(self):

        """
        create a copy of this instance
        :return copied beam
        """

        beam = Beam(base_plane=rg.Plane(self.base_plane),
                dx=self.dx,
                dy=self.dy,
                dz=self.dz)

        for d in self.dowel_list:

            dowel = Dowel(base_plane=rg.Plane(d.base_plane),
                line=d.line)
            beam.add_dowel(dowel)

        return beam

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

        diff = self.base_plane.Normal * self.dz * 0.5
        p1 = rg.Point3d.Subtract(self.base_plane.Origin, diff)
        p2 = rg.Point3d.Subtract(self.base_plane.Origin, -diff)

        return rg.Line(p1, p2)

    def transform_instance_to_frame(self, target_frame=None):

        """
        in-place transform
        :param target_frame:  target frame to transform according to this base_plane
        """

        Beam.__move_to_frame(self, self.base_plane, target_frame)

    def transform_duplicate_to_frame(self, target_frame=None):

        """
        get the new beam transformed
        :param target_frame:  target frame to transform according to this base_plane
        :return Beam class
        """

        copied = self.copy()
        return Beam.__move_to_frame(copied, self.base_plane, target_frame)

    def transform_instance_from_frame_to_frame(self, source_frame, target_frame=None):

        Beam.__move_to_frame(self, source_frame, target_frame)

    def transform_duplicate_from_frame_to_frame(self, source_frame, target_frame=None):

        copied = self.copy()
        return Beam.__move_to_frame(copied, source_frame, target_frame)

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

class Dowel:

    """
    Dowel class with connected beams
    """

    """radius of dowel itself"""
    inner_radius = 10

    """radius to be drilled"""
    outer_radius = 12

    def __init__(self, base_plane=None, line=None):

        """
        initialization
        :param base_plane: base plane which the dowel is along with
        :param line: line object that corresponds to the dowel itself

        base_plane and line are exclusive!
        """

        if base_plane and line:
            # TODO throw error
            return

        self.base_plane = base_plane
        self.line = line
        self.beam_list  = []

    def remove_duplicates_in_beam_list(self):

        """
        resolve beam duplication
        """

        return list(set(self.beam_list))

    def brep_representation(self):

        """
        make a brep of this dowel (for now with pseudo end points)
        :return cylinder object of this dowel
        """

        return self.get_inner_pipe()

    def get_line(self):

        """
        get a line object of this dowel
        :return line object
        """

        if self.line:
            return self.line

        # get an infinite line
        diff = self.base_plane.Normal * 9999
        p1 = rg.Point3d.Subtract(self.base_plane.Origin, diff)
        p2 = rg.Point3d.Subtract(self.base_plane.Origin, -diff)

        return rg.Line(p1, p2)

    def get_outer_pipe(self):

        """
        get a cylinder drilled
        :return cylinder object
        """

        return self.__get_pipe(self.outer_radius)

    def get_inner_pipe(self):

        """
        get a cylinder of dowel
        :return cylinder object
        """

        return self.__get_pipe(self.inner_radius)

    def __get_pipe(self, radius):

        """
        private method to create a cylinder
        """

        line = self.get_line()

        _, plane = line.ToNurbsCurve().PerpendicularFrameAt(0)
        circle = rg.Circle(plane, radius)
        return rg.Cylinder(circle, line.Length)

# instanciate objects
beam_1  = Beam(base_plane=beam_base_plane_1, dx=300, dy=50, dz=25)
beam_2  = Beam(base_plane=beam_base_plane_2, dx=300, dy=50, dz=25)
dowel_1 = Dowel(base_plane=dowel_base_plane_1)
dowel_2 = Dowel(base_plane=dowel_base_plane_2)

beam_1.add_dowel(dowel_1)
beam_1.add_dowel(dowel_2)
beam_2.add_dowel(dowel_1)
beam_2.add_dowel(dowel_2)

# visualize the beams positioned in space
beams = [b.brep_representation() for b in [beam_1, beam_2]]

# create holes
frame = rg.Plane(rg.Plane.WorldXY.Origin, rg.Plane.WorldXY.ZAxis)
frame.Translate(rg.Vector3d(-200, -200, 0))

gripping_planes = []
top_planes = []
bottom_planes = []

holes = Hole.create_holes(beam_1)
for hole in holes:

    hole.orient_to_drilling_station(frame)

    top_planes.append(hole.top_plane)
    bottom_planes.append(hole.bottom_plane)
    gripping_planes.append(hole.gripping_plane)

tmp.append(holes[1].beam.brep_representation())
tmp.append(holes[0].beam.brep_representation())

holes = Hole.create_holes(beam_2)
for hole in holes:

    hole.orient_to_drilling_station(frame)

    top_planes.append(hole.top_plane)
    bottom_planes.append(hole.bottom_plane)
    gripping_planes.append(hole.gripping_plane)

tmp.append(holes[1].beam.brep_representation())
tmp.append(holes[0].beam.brep_representation())
