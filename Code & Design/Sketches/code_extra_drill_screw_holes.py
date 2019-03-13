"""Provides a scripting component.
    Inputs:
        x: The x script variable
        y: The y script variable
    Output:
        a: The a output variable"""

__author__ = "ytakzk"
__version__ = "2019.02.27"

import Rhino.Geometry as rg
from geometry.fabricatable_beam import FabricatableBeam
import Grasshopper.Kernel.Data.GH_Path as ghpath
import Grasshopper.DataTree as datatree
import System
import math as m
import copy as c
dowel_lines  = datatree[System.Object]()
dowel_planes = datatree[System.Object]()
screw_drill_lines  = datatree[System.Object]()
screw_drill_planes = datatree[System.Object]()

transformed_beams = []

for b in beams:
    
    plane = rg.Plane(target_plane)
    plane.Origin = rg.Point3d(
        plane.Origin.X + b.dx * 0.5,
        plane.Origin.Y,
        plane.Origin.Z
    )
    
    transformed_beam = FabricatableBeam.orient_structure([b], b.base_plane, plane)
    transformed_beams.append(transformed_beam[0])

compas_beams = [b.create_compas_beam() for b in transformed_beams]

def get_screw_holes(beam):
    # drill parameters
    drill_angle = 55            # in reference to the plain
    drill_depth = 25            # length drill line in wood
    drill_start_tolerance = 40  # extension drill line outside of the beam
    x_spacing = 30              # how much x deviates from the average position
    y_spacing = 40


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
    if spacing_x < 150.0:
        spacing_x = 150
        
    print "spacing_x after correction", spacing_x

    # setting the raw locations where the holes should be
    neg_x_loc = start_x + spacing_x
    pos_x_loc = end_x - spacing_x

    y_delta = m.cos(m.radians(drill_angle))
    z_delta = m.sin(m.radians(drill_angle))

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
    # pt inside the beam
    x1 = neg_x_loc + x_spacing
    y1 = top_y_coordinate
    z1 = top_z_coordinate
    pt_1 = rg.Point3d(x1, y1, z1)
    ln_0 = rg.Line(pt_0, pt_1)
    pl_0 = rg.Plane(pt_0, rg.Vector3d(pt_0 - pt_1))

    # ln_1
    # pt inside the beam
    x0 = pos_x_loc - x_spacing
    y0 = bot_y_coordinate
    z0 = bot_z_coordinate
    pt_0 = rg.Point3d(x0, y0, z0)
    # pt inside the beam
    x1 = pos_x_loc - x_spacing
    y1 = top_y_coordinate
    z1 = top_z_coordinate
    pt_1 = rg.Point3d(x1, y1, z1)
    ln_1 = rg.Line(pt_0, pt_1)
    pl_1 = rg.Plane(pt_0, rg.Vector3d(pt_0 - pt_1))

    # ln_2
    # pt inside the beam
    x0 = neg_x_loc - x_spacing
    y0 = - bot_y_coordinate
    z0 = bot_z_coordinate
    pt_0 = rg.Point3d(x0, y0, z0)
    # pt inside the beam
    x1 = neg_x_loc - x_spacing
    y1 = - top_y_coordinate
    z1 = top_z_coordinate
    pt_1 = rg.Point3d(x1, y1, z1)
    ln_2 = rg.Line(pt_0, pt_1)
    pl_2 = rg.Plane(pt_0, rg.Vector3d(pt_0 - pt_1))

    # ln_3
    # pt inside the beam
    x0 = pos_x_loc + x_spacing
    y0 = - bot_y_coordinate
    z0 = bot_z_coordinate
    pt_0 = rg.Point3d(x0, y0, z0)
    # pt inside the beam
    x1 = pos_x_loc + x_spacing
    y1 = - top_y_coordinate
    z1 = top_z_coordinate
    pt_1 = rg.Point3d(x1, y1, z1)
    ln_3 = rg.Line(pt_0, pt_1)
    pl_3 = rg.Plane(pt_0, rg.Vector3d(pt_0 - pt_1))
    
    line_set = [ln_0, ln_1, ln_2, ln_3]
    pln_set = [pl_0, pl_1, pl_2, pl_3]
    
    translate_to_origin_beam = rg.Transform.Translation(rg.Vector3d(beam_origin))
    
    [line.Transform(translate_to_origin_beam) for line in line_set]
    [pln.Transform(translate_to_origin_beam) for pln in pln_set]
    
    return line_set, pln_set

planes = []
for i, beam in enumerate(transformed_beams):
    
    path = ghpath(i)
    for line, tmp_dowel_plane in zip(beam.get_dowel_lines(), beam.holes):
        dowel_lines.Add(line, path)
        
        dowel_plane = rg.Plane(tmp_dowel_plane)
        min_angle = 9999
        for j in range(30):
            
            candidate_plane = rg.Plane(tmp_dowel_plane)
            diff = m.radians(12 * (j + 1))
            candidate_plane.Rotate(diff, candidate_plane.ZAxis, candidate_plane.Origin)
            
            angle = rg.Vector3d.VectorAngle(candidate_plane.XAxis, rg.Plane.WorldXY.YAxis)

            if angle < min_angle:
                min_angle = angle
                dowel_plane = candidate_plane

        dowel_planes.Add(dowel_plane, path)
    planes.append(beam.base_plane)
    
    print i
    
    if i < 4:
        extra_drill_lines, extra_drill_planes = get_screw_holes(beam)
        print "extra drill lines: ", extra_drill_lines
        for index, line in enumerate(extra_drill_lines):
            screw_drill_lines.Add(line, path)
            screw_drill_planes.Add(extra_drill_planes[index], path)
#    planes.extend(beam.holes)
        
beam_breps = [b.create_brep() for b in transformed_beams]

# snippet to find the extra drill lines for the screw Holes