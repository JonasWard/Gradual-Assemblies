'''
Created on 14.01.2019
@author: feihln

'''

import Rhino.Geometry as rg
import math as m
rg.Point3d()
class Dowel(object):
    """
    Dowel class, representation of a circular dowel section

    args:
    -line:
    """

    def __init__(self, line, rod_d = 24):
        self.r = rod_d / 2 #radius
        self.d = rod_d #diameter
        self.line = line

        ##fabrication atributes##
        #added depth to be sure to drill through
        self.safety_cut_depth = 1.0

    def placement_frame_gen(self):
        start_pt = self.line.PointAt(0.0)
        end_pt = self.line.PointAt(1.0)
        frame_normal = rg.Vector3d(end_pt - start_pt)

        self.base_pl = rg.Plane(start_pt, frame_normal)
        self.top_pl = rg.Plane(end_pt, frame_normal)

    def brep_representation(self):
        cylinder = rg.Brep.CreatePipe(rg.LineCurve(self.line), self.r, False, rg.PipeCapMode.Flat, False, .01, .01)
        return cylinder

class Beam(object):
    """
    Beam class, represention of a wood section

     args:
     -o_plane :  Plane defining the beam orientation,
                    origin is in the middle of the beam,
                    x_axis is the long axis of the beam,
                    y_axis is the second biggest beam size
    -s_x :      size of the beam in x(beam coordinates) direction
    -s_y :      size of the beam in y(beam coordinates) direction
    -s_z :      size of the beam in z(beam coordinates) direction
    """

    def __init__(self, o_plane, s_x = 2000, s_y = 100, s_z = 40):
        self.o_plane = o_plane
        self.size_x = s_x
        self.size_y = s_y
        self.size_z = s_z

        # statement to indicate that no intersections have been calculated yet
        self.intersections_calculated = False
        # statement to indicate that there are no wrongly place holes, False if all dowel placements are possible
        self.bad_points = False
        # List of holes in the beam for dowel insertion
        self.hole_list = []

    def box_interval(self, range, offset = 0):
        """
        defines intervals used to create geometry down the road

        args:
        -range : full range (size)
        -offset :
        """
        value = range * .5 - offset
        return rg.Interval(-value, value)

    def generate_box(self, plane = self.o_plane):
        """
        generate a simple box representation of the beam
        (no holes, no end angles)

        """
        self.x_int = self.box_interval(self.size_x)
        self.y_int = self.box_interval(self.size_y)
        self.z_int = self.box_interval(self.size_z)
        beam_box = rg.Box(plane, self.x_int, self.y_int, self.z_int)
        return beam_box

    def generate_holes(self, dowels):
        """
        for each dowel hole, generate a plane that is stored in the hole_list of the beam.
        the origin of the plane is the middle of the dowel,
        and the normal of the plane is the main axis of the dowel.

        args:
        -dowels : list of the dowels connected to the beam
        -
        """
        #create plane
        for dowel in dowels:
            line = dowel.line
            dowel_origin = rg.Intersect.Intersection.LinePlane(line, self.o_plane)
            hole_plane = rg.Plan


    def beam_line_intersection(self, dowels, coll_off_w = 0, coll_off_l = 0):
        """

        """

        # generating the top & bottom plane of a beam
        self.top_pl, self.bot_pl = rg.Plane(self.o_plane), rg.Plane(self.o_plane)

        move_up = rg.Vector3d(self.o_plane.Normal) *     0.5 * self.size_z
        move_down = rg.Vector3d(self.o_plane.Normal) *  -0.5 * self.size_z
        self.top_pl.Translate(move_up)
        self.bot_pl.Translate(move_down)

        # setting up global variables
        self.top_pts, self.bot_pts, self.dowel_ds = [], [], []
        self.local_int_lines = []

        for dowel in dowels:
            line = dowel.line
            r = dowel.r

            temp, top_pt_p = rg.Intersect.Intersection.LinePlane(line, self.top_pl)
            temp, bot_pt_p = rg.Intersect.Intersection.LinePlane(line, self.bot_pl)

            # implementing a scale_up to the geometry to allow for full overlap
            # with the bottom & top plane
            center_pt = rg.Point3d(top_pt_p - bot_pt_p) / 2

            normal = self.o_plane.normal
            vector = rg.Vector3d(top_pt_p - bot_pt_p)
            alfa = m.pi / 2 - rg.Vector3d(vector, normal)
            local_l = self.size_z + r / m.tan(alfa) + self.safety_l

            self.dowel_ds.append(r)
            self.top_pts.append(line.PointAt(top_pt_p))
            self.bot_pts.append(line.PointAt(bot_pt_p))
            self.local_int_lines.append(rg.Line(line.PointAt(top_pt_p),line.PointAt(bot_pt_p)))

        # indicating that the intersections have been calculated
        self.intersections_calculated = True

    def beam_line_intersection_collision(self, coll_off_w = 0, coll_off_l = 0):
        if (self.intersections_calculated):
            x_rec_int = self.interval_gen(self.size_x, coll_off_w)
            y_rec_int = self.interval_gen(self.size_y, coll_off_l)
            rec_up = rg.Rectangle3d(self.o_plane, x_rec_int, y_rec_int)
            rec_down = rg.Rectangle3d(self.o_plane, x_rec_int, y_rec_int)

            for top_pt in self.top_pts:
                value = rec_up.Contains(top_pt, self.top_pl)
                if (value == 2 or value == 0):
                    break
            else:
                self.bad_points = True
            for bot_pt in self.bot_pts:
                value = rec_down.Contains(bot_pt, self.bot_pl)
                if (value == 2 or value == 0):
                    break
            else:
                self.bad_points = True
        else:
            print "beam_line_intersection_collision requires some intersections"

    def beam_dowel_gen(self):
        pass

    def transform_to_other_plane(self, other_plane):
        self.transform_plane = other_plane
        trans = rg.Transform.PlaneToPlane(self.o_plane, other_plane)
        self.lines_transformed = []
        for line in self.local_int_lines:
            line_transformed = rg.LineCurve(line)
            line_transformed.Transform(trans)
            self.lines_transformed.append(line_transformed)

    def brep_subtraction(self, holes, plane = self.o_plane):
        self.brep_repr = self.generate_box(plane)
        for hole in holes:
            self.brep_repr = rg.Brep.CreateBooleanDifference(self.brep_repr, hole, 0.1)[0]
        return box_geom

    def gen_3D_geom(self, plane = self.o_plane):
        if (plane == self.o_plane):
            if (self.intersections_calculated):
                local_box = self.generate_box(self.o_plane)
                dowel = SimpleDowel(self.lines, self.rod_ds)
                dowel_postives = self.brep_subtraction(local_box, dowels)
            else:
                return self.generate_box(self.o_plane)
        else:
            if (self.intersections_calculated):
                return self.generate_box(self.transform_plane)

test_dowels = SimpleDowel(lines, rod_d).brep_representation()

# test_beam = SimpleBeam(origin_plane, size_x, size_y, size_z)
# test_beam.beam_line_intersection(lines)
# test_beam.transform_for_robot(o_2)
#
# for_robot = []
# for_robot.append(o_2)
# for_robot.extend(test_beam.lines_transformed)
#
# for_3Dprint = []
# for_3Dprint.append(test_beam.generate_geom_for_print())
# for_3Dprint.extend(test_beam.lines_transformed)
#
# display_geom.append(test_beam.geom)
