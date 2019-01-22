# DivideCurve.py

import Rhino.Geometry as rg

# setting imput parameters

global curves, divisions
global curvature_factor, curvature_change
global curve_count, spacing

curve_count = len(curves) - len(curves) % 3
divisions = divisions - divisions % 2

# regrading the curve for higher curvature areas

def divider(curves):
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

global_points = []

for s in range(curve_count):
    curve = curves[s]
    local_pts, ignore_curve = divider(curve)
    global_points.append(local_pts)

m_parameter = int (divisions / 2.0)
n_parameter = int (curve_count / 3.0)

raw_line_list = []
global_line_list = []
for n in range(n_parameter):
    local_line_list = []
    for m in range(m_parameter):
        i = (n * 3 + m) % curve_count
        j1 = m*2
        j2 = j1 + 1
        pt_1 = global_points[i][j1]
        pt_2 = global_points[i][j2]
        local_line = rg.Line(pt_1, pt_2)
        local_line_list.append(local_line)
    global_line_list.append(local_line_list)

dowels = []
for j in range(n_parameter):
    for i in range(1, m_parameter, 1):
        line_0 = global_line_list[j][i - 1]
        line_1 = global_line_list[j][i]
        ignore, a, b = rg.Intersect.Intersection.LineLine(line_0, line_1)
        # line 0 new
        l1_pt_0, l1_pt_1 = line_0.PointAt(0), line_0.PointAt(a)
        l2_pt_0, l2_pt_1 = line_1.PointAt(b), line_1.PointAt(1)
        raw_line_list.append(rg.Line(l1_pt_0, l1_pt_1))
        global_line_list[j][i - 1] = rg.Line(l1_pt_0, l1_pt_1)
        global_line_list[j][i] = rg.Line(l2_pt_0, l2_pt_1)
