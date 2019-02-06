import Rhino.Geometry as rg
import ghpythonlib.components as gh 
import Grasshopper.Kernel.Data.GH_Path as ghpath
import Grasshopper.DataTree as datatree
import System
import math
import beam
import hole
import modular_beam
from dowel import Dowel


shift_ratio = 0.67
dowel_radius = 10

"""
Module class to contain three beams
"""
class Module(object):
    
    def __init__(self, middle_beam, side_beam_1, side_beam_2, depth=0, scale=1.0):
        
        self.middle_beam = middle_beam
        self.side_beam_1 = side_beam_1
        self.side_beam_2 = side_beam_2
        
        self.middle_beam.belongs_to(self)
        self.side_beam_1.belongs_to(self)
        self.side_beam_2.belongs_to(self)
        
        self.depth = depth
        self.scale = scale
        
        self.children = []
    
    def get_beams(self):
        
        return [self.middle_beam, self.side_beam_1, self.side_beam_2]
    
    def add_child(self, child):
        
        self.children.append(child)
    
    def add_dowels(self):
        
        b = self.middle_beam
        b1 = self.side_beam_1
        b2 = self.side_beam_2
        
        
        b_line = b.get_baseline().ToNurbsCurve()
        b1_line = b1.get_baseline().ToNurbsCurve()
        b2_line = b2.get_baseline().ToNurbsCurve()
        
        
        #splitting the curve to get the overlapping length (Middle Beam)
        b_line = gh.Shatter(b_line, shift_ratio)[1]
        print b_line.GetLength()
        b_rc = gh.EvaluateLength(b_line,90 * self.scale, False)[0]
        b_len_p = gh.EvaluateLength(b_line,90 * self.scale, False)[2]
        b_line = gh.Shatter(b_line,b_len_p)[1]
        print b_line.GetLength()
        
        b_top_line = rg.NurbsCurve(b_line)
        b_bottom_line = rg.NurbsCurve(b_line)
        
        #Translating the curve in both direction (Middle Beam)
        mb_offset_value = b.base_plane.YAxis * 20 * self.scale
        b_top_line.Translate(mb_offset_value)
        b_bottom_line.Translate(-mb_offset_value)
        print b_top_line, b_bottom_line
        
        #splitting the curve to get the overlapping length (Side Beam 1)
        b1_line = gh.Shatter(b1_line, shift_ratio)[0]
        print b1_line.GetLength()
        b1_rc = gh.EvaluateLength(b1_line,90 * self.scale, False)[0]
        b1_len_p = gh.EvaluateLength(b1_line,90 * self.scale, False)[2]
        b1_line = gh.Shatter(b1_line,b1_len_p)[1]
        print b1_line.GetLength()
        
        b1_top_line = rg.NurbsCurve(b1_line)
        b1_bottom_line = rg.NurbsCurve(b1_line)
        
        #Translating the curve in both direction (Side Beam 1)
        sb_offset_value = b1.base_plane.YAxis * 20 * self.scale
        b1_top_line.Translate(sb_offset_value)
        b1_bottom_line.Translate(-sb_offset_value)
        print b1_top_line, b1_bottom_line
        
        #splitting the curve to get the overlapping length (Side Beam 2)
        b2_line = gh.Shatter(b2_line, shift_ratio)[0]
        print b2_line.GetLength()
        b2_rc = gh.EvaluateLength(b2_line,90 * self.scale, False)[0]
        b2_len_p = gh.EvaluateLength(b2_line,90 * self.scale, False)[2]
        b2_line = gh.Shatter(b2_line,b2_len_p)[1]
        print b2_line.GetLength()
        
        b2_top_line = rg.NurbsCurve(b2_line)
        b2_bottom_line = rg.NurbsCurve(b2_line)
        
        #Translating the curve in both direction (Side Beam 2)
        sb_offset_value = b2.base_plane.YAxis * 20 * self.scale
        b2_top_line.Translate(sb_offset_value)
        b2_bottom_line.Translate(-sb_offset_value)
        print b2_top_line, b2_bottom_line
        
        
#        pts = [[b1_rc,b2_rc]]
        
#        for p1, p2 in pts:
            
