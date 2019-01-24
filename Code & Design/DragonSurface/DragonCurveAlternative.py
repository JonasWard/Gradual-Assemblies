# dragon curve using only alternation

# DivideCurve.py

import Rhino.Geometry as rg

# setting imput parameters

global curves, divisions
global curvature_factor, curvature_change
global curve_count, spacing
divider_bool

curve_correct_val = round((curve_count - 1) / 2, 0)
n_parameter = int((curve_correct_val - (curve_correct_val - 1) % 2) / 2)
curve_count = n_parameter * 4
m_parameter = int (divisions / 4.0 - 1)
divisions = m_parameter * 4


print "m_parameter", divisions, m_parameter
print "n_parameter", len(curves), curve_count, n_parameter

# regrading the curve for higher curvature area

def divider_complex(curves):
    curve_domain = curves.Domain
    curve_domain_length = curve_domain[1] - curve_domain[0]

    range_value = curve_domain_length / (divisions - 1)
    domain_list = []
    temp_vector_length_list = []
    for i in range (divisions):
        local_t = curve_domain[0] + i * range_value
        domain_list.append(local_t)
        local_curvature_vec = rg.Vector3d(curves.CurvatureAt(local_t))
        vector_length = local_curvature_vec.Length
        temp_vector_length_list.append(vector_length)

    temp_vector_length_partial_sums = []
    temp_point_list = []
    count = 0
    previous_value = 0
    for local_vec_l in (temp_vector_length_list):
        x_value = domain_list[count]
        y_value = previous_value * curvature_factor
        local_pt = rg.Point3d(x_value, y_value, 0)
        temp_point_list.append(local_pt)
        temp_vector_length_partial_sums.append(previous_value)
        previous_value += local_vec_l
        count += 1

    curvature_crv = rg.Curve.CreateControlPointCurve(temp_point_list, 10)
    temp_points_curvature_crv = curvature_crv.DivideByCount(divisions - 1, True)
    t_vals = [curvature_crv.PointAt(pt).X for pt in temp_points_curvature_crv]
    v_vals = [curves.CurvatureAt(t_value) for t_value in t_vals]
    rel_curv_pt = [(curves.PointAt(t_vals[i]) + v_vals[i]) for i in range(divisions)]
    current_points = [curves.PointAt(t_val) for t_val in t_vals]
    next_points = [(curves.PointAt(t_vals[i]) + v_vals[i] * curvature_change) for i in range(divisions)]
    next_curve = rg.Curve.CreateControlPointCurve(next_points, 10)
    transl = rg.Transform.Translation(rg.Vector3d(0,spacing,0))
    next_curve.Transform(transl)
    return current_points, next_curve

def divider_simple(curves):
    curve_domain = curves.Domain
    curve_domain_length = curve_domain[1] - curve_domain[0]

    range_value = curve_domain_length / (divisions - 1)

    points = []
    for i in range (divisions):
        local_t = curve_domain[0] + i * range_value
        local_point = curves.PointAt(local_t)
        points.append(local_point)

    return points

global_points = []
global_points_flatten = []

# dividing the curve in pieces

for s in range(curve_count):
    curve = curves[s]
    if (divider_bool):
        local_pts, ignore_curve = divider_complex(curve)
    else:
        local_pts = divider_simple(curve)
    [global_points_flatten.append(rg.Point3d(point)) for point in local_pts]
    global_points.append(local_pts)

# constructing the main directions

raw_line_list = []
global_line_list = []
for n in range(n_parameter):
    i = n * 4
    local_line_list = []
    for m in range(m_parameter):
        j1 = m * 4
        j2 = m * 4 + 1
        pt_1_0 = global_points[i][j1]
        pt_2_0 = global_points[i][j2]
        pt_1_1 = global_points[i + 1][j1 + 2]
        pt_2_1 = global_points[i + 1][j2 + 2]
        line_0 = rg.Line(pt_1_0, pt_2_0)
        line_1 = rg.Line(pt_1_1, pt_2_1)
        local_line_list.append(line_0)
        local_line_list.append(line_1)
        print i, ", ", j1
    global_line_list.append(local_line_list)

