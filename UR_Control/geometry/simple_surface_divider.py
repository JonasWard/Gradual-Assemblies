# simple surface divisions

import sys

# import the beam_class
path_to_append = single_parent
sys.path.append(path_to_append)

print path_to_append

import geometry.beam as beam
import geometry.hole_class as hc

import Rhino.Geometry as rg

# force reload when rerunning
reload(beam)
reload(hc)

# grasshopper parameters

surface
u_div
v_div

start_position

# # check to make sure there are an even amount of beams
# u_div += (u_div % 2)

# surface remapping
surface.SetDomain(0, rg.Interval(0, u_div))
surface.SetDomain(1, rg.Interval(1, v_div))

list_a = []
list_b = []

beam_list_a = []
beam_list_b = []

for u_val in range(u_div + 1):
    if u_val % 2 == start_position:
        v_line_list = []
        v_beam_list = []
        for v_val in range(1, v_div, 2):
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
        for v_val in range(2, v_div, 2):
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
hole_visualisation = []
hole_list_a = []
hole_list_b = []
pt_locations_bot = []
pt_locations_top = []

for v_beams_lists in beam_list_a:
    hole_v_list = []
    for beam in v_beams_lists:
        beam.extend(100)
        holes = [hc.Hole((beam), 0).joint_pts, hc.Hole((beam), 1).joint_pts]
        hole_visualisation.extend([holes[0][0][0], holes[0][1][0], holes[0][1][1], holes[0][1][2],  holes[0][2][0], holes[0][2][1], holes[0][2][2], holes[1][0][0], holes[1][1][0], holes[1][1][1], holes[1][1][2],  holes[1][2][0], holes[1][2][1], holes[1][2][2]])
        hole_v_list.append(holes)
        beam_visualisation.append(beam.brep_representation())
    hole_list_a.append(hole_v_list)

hole_list_a

for v_beams_lists in beam_list_b:
    hole_v_list = []
    for beam in v_beams_lists:
        beam.extend(100)
        holes = [hc.Hole((beam), 0).joint_pts, hc.Hole((beam), 1).joint_pts]
        hole_visualisation.extend([holes[0][0][0], holes[0][1][0], holes[0][1][1], holes[0][1][2],  holes[0][2][0], holes[0][2][1], holes[0][2][2], holes[1][0][0], holes[1][1][0], holes[1][1][1], holes[1][1][2],  holes[1][2][0], holes[1][2][1], holes[1][2][2]])
        hole_v_list.append(holes)
        beam_visualisation.append(beam.brep_representation())
    hole_list_b.append(hole_v_list)
