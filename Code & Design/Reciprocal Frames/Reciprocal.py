# simple reciprocal frame form generator

import Rhino.Geometry as rg
import math as m

# grasshopper variables

rotation_angle
goal_length
points

# interpretation of those variables

count = len(points)
print count

# rotation vector generator
val_x, val_y, val_z = 0, 0, 0

def distance_2pt(pt_0, pt_1):
    x1, y1, z1 = pt_0.X, pt_0.Y, pt_0.Z
    x2, y2, z2 = pt_1.X, pt_1.Y, pt_1.Z
    distance = m.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
    return distance

# center_point
for pt in points:
    val_x += pt.X
    val_y += pt.Y
    val_z += pt.Z
center_point = rg.Point3d(val_x / count, val_y / count, val_z / count)

# mid_points
mid_points = []
dir_vectors_rot = []
dir_vectors_x = []

lines = []

scale_values = []
planes = []
base_planes = []

for i in range(count):
    mid_point = (points[i] + points[(i - 1) % count]) / 2
    print points[i], points[(i - 1) % count]
    local_distance = distance_2pt(points[i], points[(i - 1) % count])
    print local_distance
    angle = rotation_angle / local_distance
    mid_points.append(mid_point)
    dir_vector_rot = rg.Vector3d(mid_point - center_point)
    dir_vectors_rot.append(dir_vector_rot)
    rotation = rg.Transform.Rotation(angle, dir_vector_rot, mid_point)
    end_point = rg.Point3d(points[i])
    end_point.Transform(rotation)
    start_point = rg.Point3d(points[(i - 1) % count])
    start_point.Transform(rotation)
    print end_point, start_point
    local_line = rg.Line(start_point, end_point)
    lines.append(local_line)
    local_scale_value = goal_length / local_distance
    scale_values.append(local_scale_value)
    dir_vector_y = rg.Vector3d(end_point - start_point)

    local_plane = rg.Plane(rg.Point3d(0,0,0), dir_vector_y, dir_vector_rot)
    base_planes.append(local_plane)


scaled_lines = []

for i in range(count):
    start_point = rg.Point3d(lines[i].PointAt(0))
    end_point = rg.Point3d(lines[i].PointAt(1))
    scale_matrix = rg.Transform.Scale(start_point, scale_values[i])
    end_point.Transform(scale_matrix)
    local_line = rg.Line(start_point, end_point)
    scaled_lines.append(local_line)

xy_pl = rg.Plane.WorldXY
ign, t_val = rg.Intersect.Intersection.LinePlane(scaled_lines[0], xy_pl)
scaled_lines[0] = rg.Line(scaled_lines[0].PointAt(0), scaled_lines[0].PointAt(t_val))

lengths = []
boxes = []

for i in range(count):
    start_point = rg.Point3d(scaled_lines[i].PointAt(0))
    end_point = rg.Point3d(scaled_lines[i].PointAt(1))
    length = distance_2pt(start_point, end_point)
    mid_point = rg.Vector3d( (start_point + end_point) / 2)
    trans_matrix = rg.Transform.Translation(mid_point)
    base_planes[i].Transform(trans_matrix)
    lengths.append(length)

    x_size = rg.Interval(- length / 2.0, length / 2.0)
    y_size = rg.Interval(- 50, 50)
    z_size = rg.Interval(- 20, 20)

    local_box = rg.Box(base_planes[i], x_size, y_size, z_size)
    boxes.append(local_box)