dowels = []

main_direction_length = len(global_line_list)
secundary_direction_length = len(global_line_list[0])

# print "main_direction_length: ", main_direction_length, " secundary_direction_length ", secundary_direction_length

# calculating the overlap of the main direction

for i in range(main_direction_length):
    for j in range(1, secundary_direction_length, 1):
        line_0 = global_line_list[i][j - 1]
        line_1 = global_line_list[i][j]
        ignore, a, b = rg.Intersect.Intersection.LineLine(line_0, line_1)
        # line 0 new
        l1_pt_0, l1_pt_1 = line_0.PointAt(0), line_0.PointAt(a)
        l2_pt_0, l2_pt_1 = line_1.PointAt(b), line_1.PointAt(1)
        raw_line_list.append(rg.Line(l1_pt_0, l1_pt_1))
        raw_line_list.append(rg.Line(l2_pt_0, l2_pt_1))
        global_line_list[i][j - 1] = rg.Line(l1_pt_0, l1_pt_1)
        global_line_list[i][j] = rg.Line(l2_pt_0, l2_pt_1)

# constructing the second direction

dir2_raw_line_list = []
dir2_global_line_list = []

for n in range(n_parameter - 1):
    i = n * 4 + 2
    dir2_local_line_list = []
    for m in range(m_parameter - 1):
        j1 = m * 4 + 1
        j2 = m * 4 + 2
        # group 0
        # pt_1_0_0 = global_points[i - 2][j1]
        # pt_1_0_1 = global_points[i + 2][j1]
        # pt_2_0_0 = global_points[i - 2][j2]
        # pt_2_0_1 = global_points[i + 2][j2]
        # pt_1_0 = ( pt_1_0_0 + pt_1_0_1 ) / 2.0
        # pt_2_0 = ( pt_2_0_0 + pt_2_0_1 ) / 2.0
        # # group 1
        # pt_1_1_0 = global_points[i - 1][j1 + 2]
        # pt_1_1_1 = global_points[i + 3][j1 + 2]
        # pt_2_1_0 = global_points[i - 1][j2 + 2]
        # pt_2_1_1 = global_points[i + 3][j2 + 2]
        # pt_1_1 = ( pt_1_1_0 + pt_1_0_1) / 2.0
        # pt_2_1 = ( pt_2_1_0 + pt_2_0_1) / 2.0

        pt_1_0 = global_points[i][j1]
        pt_2_0 = global_points[i][j2]
        pt_1_1 = global_points[i + 1][j1 + 2]
        pt_2_1 = global_points[i + 1][j2 + 2]

        line_0 = rg.Line(pt_1_0, pt_2_0)
        line_1 = rg.Line(pt_1_1, pt_2_1)
        dir2_local_line_list.append(line_0)
        dir2_local_line_list.append(line_1)
        print i, ", ", j1
    dir2_global_line_list.append(dir2_local_line_list)

dir2_main_direction_length = len(dir2_global_line_list)
dir2_secundary_direction_length = len(dir2_global_line_list[0])

print "dir2_main_direction_length: ", dir2_main_direction_length, " dir2_secundary_direction_length ", dir2_secundary_direction_length

# calculating the overlap of the main direction

dir2_raw_line_list = []
for i in range(dir2_main_direction_length):
    for j in range(1, dir2_secundary_direction_length, 1):
        line_0 = dir2_global_line_list[i][j - 1]
        line_1 = dir2_global_line_list[i][j]
        ignore, a, b = rg.Intersect.Intersection.LineLine(line_0, line_1)
        # line 0 new
        l1_pt_0, l1_pt_1 = line_0.PointAt(0), line_0.PointAt(a)
        l2_pt_0, l2_pt_1 = line_1.PointAt(b), line_1.PointAt(1)
        dir2_raw_line_list.append(rg.Line(l1_pt_0, l1_pt_1))
        dir2_raw_line_list.append(rg.Line(l2_pt_0, l2_pt_1))
        dir2_global_line_list[i][j - 1] = rg.Line(l1_pt_0, l1_pt_1)
        dir2_global_line_list[i][j] = rg.Line(l2_pt_0, l2_pt_1)
