'''
Created on 07.01.2019
update by Wenqian157 14.01.2019

@author: jennyd, JonasWard, Wenqian157
'''

import Rhino.Geometry as rg
import math as m
# import rhinoscriptsyntax as rs

class SimpleDowel(object):
    # simple dowel class for Timner Assemblies

    def __init__(self, line, rod_d):
        self.r = rod_d / 2
        self.d = rod_d
        self.line = line

        self.safety_l = 1.0

    def placement_frame_gen(self):
        start_pt = self.line.PointAt(0.0)
        end_pt = self.line.PointAt(1.0)
        frame_normal = rg.Vector3d(end_pt - start_pt)

        self.base_pl = rg.Plane(start_pt, frame_normal)
        self.top_pl = rg.Plane(end_pt, frame_normal)

    def brep_representation(self):
        flat = rg.PipeCapMode.Flat
        brep = rg.Brep.CreatePipe(rg.LineCurve(self.line), self.r, False, flat, False, .01, .01)
        return brep

class SimpleBeam(object):
    # simple beam class for Timber Assemblies

    def __init__(self, o_plane, s_x = 1500, s_y = 20, s_z = 40):
        self.o_plane = o_plane
        self.size_x = s_x
        self.size_y = s_y
        self.size_z = s_z

        self.box_geom = self.generate_box()
        # statement to indicate that no intersections have been calculated yet
        self.intersections_calculated = False
        # statement to indicate that there are no wrongly place holes
        self.bad_points = True
        # statement to indicate that the 3d geometry - so with boolean difference
        # hasn't been generated yet
        self.gen_3d_gem = False

        self.safety_l = 2.0

    def interval_gen(self, range, offset = 0):
        value = range * .5 - offset
        return rg.Interval(-value, value)

    def generate_box(self, plane = False):
        if not plane:
            plane = self.o_plane

        self.x_int = self.interval_gen(self.size_x)
        self.y_int = self.interval_gen(self.size_y)
        self.z_int = self.interval_gen(self.size_z)
        local_box = rg.Box(plane, self.x_int, self.y_int, self.z_int)
        return local_box

    def calculate_midpoint(self, point_a, point_b):
        distance = point_a.DistanceTo(point_b)
        x1, y1, z1 = point_a.X, point_a.Y, point_a.Z
        x2, y2, z2 = point_b.X, point_b.Y, point_b.Z
        return rg.Point3d((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2), distance

    def beam_line_intersection(self, dowels, coll_off_w = 0, coll_off_l = 0):
        # generating the top & bottom plane of a beam
        self.top_pl, self.bot_pl = rg.Plane(self.o_plane), rg.Plane(self.o_plane)
        move_up = rg.Vector3d(self.o_plane.Normal)
        move_down = rg.Vector3d(self.o_plane.Normal)
        move_up *= .5 * self.size_z
        move_down *= - .5 * self.size_z
        self.top_pl.Translate(move_up)
        self.bot_pl.Translate(move_down)

        # setting up global variables
        self.dow_top_pls, self.dow_bot_pls, self.dow_r = [], [], []
        self.dow_lines, self.dow_rad = [], []

        for dowel in dowels:
            line = dowel.line
            r = dowel.r

            temp, top_pt_p = rg.Intersect.Intersection.LinePlane(line, self.top_pl)
            top_pt_p = line.PointAt(top_pt_p)
            temp, bot_pt_p = rg.Intersect.Intersection.LinePlane(line, self.bot_pl)
            bot_pt_p = line.PointAt(bot_pt_p)

            # implementing a scale_up to the geometry to allow for full overlap
            # with the bottom & top plane
            center_pt, dis = self.calculate_midpoint(top_pt_p, bot_pt_p)

            normal = self.o_plane.Normal
            vector = rg.Vector3d(rg.Point3d.Subtract(top_pt_p, bot_pt_p))
            alfa = m.pi / 2 - rg.Vector3d.VectorAngle(vector, normal)
            local_l = (self.size_z + r / m.tan(alfa) - 2 * self.safety_l - dis) / (dis * 2.0)
            top_pt_p -= rg.Vector3d(vector) * local_l
            bot_pt_p += rg.Vector3d(vector) * local_l

            top_pl = rg.Plane(top_pt_p, vector)
            bot_pl = rg.Plane(bot_pt_p, vector)

            self.dow_rad.append(r)
            self.dow_top_pls.append(top_pl)
            self.dow_bot_pls.append(bot_pl)
            self.dow_lines.append(rg.Line(top_pt_p,bot_pt_p))

        # indicating that the intersections have been calculated
        self.intersections_calculated = True
        self.intersections_count = len(self.dow_lines)

    # def beam_line_intersection_collision(self, coll_off_w = 0, coll_off_l = 0):
    #     if (self.intersections_calculated):
    #         x_rec_int = self.interval_gen(self.size_x, coll_off_w)
    #         y_rec_int = self.interval_gen(self.size_y, coll_off_l)
    #         rec_up = rg.Rectangle3d(self.o_plane, x_rec_int, y_rec_int)
    #         rec_down = rg.Rectangle3d(self.o_plane, x_rec_int, y_rec_int)
    #
    #         for top_pt in self.top_pts:
    #             value = rec_up.Contains(top_pt, self.top_pl)
    #             if (value == 2 or value == 0):
    #                 break
    #         else:
    #             self.bad_points = True
    #         for bot_pt in self.bot_pts:
    #             value = rec_down.Contains(bot_pt, self.bot_pl)
    #             if (value == 2 or value == 0):
    #                 break
    #         else:
    #             self.bad_points = True
    #     else:
    #         print "beam_line_intersection_collision requires some intersections"

    def beam_dowel_gen(self):
        pass

    def transform_to_other_plane(self, other_plane = rg.Plane.WorldXY):
        self.trans_dow_line, self.trans_dow_top_pls, self.trans_dow_bot_pls = [], [], []

        self.trans_box = self.generate_box(other_plane)
        self.trans_plane = other_plane

        self.transform_plane = other_plane
        trans_matrix = rg.Transform.PlaneToPlane(self.o_plane, other_plane)

        for i in range(self.intersections_count):
            trans_line = rg.LineCurve(self.dow_lines[i])
            trans_top_pl = rg.Plane(self.dow_top_pls[i])
            trans_bot_pl = rg.Plane(self.dow_bot_pls[i])
            trans_line.Transform(trans_matrix)
            trans_top_pl.Transform(trans_matrix)
            trans_bot_pl.Transform(trans_matrix)
            self.trans_dow_line.append(trans_line)
            self.trans_dow_top_pls.append(trans_top_pl)
            self.trans_dow_bot_pls.append(trans_bot_pl)

        print self.gen_3d_gem

        if self.gen_3d_gem:
            self.trans_brep_repr = self.brep_repr.Duplicate()
            self.trans_brep_repr.Transform(trans_matrix)

    def transform_to_drill_plane(self, drill_plane = False, safety_plane_distance = 50):
        print drill_plane
        if not drill_plane:
            drill_plane = rg.Plane.WorldXY

        self.drill_plane = drill_plane

        self.drill_top_pls, self.drill_bot_pls, self.drill_safety_pls = [], [], []
        self.drill_top_box, self.drill_bot_box = [], []

        for top_pl in self.dow_top_pls:
            trans_matrix = rg.Transform.PlaneToPlane(top_pl, drill_plane)
            drill_top_pl = rg.Plane(self.o_plane)
            drill_top_box = self.generate_box()
            drill_top_pl.Transform(trans_matrix)
            drill_top_box.Transform(trans_matrix)
            self.drill_top_pls.append(drill_top_pl)
            self.drill_top_box.append(drill_top_box)

        for bot_pl in self.dow_bot_pls:
            trans_matrix = rg.Transform.PlaneToPlane(bot_pl, drill_plane)

            drill_bot_pl = rg.Plane(self.o_plane)
            drill_bot_box = self.generate_box()
            drill_bot_pl.Transform(trans_matrix)
            drill_bot_box.Transform(trans_matrix)
            self.drill_bot_pls.append(drill_bot_pl)
            self.drill_bot_box.append(drill_bot_box)

            safety_pl = rg.Plane(bot_pl)
            normal_vector = rg.Vector3d(safety_pl.Normal)
            safety_pl.Translate(-safety_plane_distance * normal_vector)

            trans_matrix = rg.Transform.PlaneToPlane(safety_pl, drill_plane)
            drill_safety_plane = rg.Plane(self.o_plane)
            drill_safety_plane.Transform(trans_matrix)
            self.drill_safety_pls.append(drill_safety_plane)

    def brep_generator(self):
        # this is by far the most time consuming component!
        # only generate it when you need it
        brep_repr = self.generate_box().ToBrep()

        for i in range(self.intersections_count):
            hole = SimpleDowel(self.dow_lines[i], self.dow_rad[i]).brep_representation()
            brep_repr_new = rg.Brep.CreateBooleanDifference([brep_repr], hole, 0.1)
            brep_repr = brep_repr_new[0]

        self.brep_repr = brep_repr
        self.gen_3d_gem = True
        return brep_repr

test_dowels = []

# for line in lines:
#     test_dowels.append(SimpleDowel(line, rod_d))

test_box_ref_1 = []
for i in range (len(origin_plane)):
    ref = SimpleBeam(origin_plane[i], size_x, size_y, size_z)
    test_box_ref_1.append(ref)
    box_rep = ref.generate_box()

# test_box_ref_1.beam_line_intersection(test_dowels)
# test_box_ref_1.transform_to_drill_plane(drill_plane)

test_box = []
for i in range (len(origin_plane)):
    test_box.append(test_box_ref_1[i].generate_box())

# hole_box = test_box_ref_1.brep_generator()
# top_pls = test_box_ref_1.drill_top_pls
# bot_pls = test_box_ref_1.drill_bot_pls
# safety_pls = test_box_ref_1.drill_safety_pls
#
# boxes_top = test_box_ref_1.drill_top_box
# boxes_bot = test_box_ref_1.drill_bot_box
# test_box_0 = test_box_ref_1.trans_brep_repr
# test_box_0_lines = test_box_ref_1.dow_lines
# test_box_ref_2 = SimpleBeam(origin_plane[1], size_x, size_y, size_z)
# test_box_ref_2.beam_line_intersection(test_dowels)
# test_box_1 = test_box_ref_2.generate_box()

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
