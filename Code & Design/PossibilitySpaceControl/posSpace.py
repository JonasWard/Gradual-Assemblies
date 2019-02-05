# rhino file to check the possibility space of an object

import Rhino.Geometry as rg
import math as m

# adding the beam class
# parent is the 2nd order parent of the gh file

import os, sys

geometry_lib_path = os.path.join(parent, 'UR_CONTROL')
sys.path.append(geometry_lib_path)

import geometry.beam as beam
import geometry.dowel as dowel
import geometry.hole as hole

# force reload when rerunning
reload(beam)
reload(dowel)
reload(hole)

x_dim = 1000
y_dim = 120
z_dim = 40

world_origin = rg.Point3d(0, 0, 0)

world_x = rg.Vector3d(1, 0, 0)
world_y = rg.Vector3d(0, 1, 0)
world_z = rg.Vector3d(0, 0, 1)

beam_1 = beam.Beam(rg.Plane.WorldYZ, x_dim, y_dim, z_dim)

rotation = rg.Transform.Rotation(m.pi / 2.0, world_x, world_origin)
translation = rg.Transform.Translation(rg.Vector3d(1000, 0, 0))

plane = rg.Plane.WorldYZ
plane.Transform(rotation)
plane.Transform(translation)

beam_2 = beam.Beam(plane, x_dim, y_dim, z_dim)

line_1, line_2 = beam_1.get_baseline(), beam_2.get_baseline()

number = 10
t_vals = [i / (number - 1) for i in range(number)]
pts_1 = [line_1.PointAt(t_val) for t_val in t_vals]
pts_2 = [line_2.PointAt(t_val) for t_val in t_vals]

dowels = [dowel.Dowel(None, rg.Line(pts_2[i], pts_1[i])) for i in range(number)]

[beam_1.add_dowel(dowel) for dowel in dowels]
[beam_2.add_dowel(dowel) for dowel in dowels]

beam_breps = [beam_1.brep_representation(), beam_2.brep_representation()]
spheres_boundary = beam_1.check_boundary_constraints()
spheres_angles = beam_1.check_angle_constraints()

recs = []
for i in range (len(beam_1.top_recs)):
    recs.append(beam_1.top_recs[i])
    recs.append(beam_1.bottom_recs[i])
