# DivideCurve.py

import Rhino.Geometry as rg

# setting imput parameters

global curve, divisions
global curvature_factor, curvature_change
global curve_count, spacing

# regrading the curve for higher curvature areas

def divider(curves):
    curve_domain = curves.Domain
    curve_domain_length = curve_domain[1] - curve_domain[0]

    range_value = curve_domain_length / divisions
    domain_list = []
    temp_vector_length_list = []
    for i in range (divisions + 1):
        local_t = i * range_value
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
    temp_points_curvature_crv = curvature_crv.DivideByCount(divisions, True)
    t_vals = [curvature_crv.PointAt(pt).X for pt in temp_points_curvature_crv]
    v_vals = [curves.CurvatureAt(t_value) for t_value in t_vals]
    rel_curv_pt = [(curves.PointAt(t_vals[i]) + v_vals[i]) for i in range(divisions + 1)]
    current_points = [curves.PointAt(t_val) for t_val in t_vals]
    next_points = [(curves.PointAt(t_vals[i]) + v_vals[i] * curvature_change) for i in range(divisions + 1)]
    next_curve = rg.Curve.CreateControlPointCurve(next_points, 10)
    transl = rg.Transform.Translation(rg.Vector3d(0,spacing,0))
    next_curve.Transform(transl)
    return current_points, next_curve

global_points = []

for k in range (curve_count):
    local_pts, curve = divider(curve)
    print local_pts
    print curve
    global_points.append(local_pts)
