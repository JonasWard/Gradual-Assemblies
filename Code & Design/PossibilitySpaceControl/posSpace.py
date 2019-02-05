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
angle = 65

world_origin = rg.Point3d(0, 0, 0)

world_x = rg.Vector3d(1, 0, 0)
world_y = rg.Vector3d(0, 1, 0)
world_z = rg.Vector3d(0, 0, 1)

beam_1 = beam.Beam(rg.Plane.WorldYZ, x_dim, y_dim, z_dim)

rotation = rg.Transform.Rotation(m.pi / 9.0, world_x, world_origin)
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

spheres_boundary = []
sphere_angles = []
beam_breps = []

beams = [beam_1, beam_2]

for beam_obj in beams:
    [beam_obj.add_dowel(dowel) for dowel in dowels]
    local_spheres_boundary = beam_obj.check_boundary_constraints()
    local_spheres_angles = beam_obj.check_angle_constraints()
    [spheres_boundary.append(local_sphere) for local_sphere in local_spheres_boundary]
    [sphere_angles.append(local_angle) for local_angle in local_spheres_angles]
    beam_breps.append(beam_obj.brep_representation())

# possibility space in itself

point = rg.Point3d(2000,500,300)
pyramid_list = []

for beam_obj in beams:
    polylines_top = beam_obj.top_recs
    polylines_bottom = beam_obj.bottom_recs
    cone_planes = [polylines_top[0].Plane, polylines_bottom[0].Plane]
    distance = 10000
    index = 0
    top_bottom = 0
    for polyline_top in polylines_top:
        local_distance = polyline_top.ClosestPoint(point).DistanceTo(point)
        if local_distance < distance:
            distance = local_distance
            value_to_consider = index
            top_bottom = 1
        index += 1

    local_distance = polylines_bottom[value_to_consider].ClosestPoint(point).DistanceTo(point)
    if local_distance < distance:
        top_bottom = 0

    # cone construction
    cone_plane = cone_planes[top_bottom]
    cone_construction_plane = rg.Plane(cone_plane)
    translation = rg.Transform.Translation(rg.Vector3d(point - cone_construction_plane.Origin))
    cone_construction_plane.Transform(translation)
    cone_height = - cone_plane.ClosestPoint(point).DistanceTo(point)
    cone_radius = m.tan(m.radians(90 - angle)) * abs(cone_height)
    cone = rg.Cone(cone_construction_plane, cone_height, cone_radius).ToBrep(True)
    pyramid_list.append(cone)

    # top plane
    polylines_top[value_to_consider]
    loc_pts = [polylines_top[value_to_consider].Corner(i) for i in range(4)]
    faces = [rg.NurbsSurface.CreateFromCorners(loc_pts[0], loc_pts[1], loc_pts[2], loc_pts[3])]
    [faces.append(rg.NurbsSurface.CreateFromCorners(loc_pts[i], loc_pts[(i + 1) % 4], point)) for i in range(4)]
    faces = [face.ToBrep() for face in faces]
    pyramid = rg.Brep.JoinBreps(faces, .01)[0]
    pyramid_list.append(pyramid)

    # bottom plane
    polylines_bottom[value_to_consider]
    loc_pts = [polylines_bottom[value_to_consider].Corner(i) for i in range(4)]
    faces = [rg.NurbsSurface.CreateFromCorners(loc_pts[0], loc_pts[1], loc_pts[2], loc_pts[3])]
    [faces.append(rg.NurbsSurface.CreateFromCorners(loc_pts[i], loc_pts[(i + 1) % 4], point)) for i in range(4)]
    faces = [face.ToBrep() for face in faces]
    pyramid = rg.Brep.JoinBreps(faces, .01)[0]
    pyramid_list.append(pyramid)

# count = len (pyramid_list)
# intersection = pyramid_list[0]
# for index in range (1, count, 1):
#     print intersection
#     intersection = rg.Brep.CreateBooleanIntersection([intersection], [pyramid_list[index]], 0.01)[0]
