'''
Created on 07.01.2019
update by Wenqian157 14.01.2019

@author: jennyd, JonasWard, Wenqian157
'''

import Rhino.Geometry as rg
# import rhinoscriptsyntax as rs

class SimpleDowel(object):
    # simple dowel class for Timner Assemblies

    def __init__(self, o_plane, rod_d, length):
        self.o_plane = o_plane
        self.rod_r = rod_d / 2
        self.rod_d = rod_d
        self.l = length

        # variable indicating that the line_representation has not been generated
        self.line_rep_gen = False

    def line_representation(self):
        if (self.line_rep_gen):
            return self.line
        else:
            n_v3d = rg.Vector3d(self.o_plane.Normal)
            l_v3d = n_v3d * self.l
            o_p3d = rg.Point3d(self.o_plane.Origin)
            end_p3d = rg.Point3d(o_p3d).Translate(l_v3d)

            self.line = rg.LineCurve(o_p3d, end_p3d)

            return self.line
            self.line_rep_gen = True

    def brep_representation(self):
        if (self.line_rep_gen):
            brep = rg.Brep.CreatePipe(self.line, self.rod_r, False, 1)
            return brep
        else:
            self.line_representation(self)
            brep = rg.Brep.CreatePipe(self.line, self.rod_r, False, 1)
            return brep

class SimpleBeam(object):
    # simple beam class for Timber Assemblies

    def __init__(self, o_plane, s_x = 1500, s_y = 20, s_z = 40):
        self.o_plane = o_plane
        self.size_x = s_x
        self.size_y = s_y
        self.size_z = s_z

        self.geom = self.generate_box(self.o_plane)

        # statement to indicate that no intersections have been calculated yet
        self.intersection_calculated = False
        # statement to indicate that there are no wrongly place holes
        self.bad_points = True

    def interval_gen(self, range, offset = 0):
        value = range * .5 - offset
        return rg.Interval(-value, value)

    def generate_box(self, plane):
        self.x_int = self.interval_gen(size_x)
        self.y_int = self.interval_gen(size_y)
        self.z_int = self.interval_gen(size_z)
        local_box = rg.Box(plane, self.x_int, self.y_int, self.z_int)
        return local_box

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
        self.top_pts, self.bot_pts, self.dowel_d = [], [], []
        self.local_int_lines = []

        for dowel in dowels:
            line = dowel.line_representation()

            temp, top_pt_p = rg.Intersect.Intersection.LinePlane(line, self.top_pl)
            temp, bot_pt_p = rg.Intersect.Intersection.LinePlane(line, self.bot_pl)

            self.dowel_d.append(dowel.rod_d)
            self.top_pts.append(line.PointAt(top_pt_p))
            self.bot_pts.append(line.PointAt(bot_pt_p))
            self.local_int_lines.append(rg.Line(line.PointAt(top_pt_p),line.PointAt(bot_pt_p)))

        # indicating that the intersections have been calculated
        self.intersection_calculated = True

    def beam_line_intersection_collision(self, coll_off_w = 0, coll_off_l = 0):
        if (self.intersection_calculated):
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

    def transform_to_other_plane(self, other_plane):
        self.transform_plane = other_plane
        trans = rg.Transform.PlaneToPlane(self.o_plane, other_plane)
        self.lines_transformed = []
        for line in self.local_int_lines:
            line_transformed = line
            line_transformed.Transform(trans)
            self.lines_transformed.append(line_transformed)

    def gen_3D_geom(self, plane = self.o_plane):
        return self.generate_box(self.transform_plane)

test_beam = SimpleBeam(origin_plane, size_x, size_y, size_z)
test_beam.beam_line_intersection(lines)
test_beam.transform_for_robot(o_2)

for_robot = []
for_robot.append(o_2)
for_robot.extend(test_beam.lines_transformed)

for_3Dprint = []
for_3Dprint.append(test_beam.generate_geom_for_print())
for_3Dprint.extend(test_beam.lines_transformed)

display_geom.append(test_beam.geom)
