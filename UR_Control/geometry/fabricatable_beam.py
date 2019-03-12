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

    def __init__(self, base_plane, dx, dy, dz, holes, has_pockets=False, has_dowel_holes=True, has_annoying_pockets=False, is_shitty_beam=False):

        """
        initialization
        :param base_plane:              base plane which the beam is along with
        :param dx:                      the length along the local x-axis (= the length of this beam)
        :param dy:                      the length along the local y-axis
        :param dz:                      the length along the local z-axis
        :param holes:                   the planes that define dowels
        :param has_pockets:             the planes that define dowels
        :param has_dowel_holes:         the planes that define dowels
        :param has_annoying_pockets:    the planes that define dowels
        :param is_shitty_beam:          beam has to be cut under an angle (default = False)
        """
        
        self.base_plane = base_plane
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.has_pockets = has_pockets
        self.has_dowel_holes = has_dowel_holes
        self.has_annoying_pockets = has_annoying_pockets
        self.is_shitty_beam = is_shitty_beam 

        self.holes = holes
    
    def copy(self):

        holes = []

        for h in self.holes:

            holes.append(rg.Plane(h))
        
        base_plane = rg.Plane(self.base_plane)

        return FabricatableBeam(base_plane, self.dx, self.dy, self.dz, holes, self.has_pockets, self.has_dowel_holes, self.has_annoying_pockets, self.is_shitty_beam)
    
    def transform(self, transform):
        
        base_plane = rg.Plane(self.base_plane)
        base_plane.Transform(transform)
        
        holes = []
        
        for h in self.holes:
            
            hole = rg.Plane(h)
            hole.Transform(transform)
            holes.append(hole)
        
        return FabricatableBeam(base_plane, \
                self.dx, self.dy, self.dz, holes, self.has_pockets, self.has_dowel_holes, self.has_annoying_pockets, self.is_shitty_beam)
    
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

    def get_screw_holes(self, flip = False):
        """ Annoying hole class

        :param flip:        Whether the beam is flipped around it's z-axis or not
        :return line_set:   Dowel line representation set
        :return pln_set:    Dowel plane set
        """

        beam = self

        # drill parameters
        drill_angle = 55            # in reference to the plain
        drill_depth = 20            # length drill line in wood
        drill_start_tolerance = 1   # extension drill line outside of the beam
        x_spacing = 30              # how much x deviates from the average position
        y_spacing = 30


        # getting the average location of the start & end joint groups on the beam
        dowel_pts = [dowel.Origin for dowel in beam.holes]
        beam_origin = beam.base_plane.Origin
        beam_origin_x = beam_origin.X

        # getting the even spacing in between the dowel_lines
        new_line_neg = 0.0
        new_line_neg_count = 0
        new_line_pos = 0.0
        new_line_pos_count = 0

        # seperating and tallying up the negative from the positive values
        for dowel_pt in dowel_pts:
            if dowel_pt.X - beam_origin_x > 0:
                new_line_pos_count += 1
                new_line_pos += dowel_pt.X - beam_origin_x
            else:
                new_line_neg_count += 1
                new_line_neg += dowel_pt.X - beam_origin_x

        # average x locations of the joints on the beam
        start_x = new_line_neg / new_line_neg_count
        end_x = new_line_pos / new_line_pos_count
        delta_x = end_x - start_x

        spacing_x = delta_x * .25
        
        print "spacing_x before correction", spacing_x
        if spacing_x < 230.0:
            spacing_x = 230
            
        print "spacing_x after correction", spacing_x

        # setting the raw locations where the holes should be
        neg_x_loc = start_x + spacing_x
        pos_x_loc = end_x - spacing_x

        y_delta = math.cos(math.radians(drill_angle))
        z_delta = math.sin(math.radians(drill_angle))

        # locations on the beam
        int_y_coordinate = beam.dy * .5 - y_spacing
        int_z_coordinate = beam.dz * .5

        # locations in the beam
        bot_y_coordinate = int_y_coordinate - y_delta * drill_depth
        bot_z_coordinate = int_z_coordinate - z_delta * drill_depth
        
        print bot_z_coordinate, bot_y_coordinate

        # locations outside of the beam
        top_y_coordinate = int_y_coordinate + y_delta * drill_start_tolerance
        top_z_coordinate = int_z_coordinate + z_delta * drill_start_tolerance

        # setting up all the point_set
        #    ---------------------------------------------------
        #   |     o     ln_0 -> *          * <- ln_1      o     |
        #   |  o    o       --------------------        o    o  |
        #   |    o      * <- ln_2      -   ln_3 -> *       o    |
        #    ---------------------------------------------------

        # ln_0
        # pt inside the beam
        x0 = neg_x_loc + x_spacing
        y0 = bot_y_coordinate
        z0 = bot_z_coordinate
        pt_0 = rg.Point3d(x0, y0, z0)
        # pt outside the beam
        x1 = neg_x_loc + x_spacing
        y1 = top_y_coordinate
        z1 = top_z_coordinate
        pt_1 = rg.Point3d(x1, y1, z1)
        ln_0 = rg.Line(pt_1, pt_0)
        pl_0 = rg.Plane(pt_1, rg.Vector3d(pt_0 - pt_1))

        # ln_1
        # pt inside the beam
        x0 = pos_x_loc - x_spacing
        y0 = bot_y_coordinate
        z0 = bot_z_coordinate
        pt_0 = rg.Point3d(x0, y0, z0)
        # pt outside the beam
        x1 = pos_x_loc - x_spacing
        y1 = top_y_coordinate
        z1 = top_z_coordinate
        pt_1 = rg.Point3d(x1, y1, z1)
        ln_1 = rg.Line(pt_1, pt_0)
        pl_1 = rg.Plane(pt_1, rg.Vector3d(pt_0 - pt_1))

        # ln_2
        # pt inside the beam
        x0 = neg_x_loc - x_spacing
        y0 = - bot_y_coordinate
        z0 = bot_z_coordinate
        pt_0 = rg.Point3d(x0, y0, z0)
        # pt outside the beam
        x1 = neg_x_loc - x_spacing
        y1 = - top_y_coordinate
        z1 = top_z_coordinate
        pt_1 = rg.Point3d(x1, y1, z1)
        ln_2 = rg.Line(pt_1, pt_0)
        pl_2 = rg.Plane(pt_1, rg.Vector3d(pt_0 - pt_1))

        # ln_3
        # pt inside the beam
        x0 = pos_x_loc + x_spacing
        y0 = - bot_y_coordinate
        z0 = bot_z_coordinate
        pt_0 = rg.Point3d(x0, y0, z0)
        # pt outside the beam
        x1 = pos_x_loc + x_spacing
        y1 = - top_y_coordinate
        z1 = top_z_coordinate
        pt_1 = rg.Point3d(x1, y1, z1)
        ln_3 = rg.Line(pt_1, pt_0)
        pl_3 = rg.Plane(pt_1, rg.Vector3d(pt_0 - pt_1))
        
        line_set = [ln_0, ln_1, ln_2, ln_3]
        pln_set = [pl_0, pl_1, pl_2, pl_3]

        # flip around world xy plane
        if flip:
            mirror_transform = rg.Transform.Mirror(rg.Plane.WorldXY)
            [line.Transform(mirror_transform) for line in line_set]
            [plane.Transform(mirror_transform) for plane in pln_set]
        
        translate_to_origin_beam = rg.Transform.Translation(rg.Vector3d(beam_origin))
        
        [line.Transform(translate_to_origin_beam) for line in line_set]
        [pln.Transform(translate_to_origin_beam) for pln in pln_set]
        
        return line_set, pln_set

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
    def instantiate_from_beam(beam, has_pockets=False, has_dowel_holes=True, has_annoying_pockets=False, is_shitty_beam=False):

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
            beam.dx + (beam.extension + beam.end_cover) * 2, beam.dy, beam.dz, holes, has_pockets, has_dowel_holes, has_annoying_pockets, is_shitty_beam)
            
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
                'has_pockets': 1 if b.has_pockets else 0,
                'has_dowel_holes': 1 if b.has_dowel_holes else 0,
                'has_annoying_pockets': 1 if b.has_annoying_pockets else 0,
                'is_shitty_beam': 1 if b.is_shitty_beam else 0
            }
            
            d['holes'] = [FabricatableBeam.plane_to_dic(h) for h in b.holes]
            
            data.append(d)
        
        with open(path, 'w') as f:  
            json.dump(data, f)

    @staticmethod
    def read_from_json(path, scale=1.0):
        
        beams = []
        
        with open(path, 'r') as f:
            data = json.load(f)
            
            for d in data: 
            
                dx = float(d['dx'])
                dy = float(d['dy'])
                dz = float(d['dz'])
                has_pockets = True if int(d['has_pockets']) == 1 else False
                has_dowel_holes = True if int(d['has_dowel_holes']) == 1 else False
                has_annoying_pockets = True if 'has_annoying_pockets' in d and int(d['has_annoying_pockets']) == 1 else False
                is_shitty_beam = True if 'is_shitty_beam' in d and int(d['is_shitty_beam']) == 1 else False
                base_plane = FabricatableBeam.dic_to_plane(d['plane'])
                holes = [FabricatableBeam.dic_to_plane(dic) for dic in d['holes']]

                if scale != 1.0:

                    dx *= scale
                    dy *= scale
                    dz *= scale

                    base_plane.Origin *= scale
                    for hole in holes:
                        hole.Origin *= scale
                
                beam = FabricatableBeam(base_plane, dx, dy, dz, holes, has_pockets, has_dowel_holes, has_annoying_pockets, is_shitty_beam)
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
        
        is_list = True
        if not type(beams) == list:
            is_list = False
            beams = [beams]
        
        transform = rg.Transform.PlaneToPlane(src, target)
        
        transformed_beams = []
        
        for b in beams:
            
            beam = b.transform(transform)
            transformed_beams.append(beam)
        
        if is_list:
            return transformed_beams
        else:
            return transformed_beams[0]
