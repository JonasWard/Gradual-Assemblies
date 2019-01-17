import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import math as m

temp_geom = []
temp_lines = []
planes_trans = []
hole_planes = []

class SimpleBeam(object):
    """Simple Beam class for Timber Assemblies.
    """
    def __init__(self, origin_plane, size_x = 1500, size_y = 120, size_z = 40):
        self.o_p = origin_plane
        self.s_x = size_x
        self.s_y = size_y
        self.s_z = size_z

        self.geom = []
        self.generate_box()
        self.generate_connection_points()

    def generate_box(self):
        """Generates a simple box defining the volume of the beam with center point at the origin plane.
        """
        temp_box = rg.Box(self.o_p, rg.Interval(-self.s_x*0.5,self.s_x*0.5), rg.Interval(-self.s_y*0.5,self.s_y*0.5), rg.Interval(-self.s_z*0.5,self.s_z*0.5))
        self.geom.append(temp_box)

    def generate_connection_points(self):
        """Generates two list for connection points, one at bottom one at top surface of the beam.
        """
        start_pt = self.o_p.Origin - self.o_p.XAxis * self.s_x*0.4 - self.o_p.ZAxis * self.s_z*0.5
        end_pt = self.o_p.Origin + self.o_p.XAxis * self.s_x*0.4 - self.o_p.ZAxis * self.s_z*0.5
        bottom_line = rg.LineCurve(start_pt, end_pt)
        bottom_params = bottom_line.DivideByCount(10, True)
        self.bottom_pts = [bottom_line.PointAt(p) for p in bottom_params]

        start_pt = self.o_p.Origin - self.o_p.XAxis * self.s_x*0.4 + self.o_p.ZAxis * self.s_z*0.5
        end_pt = self.o_p.Origin + self.o_p.XAxis * self.s_x*0.4 + self.o_p.ZAxis * self.s_z*0.5
        top_line = rg.LineCurve(start_pt, end_pt)
        top_params = top_line.DivideByCount(10, True)
        self.top_pts = [top_line.PointAt(p) for p in top_params]

        temp_geom.extend(self.bottom_pts)
        temp_geom.extend(self.top_pts)

    def connect_beam(self, other_beam):
        for i,pt in enumerate(self.bottom_pts):
            distance = pt.DistanceTo(other_beam.top_pts[i])
            if distance < 250:
                #print "in"
                dowel_line = rg.Line(pt,other_beam.top_pts[i])
                temp_lines.append(dowel_line)
                line_normal = rg.Vector3d.Subtract(rg.Vector3d(pt),rg.Vector3d(other_beam.top_pts[i]))
                line_plane = rg.Plane(pt, line_normal)
                hole_planes.append(line_plane)
            #print distance

    def generate_drillplanes(self, beam_plane, list_hole_planes, drill_plane):
        self.b_p = beam_plane
        self.h_p = list_hole_planes
        self.d_p = drill_plane

        # generates drilling planes
        for i,pl in enumerate(self.h_p):
            trans = rg.Transform.PlaneToPlane(pl, self.d_p)
            plane_trans = rg.Plane(self.b_p)
            rg.Plane.Transform(plane_trans, trans)
            rg.Plane.Flip(plane_trans)
            planes_trans.append(plane_trans)

test_beam = SimpleBeam(origin_plane, size_x, size_y, size_z)

o_plane = rg.Plane(origin_plane)
o_plane.Translate(o_plane.ZAxis * 50)
o_plane.Rotate(m.radians(rot), o_plane.ZAxis,o_plane.Origin)
test_beam_2 = SimpleBeam(o_plane, size_x, size_y, size_z)

test_beam.connect_beam(test_beam_2)
test_beam.generate_drillplanes(origin_plane, hole_planes, drill_plane)

temp_geom.extend(test_beam.geom)
temp_geom.extend(test_beam_2.geom)

print planes_trans
