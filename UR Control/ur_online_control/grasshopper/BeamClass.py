'''
Created on 07.01.2019
update by JonasWard 13.01.2019

@author: jennyd, JonasWard
'''

import Rhino.Geometry as rg

xy_plane = rg.Plane(rg.Point3d(0,0,0), rg.Vector3d(0,0,1))

class SimpleBeam(object):
    """simple beam class for Timber Assemblies"""
    """"""
    def __init__(self, o_plane, size_x = 1500, size_y = 20, size_z = 40):
        self.o_plane = origin_plane
        self.o_plane.Normal.Unitize
        self.size_x = size_x
        self.size_y = size_y
        self.size_z = size_z

        self.geom = self.generate_box()
        self.bottom_pts, self.top_pts = self.generate_connection_points()

    def interval_gen(range, offset = 0):
        value = range * .5 - offset
        minimum_val = - value
        maximum_val = value
        return rg.Interval(minimum_val, maximum_val)

    def generate_box(self, plane = self.o_plane):
        self.x_int = interval_gen(size_x)
        self.y_int = interval_gen(size_y)
        self.z_int = interval_gen(size_z)
        local_box = rg.Box(self.o_plane, self.x_int, self.y_int, self.z_int)
        return local_box

    def beam_in_base_position(self):
        return generate_box(self, plane = xy_plane)

    def beam_line_intersection(self, lines, coll_off_w = 0, coll_off_l = 0):
        top_pl, bot_pl = rg.Plane(self.o_plane), rg.Plane(self.o_plane)
        move_up = rg.Vector3d(self.o_plane.Normal)
        move_down = rg.Vector3d(self.o_plane.Normal)
        move_up *= .5 * self.size_z
        move_down *= - .5 * self.size_z
        top_pl.Translate(move_up)
        bot_pl.Translate(move_down)

        self.top_pts, self.bottom_pts = [], []
        x_rec_int = interval_gen(self.size_x, coll_off_w)
        y_rec_int = interval_gen(self.size_y, coll_off_l)
        rec_up = rg.Rectangle3d(self.o_plane, x_rec_int, y_rec_int)
        rec_down = rg.Rectangle3d(self.o_plane, x_rec_int, y_rec_int)
        self.local_int_lines = []

        for line in lines:
            temp, top_pt_p = rg.Intersect.Intersection.LinePlane(line, top_pl)
            temp, bot_pt_p = rg.Intersect.Intersection.LinePlane(line, bot_pl)
            self.top_pts.append(rg.line.PointAt(top_pt_p))
            self.bottom_pts.append(rg.line.PointAt(bot_pt_p))

            self.local_int_lines.append(Line)
