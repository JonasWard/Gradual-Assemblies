'''
Created on 07.01.2019
update by JonasWard 10.01.2019

@author: jennyd, JonasWard
'''


import rhinoscriptsyntax as rs
import math as m

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

    def generate_box(self, plane = self.o_plane):
        x_interval = rg.Interval(- self.size_x * 0.5, self.size_x * .5)
        y_interval = rg.Interval(- self.size_y * 0.5, self.size_y * .5)
        z_interval = rg.Interval(- self.size_z * 0.5, self.size_z * .5)
        local_box = rg.Box(self.o_plane, x_interval, y_interval, z_interval)
        return local_box

    def beam_in_base_position(self):
        return generate_box(self, plane = xy_plane)

    def beam_line_intersection(self, lines):
        top_pl, bot_pl = rg.Plane(self.o_plane), rg.Plane(self.o_plane)
        move_up, move_down = rg.Vector3d(self.o_plane.Normal), rg.Vector3d(self.o_plane.Normal)
        move_up *= .5 * self.size_z
        move_down *= - .5 * self.size_z
        top_pl.Translate(move_up)
        bot_pl.Translate(move_down)

        self.top_pts, self.bottom_pts = [], []

        self.local_int_lines = []

        for line in lines:
            ign, top_pt_p = rg.Intersect.Intersection.LinePlane(line, top_pl)
            ign, bot_pt_p = rg.Intersect.Intersection.LinePlane(line, bot_pl)
            self.top_pts.append(rg.line.PointAt(top_pt_p))
            self.bottom_pts.append(rg.line.PointAt(bot_pt_p))

            self.local_int_lines.append(Line)
