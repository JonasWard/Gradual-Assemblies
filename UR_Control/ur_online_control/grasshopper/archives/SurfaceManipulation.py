import Rhino.Geometry as rg

# surface manipulation class

def calculate_midpoint(point_a, point_b):
    distance = point_a.DistanceTo(point_b)
    x1, y1, z1 = point_a.X, point_a.Y, point_a.Z
    x2, y2, z2 = point_b.X, point_b.Y, point_b.Z
    return rg.Point3d((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2)

# grasshopper set variables

surface
divisions_u
divisions_v
transpose_qm

# global variables

xy_plane = rg.Plane.WorldXY
surface.Transpose(transpose_qm)

# resetting the domain of the brep

dom_u = surface.Domain(0)
dom_v = surface.Domain(1)

int_1 = rg.Interval(0, 1)
surface.SetDomain(0, int_1)
surface.SetDomain(1, int_1)

u_value = 1.0/divisions_u
v_value = 1.0/divisions_v

line_list = []
dowel_list = []
frame_list = []
for i in range(divisions_u + 1):
    x_value = u_value * i
    u_val = i % 2
    for j in range(divisions_v + 1):
        if ((j % 2) == u_val) and (j < divisions_v) :
            y1_value = v_value * j
            y2_value = v_value * (j + 1)
            pt1 = surface.PointAt(x_value, y1_value)
            pt2 = surface.PointAt(x_value, y2_value)
            mid_point = calculate_midpoint(pt1, pt2)
            pt0 = xy_plane.ClosestPoint(mid_point)

            vector_x = rg.Vector3d(pt2 - pt1)
            vector_y = rg.Vector3d(mid_point - pt0)
            line = rg.Line(pt1, pt2)
            frame = rg.Plane(mid_point, vector_x, vector_y)

            line_list.append(line)
            frame_list.append(frame)
