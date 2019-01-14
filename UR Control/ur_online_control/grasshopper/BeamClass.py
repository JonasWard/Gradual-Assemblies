'''
Created on 07.01.2019
update by Wenqian157 14.01.2019

@author: jennyd, JonasWard, Wenqian157
'''

import Rhino.Geometry as rg
import rhinoscriptsyntax as rs

display_geom = []

class SimpleBeam(object):
    # simple beam class for Timber Assemblies

    def __init__(self, origin_plane, size_x = 1500, size_y = 20, size_z = 40):
        self.o_plane = origin_plane
        self.size_x = size_x
        self.size_y = size_y
        self.size_z = size_z

        self.geom = self.generate_box(self.o_plane)
        self.lines_transformed = []

    def interval_gen(self, range, offset = 0):
        value = range * .5 - offset
        return rg.Interval(-value, value)


    def generate_box(self, plane):
        self.x_int = self.interval_gen(size_x)
        self.y_int = self.interval_gen(size_y)
        self.z_int = self.interval_gen(size_z)
        local_box = rg.Box(plane, self.x_int, self.y_int, self.z_int)
        return local_box

    def beam_line_intersection(self, lines, coll_off_w = 0, coll_off_l = 0):
        top_pl, bot_pl = rg.Plane(self.o_plane), rg.Plane(self.o_plane)
        move_up = rg.Vector3d(self.o_plane.Normal)
        move_down = rg.Vector3d(self.o_plane.Normal)
        move_up *= .5 * self.size_z
        move_down *= - .5 * self.size_z
        top_pl.Translate(move_up)
        bot_pl.Translate(move_down)

        self.top_pts, self.bottom_pts = [], []
        x_rec_int = self.interval_gen(self.size_x, coll_off_w)
        y_rec_int = self.interval_gen(self.size_y, coll_off_l)
        rec_up = rg.Rectangle3d(self.o_plane, x_rec_int, y_rec_int)
        rec_down = rg.Rectangle3d(self.o_plane, x_rec_int, y_rec_int)
        self.local_int_lines = []

        for line in lines:
            temp, top_pt_p = rg.Intersect.Intersection.LinePlane(line, top_pl)
            temp, bot_pt_p = rg.Intersect.Intersection.LinePlane(line, bot_pl)
            self.top_pts.append(line.PointAt(top_pt_p))
            self.bottom_pts.append(line.PointAt(bot_pt_p))
            self.local_int_lines.append(rg.Line(line.PointAt(top_pt_p),line.PointAt(bot_pt_p)))

    def transform_for_robot(self, other_plane):
        self.transform_plane = other_plane
        trans = rg.Transform.PlaneToPlane(self.o_plane, other_plane)
        lines_transformed = []
        for line in self.local_int_lines:
            line_transformed = line
            line_transformed.Transform(trans)
            self.lines_transformed.append(line_transformed)

    def generate_geom_for_print(self):
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
