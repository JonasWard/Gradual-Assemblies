import Rhino.Geometry as rg

# surface manipulation class

def calculate_midpoint(point_a, point_b):
    distance = point_a.DistanceTo(point_b)
    x1, y1, z1 = point_a.X, point_a.Y, point_a.Z
    x2, y2, z2 = point_b.X, point_b.Y, point_b.Z
    return rg.Point3d((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2)

def add_line_to_list(list_l, list_fr, surface, u_value, v_value0, v_value1):
    pt1 = surface.PointAt(u_value, v_value0)
    pt2 = surface.PointAt(u_value, v_value1)
    mid_point = calculate_midpoint(pt1, pt2)
    pt0 = xy_plane.ClosestPoint(mid_point)

    vector_x = rg.Vector3d(pt2 - pt1)
    vector_y = rg.Vector3d(mid_point - pt0)
    line = rg.Line(pt1, pt2)
    frame = rg.Plane(mid_point, vector_x, vector_y)

    list_l.append(line)
    list_fr.append(frame)
    return list_l, list_fr

# grasshopper set variables

surface
divisions_u
divisions_v

# global variables

xy_plane = rg.Plane.WorldXY

# resetting the domain of the brep

dom_u = surface.Domain(0)
dom_v = surface.Domain(1)

int_1 = rg.Interval(0, 1)
surface.SetDomain(0, int_1)
surface.SetDomain(1, int_1)

u_unit = 1.0/divisions_u
# v correction
v_certain = int((divisions_v - 1) / 2)
print v_certain
divisions_v = 2 * v_certain - 1
print divisions_v
v_unit = 1.0/divisions_v

line_list = []
dowel_list = []
frame_list = []
for i in range(-2, divisions_u + 3, 1):
    u_val = u_unit * i
    u_cnt = i % 4
    local_line_list = []
    local_frame_list = []

    if (u_cnt == 0):
        first_value = 1
        count_value =
    if (u_cnt == 1):
        first_value = 5
    if (u_cnt == 2):
        first_value = 5
    if (u_cnt == 3):
        first_value = 7



    v_value0, v_value1 = extra_value * v_unit, (extra_value + 1) * v_unit
    local_line_list, local_frame_list = add_line_to_list(local_line_list, local_frame_list, surface, u_val, v_value0, v_value1)
    for j in range(v_certain):
        v_value0, v_value1 = (j * 4 + first_value) * v_unit, (j * 4 + first_value + 1) * v_unit
        local_line_list, local_frame_list = add_line_to_list(local_line_list, local_frame_list, surface, u_val, v_value0, v_value1)
    line_list.append(local_line_list)
    frame_list.append(local_frame_list)

flatten_list_line = []
flatten_list_frame = []
for line_lists in line_list:
    for line in line_lists:
        flatten_list_line.append(line)

for frame_lists in frame_list:
    for frame in frame_lists:
        flatten_list_frame.append(frame)
