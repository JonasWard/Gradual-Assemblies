# dragon curve retake_easy

import Rhino.Geometry as rg
import math as m

# grasshopper inputs

curves
divisions
complex_divide
global curvature_factor


count = len(curves)
curve_correct_val = round((curve_count - 1) / 2, 0)
curve_count = int((curve_correct_val - (curve_correct_val - 1) % 2) / 2) * 4

print curve_count

# global variables

v_scale = 5000.0

# function to regrade curves based on curvature

def distance_2pt(pt_0, pt_1):
    x0, y0, z0 = pt_0.X, pt_0.Y, pt_0.Z
    x1, y1, z1 = pt_1.X, pt_1.Y, pt_1.Z
    xD, yD, zD = (x1 - x0)**2, (y1 - y0)**2, (z1 - z0)**2
    distance = (xD + yD + zD) ** .5
    return distance

def curve_contain(curve, points):

    # constructing a boundary curve
    t_start, t_end = curve.Domain[0], curve.Domain[1]
    t_mid = (t_start + t_end) / 2.0
    start_pt, end_pt, mid_pt = curve.PointAt(t_start), curve.PointAt(t_end), curve.PointAt(t_mid)
    base_plane = rg.Plane(start_pt, end_pt, mid_pt)
    rotation_matrix = rg.Transform.Rotation(m.pi, base_plane.Normal, mid_pt)
    arc_max = rg.Point3d(end_pt)
    arc_max.Transform(rotation_matrix)
    arc = rg.Arc(start_pt, arc_max, end_pt).ToNurbsCurve()
    bound_curve = rg.Curve.JoinCurves([curve, arc])[0]
    print bound_curve

    # offseting that boundary curve
    offset_curve = bound_curve.DuplicateCurve()
    offset_style = rg.CurveOffsetCornerStyle.Smooth
    offset_curve.Offset(base_plane, 25.0, .01, offset_style)
    print len(bound_curve), len(offset_curve)
    if (offset_curve.GetLength(0.01) < bound_curve.GetLength(0.01)):
        for pt in points:
            pt_0 = bound_curve.ClosestPoint(pt)
            pt_1 = offset_curve.ClosestPoint(pt)
            dis_0 = distance_2pt(pt_0, pt)
            dis_1 = distance_2pt(pt_1, pt)
            if (dis_0 < dis_1):
                state = True
            else:
                state = False

            containment_values.append(state)

    else:
        for pt in points:
            pt_0 = bound_curve.ClosestPoint(pt)
            pt_1 = offset_curve.ClosestPoint(pt)
            dis_0 = distance_2pt(pt_0, pt)
            dis_1 = distance_2pt(pt_1, pt)
            if (dis_0 < dis_1):
                state = False
            else:
                state = True

            containment_values.append(state)

    return containment_values, bound_curve


def divider_complex(curve, divisions, curvature_factor):
    curve_domain = curve.Domain
    curve_domain_length = curve_domain[1] - curve_domain[0]

    range_value = curve_domain_length / (divisions)
    domain_list = []
    temp_vector_length_list = []
    for i in range (divisions + 1):
        local_t = curve_domain[0] + i * range_value
        domain_list.append(local_t)
        local_curvature_vec = rg.Vector3d(curve.CurvatureAt(local_t))
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
    v_vals = [curve.CurvatureAt(t_value) for t_value in t_vals]
    rel_curv_pt = [(curve.PointAt(t_vals[i]) + v_vals[i] * v_scale) for i in range(divisions + 1)]
    points = [curve.PointAt(t_val) for t_val in t_vals]

    containment_info, bound_crv = curve_contain(curve, rel_curv_pt)

    return points, containment_info, bound_crv, v_vals

# function to divide curves in a straight-forward mather

def divider_simple(curve, divisions):
    curve.Domain = rg.Interval(0.0, divisions * 1.0)

    v_vals = []
    points = []
    for i in range (divisions + 1):
        local_pt = rg.Point3d(curve.PointAt(i))
        points.append(local_pt)
        v_val_pt = local_pt + rg.Point3d(curve.CurvatureAt(i)) * v_scale
        v_vals.append(v_val_pt)

    containment_info, bound_crv = curve_contain(curve, v_vals)

    return points, containment_info, bound_crv, v_vals

global_points = []
global_curvature = []
bound_crvs = []
raw_points = []
raw_points_curvature = []

if (complex_divide):
    for i in range(curve_count):
        individual_points, curvature, bound_crv, curvature_point = divider_complex(curves[i], divisions, curvature_factor)
        global_points.append(individual_points)
        global_curvature.append(curvature)
        bound_crvs.append(bound_crv)
        [raw_points.append(pt) for pt in individual_points]
        [raw_points_curvature.append(pt) for pt in curvature_point]
else:
    for i in range(curve_count):
        individual_points, curvature, bound_crv, curvature_point = divider_simple(curves[i], divisions)
        global_points.append(individual_points)
        global_curvature.append(curvature)
        bound_crvs.append(bound_crv)
        [raw_points.append(pt) for pt in individual_points]
        [raw_points_curvature.append(pt) for pt in curvature_point]

# for i in range (curve_count):
#     x_value = i
#     start_value = [0, 2, 1, 3][i % 4]
#     for j in range (divisions + 1):