#            line =rg.Line(p1,p2)
#            line.Extend(80,80)
#            dowel = Dowel(line=line, dowel_radius=dowel_radius)
#            for b in self.get_beams():
#                b.add_dowel(dowel)
            
        pts = [
            [b1_rc, b_rc ,b2_rc],
            [b1_top_line.PointAtLength(50.0 * self.scale + (self.depth*10 * self.scale)), b_top_line.PointAtLength(80.0 * self.scale + (self.depth*10 * self.scale)),b2_top_line.PointAtLength(100.0 * self.scale + (self.depth*10 * self.scale))],
            [b1_bottom_line.PointAtLength(100.0 * self.scale + (self.depth*10 * self.scale)), b_bottom_line.PointAtLength(80.0 * self.scale + (self.depth*10 * self.scale)),b2_bottom_line.PointAtLength(50.0 * self.scale + (self.depth*10 * self.scale))],
        ]
        
        for p1, p2, p3 in pts:
            
            line = gh.FitLine([p1,p2,p3])
            line.Extend(70 * self.scale,70 * self.scale)
            dowel = Dowel(line=line, dowel_radius=dowel_radius * self.scale)
            
            for b in self.get_beams():
                b.add_dowel(dowel)

    def brep(self, make_holes=False):
        
        return [b.brep_representation(make_holes = make_holes) for b in \
            [self.middle_beam, self.side_beam_1, self.side_beam_2]]

    @staticmethod
    def create_with_plane(base_plane, dx, dy, dz, shift_ratio):
        
        middle_beam = ModularBeam(base_plane, dx, dy, dz, shift_ratio, 0)

        side_plane_1 = rg.Plane(base_plane)
        side_plane_1.Translate(base_plane.XAxis * dx * shift_ratio)
        side_plane_1.Translate(base_plane.ZAxis * (dz + beam_gap))
        side_beam_1  = ModularBeam(side_plane_1, dx, dy, dz, shift_ratio, 1)

        side_plane_2 = rg.Plane(base_plane)
        side_plane_2.Translate(base_plane.XAxis * dx * shift_ratio)
        side_plane_2.Translate(-base_plane.ZAxis * (dz + beam_gap))
        side_beam_2  = ModularBeam(side_plane_2, dx, dy, dz, shift_ratio, 1)
        
        return Module(middle_beam, side_beam_1, side_beam_2, 0)

    @staticmethod
    def create_with_beam(beam, depth):
        
        base_plane = beam.base_plane
        dx, dy, dz = beam_dx, beam.dy, beam.dz

        side_plane_1 = rg.Plane(base_plane)
        side_plane_1.Translate(base_plane.XAxis * dx * beam.shift_ratio)
        side_plane_1.Translate(base_plane.ZAxis * (dz + beam_gap))
        side_beam_1  = ModularBeam(side_plane_1, dx, dy, dz, beam.shift_ratio, beam.depth + 1)

        side_plane_2 = rg.Plane(base_plane)
        side_plane_2.Translate(base_plane.XAxis * dx * beam.shift_ratio)
        side_plane_2.Translate(-base_plane.ZAxis * (dz + beam_gap))
        side_beam_2  = ModularBeam(side_plane_2, dx, dy, dz, beam.shift_ratio, beam.depth + 1)
        
        return Module(beam, side_beam_1, side_beam_2, depth)

    def get_modules_in_family(self):
        
        modules = []
        
        def add(parent):
            
            modules.append(parent)
            
            for child in parent.children:
                
                if child.middle_beam.alive:
                    add(child)

        add(self)

        modules = list(set(modules))
        
        return sorted(modules, key=lambda m: m.depth)
        
    def get_beams_in_family(self):
        
        beams = []
        
        def add(parent):
            
            beams.extend(parent.get_beams())

            for child in parent.children:
                
                if child.middle_beam.alive:
                    add(child)

        add(self)
        
        filtered_beams = []
        
        for i, beam_1 in enumerate(beams):
            
            duplicated = False
            for beam_2 in beams[i+1:]:
                
                if beam_1 == beam_2:
                    duplicated = True
                    break
                    
            if not duplicated:
                filtered_beams.append(beam_1)

        return sorted(filtered_beams, key=lambda b: b.depth)
