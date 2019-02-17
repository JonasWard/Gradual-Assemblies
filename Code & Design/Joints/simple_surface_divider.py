# simple surface divisions

import sys
sys.path.append("/Users/jonas/Dropbox/0.dfab/Trimester 2/Project I - Gradual Assemblies/Gradual-Assemblies/UR_Control")
import geometry.beam as beam

import Rhino.Geometry as rg

# grasshopper parameters

surface
u_div
v_div

# check to make sure there are an even anount of beams
u_div += (u_div % 2)

# surface remapping
surface.SetDomain(0, rg.Interval(0, u_div))
surface.SetDomain(1, rg.Interval(1, v_div))

list_a = []
list_b = []

beam_list_a = []
beam_list_b = []

for u_val in range(u_div):
    if u_val % 2 == 0:
        v_line_list = []
        v_beam_list = []
        for v_val in range(0, v_div - 1, 2):
            # line representation
            pt_0 = surface.PointAt(u_val, v_val)
            pt_1 = surface.PointAt(u_val, v_val + 1)
            local_line = rg.Line(pt_0, pt_1)
            v_line_list.append(local_line)

            # beam representation
            mid_point = (pt_0 + pt_1) / 2.0
            pt_ignore, u_eval, v_eval = surface.ClosestPoint(mid_point)
            y_vector = surface.NormalAt(u_eval, v_eval)
            x_vector = rg.Vector3d(pt_1 - pt_0)
            base_plane = rg.Plane(mid_point, x_vector, y_vector)
            dx = local_line.Length
            dy = 120
            dz = 40
            local_beam = beam.Beam(base_plane, dx, dy, dz)
            v_beam_list.append(local_beam)
        list_a.append(v_line_list)
        beam_list_a.append(v_beam_list)
    else:
        v_line_list = []
        v_beam_list = []
        for v_val in range(1, v_div - 1, 2):
            # line representation
            pt_0 = surface.PointAt(u_val, v_val)
            pt_1 = surface.PointAt(u_val, v_val + 1)
            local_line = rg.Line(pt_0, pt_1)
            v_line_list.append(local_line)

            # beam representation
            mid_point = (pt_0 + pt_1) / 2.0
            pt_ignore, u_eval, v_eval = surface.ClosestPoint(mid_point)
            y_vector = surface.NormalAt(u_eval, v_eval)
            x_vector = rg.Vector3d(pt_1 - pt_0)
            base_plane = rg.Plane(mid_point, x_vector, y_vector)
            dx = local_line.Length
            dy = 120
            dz = 40
            local_beam = beam.Beam(base_plane, dx, dy, dz)
            v_beam_list.append(local_beam)
        list_b.append(v_line_list)
        beam_list_b.append(v_beam_list)

line_visualisation = []

for v_lines_lists in list_a:
    for line in v_lines_lists:
        line_visualisation.append(line)
for v_lines_lists in list_b:
    for line in v_lines_lists:
        line_visualisation.append(line)

beam_visualisation = []

for v_beams_lists in beam_list_a:
    for beam in v_beams_lists:
        beam_visualisation.append(beam.brep_representation())
for v_beams_lists in beam_list_b:
    for beam in v_beams_lists:
        beam_visualisation.append(beam.brep_representation())
