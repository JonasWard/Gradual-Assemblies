"""Provides a scripting component.
    Inputs:
        x: The x script variable
        y: The y script variable
    Output:
        a: The a output variable"""

__author__ = "ytakzk"
__version__ = "2019.02.26"

import Rhino.Geometry as rg
import os
import json
import compas_timber
from compas_timber.beam import Beam, BeamEnd, BeamSide 
from compas_timber.utilities import *
from compas.geometry import Plane
import math

class FabricatableBeam(object):

    def __init__(self, base_plane, dx, dy, dz, holes):

        """
        initialization

        :param base_plane:  base plane which the beam is along with
        :param dx:          the length along the local x-axis (= the length of this beam)
        :param dy:          the length along the local y-axis
        :param dz:          the length along the local z-axis
        :param holes:       the planes that define dowels
        """
        
        self.base_plane = base_plane
        self.dx = dx
        self.dy = dy
        self.dz = dz
        
        self.holes = holes
    
    def copy(self):

        holes = []

        for h in self.holes:

            holes.append(rg.Plane(h))
        
        base_plane = rg.Plane(self.base_plane)

        return FabricatableBeam(base_plane, self.dx, self.dy, self.dz, holes)
    
    def transform(self, transform):
        
        base_plane = rg.Plane(self.base_plane)
        base_plane.Transform(transform)
        
        holes = []
        
        for h in self.holes:
            
            hole = rg.Plane(h)
            hole.Transform(transform)
            holes.append(hole)
        
        return FabricatableBeam(base_plane, \
                self.dx, self.dy, self.dz, holes)
    
    def create_brep(self):
        
        x = rg.Interval(-self.dx * 0.5, self.dx * 0.5)
        y = rg.Interval(-self.dy * 0.5, self.dy * 0.5)
        z = rg.Interval(-self.dz * 0.5, self.dz * 0.5)
        
        return rg.Box(self.base_plane, x, y, z)
    
    def create_compas_beam(self):
        
        start_plane = rg.Plane(self.base_plane)
        start_plane.Translate(self.base_plane.XAxis * self.dx * 0.5)
    
        end_plane = rg.Plane(self.base_plane)
        end_plane.Translate(-self.base_plane.XAxis * self.dx * 0.5)
    
        e1 = BeamEnd(start_plane.Origin)
        e2 = BeamEnd(end_plane.Origin)
        
        normal = ([self.base_plane.ZAxis.X, self.base_plane.ZAxis.Y, self.base_plane.ZAxis.Z])
        
        compas_beam = Beam(e1, e2, self.dy, self.dz, normal)
        
        compas_beam.end1.cut_pln_explicit = Plane(start_plane.Origin, start_plane.XAxis)
        compas_beam.end2.cut_pln_explicit = Plane(end_plane.Origin, -end_plane.XAxis)
        
        return compas_beam
    
    def get_dowel_lines(self, extension=0):

        plane_1 = rg.Plane(self.base_plane)
        plane_1.Translate(self.base_plane.Normal * self.dz * 0.5)

        plane_2 = rg.Plane(self.base_plane)
        plane_2.Translate(-self.base_plane.Normal * self.dz * 0.5)

        lines = []
        
        for hole in self.holes:
                
            # get an infinite line
            DIFF = hole.Normal * 9999
            
            p1 = rg.Point3d.Add(hole.Origin, DIFF)
            p2 = rg.Point3d.Add(hole.Origin, -DIFF)
    
            dowel_line = rg.Line(p1, p2)
            
            succeeded, v1 = rg.Intersect.Intersection.LinePlane(dowel_line, plane_1)
            succeeded, v2 = rg.Intersect.Intersection.LinePlane(dowel_line, plane_2)
            
            p1 = dowel_line.PointAt(v1)
            p2 = dowel_line.PointAt(v2)
            
            line = rg.Line(p1, p2)

            diff = extension * 0.5
            
            line.Extend(diff, diff)
            lines.append(line)
        
        return lines
    
    @staticmethod
    def flip_whole_structure(beams):

        new_beams = []

        for b in beams:
            
            new_beam = b.copy()

            new_beam.base_plane = rg.Plane(b.base_plane.Origin, b.base_plane.XAxis, -b.base_plane.YAxis)

            for h in new_beam.holes:
                h.Flip()
            
            new_beams.append(new_beam)
        
        return new_beams

    @staticmethod
    def direct_all_beams(beams, base_plane):

        new_beams = []

        for b in beams:

            new_beam = b.copy()

            angle = rg.Vector3d.VectorAngle(new_beam.base_plane.Normal, base_plane.Normal)

            flip = False
            if math.pi * 0.5 < angle and angle < math.pi * 1.5:
                flip = True
            
            if flip:

                new_beam.base_plane = rg.Plane(b.base_plane.Origin, b.base_plane.XAxis, -b.base_plane.YAxis)

                for h in new_beam.holes:
                    h.Flip()
                
            new_beams.append(new_beam)
        
        return new_beams
    
    @staticmethod
    def instantiate_from_beam(beam):

        holes = []
        for d in beam.dowel_list:
            
            line = d.get_line(scale_value=1.2)
            
            suceeeded, val = rg.Intersect.Intersection.LinePlane(line, beam.base_plane)
            
            if not suceeeded:
                ValueError('No intersection found')
            
            p = line.PointAt(val)
            
            hole = rg.Plane(d.get_plane())
            hole.Origin = p

            # not to direct the normal of the hole to that of its beam base plane
            angle = rg.Vector3d.VectorAngle(beam.base_plane.Normal, hole.Normal)
            if math.pi * 0.5 < angle and angle < math.pi * 1.5:
                pass
            else:
                hole.Flip()
            
            holes.append(hole)
        
        return FabricatableBeam(beam.base_plane, \
            beam.dx + (beam.extension + beam.end_cover) * 2, beam.dy, beam.dz, holes)
            
    @staticmethod
    def write_as_json(beams, name='name', to='./data'):
        
        if not os.path.exists(to):
            os.makedirs(to)
        
        path = os.sep.join([to, str(name) + '.json'])
        
        data = []
        
        for b in beams:
            
            d = {
                'plane': FabricatableBeam.plane_to_dic(b.base_plane),
                'dx': b.dx,
                'dy': b.dy,
                'dz': b.dz,
            }
            
            d['holes'] = [FabricatableBeam.plane_to_dic(h) for h in b.holes]
            
            data.append(d)
        
        with open(path, 'w') as f:  
            json.dump(data, f)

    @staticmethod
    def read_from_json(path):
        
        beams = []
        
        with open(path, 'r') as f:
            data = json.load(f)
            
            for d in data: 
            
                dx = float(d['dx'])
                dy = float(d['dy'])
                dz = float(d['dz'])
                base_plane = FabricatableBeam.dic_to_plane(d['plane'])
                holes = [FabricatableBeam.dic_to_plane(dic) for dic in d['holes']]
                
                beam = FabricatableBeam(base_plane, dx, dy, dz, holes)
                beams.append(beam)
                
        return beams
        
    @staticmethod
    def plane_to_dic(plane):
        
        return {
            'x': plane.Origin.X,
            'y': plane.Origin.Y,
            'z': plane.Origin.Z,
            'xx': plane.XAxis.X,
            'xy': plane.XAxis.Y,
            'xz': plane.XAxis.Z,
            'yx': plane.YAxis.X,
            'yy': plane.YAxis.Y,
            'yz': plane.YAxis.Z
        }
        
    @staticmethod
    def dic_to_plane(dic):

        origin = rg.Point3d(float(dic['x']), float(dic['y']), float(dic['z']))
        xaxis = rg.Vector3d(float(dic['xx']), float(dic['xy']), float(dic['xz']))
        yaxis = rg.Vector3d(float(dic['yx']), float(dic['yy']), float(dic['yz']))

        return rg.Plane(origin, xaxis, yaxis) 
    
    @staticmethod
    def orient_structure(beams, src, target=rg.Plane.WorldXY):
        
        transform = rg.Transform.PlaneToPlane(src, target)
        
        transformed_beams = []
        
        for b in beams:
            
            beam = b.transform(transform)
            transformed_beams.append(beam)
        
        return transformed_beams