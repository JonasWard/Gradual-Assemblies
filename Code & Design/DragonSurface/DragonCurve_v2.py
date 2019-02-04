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

def two_pts_relations(pt_0, pt_1):

    # distance calculation
    x0, y0, z0 = pt_0.X, pt_0.Y, pt_0.Z
    x1, y1, z1 = pt_1.X, pt_1.Y, pt_1.Z
    xD, yD, zD = (x1 - x0)**2, (y1 - y0)**2, (z1 - z0)**2
    distance = (xD + yD + zD) ** .5

    # mid_point
    x2, y2, z2 = (x0 + x1) * .5, (y0 + y1) * .5, (z0 + z1) * .5
    mid_point = rg.Point3d(x2, y2, z2)

    return distance, mid_point

def curve_contain(curve, points):

    xz_plane = rg.Plane.WorldZX

    # defining the domain of the curve

    t_start, t_end = curve.Domain[0], curve.Domain[1]
    domain_length = t_end - t_start
    t_start_extra, t_end_extra = domain_length * -.02 + t_start, domain_length * 0.02 + t_end

    # getting a plane at extra lengths & mid_point

    start_pt, end_pt, mid_pt = curve.PointAt(t_start_extra), curve.PointAt(t_end_extra), curve.PointAt(t_end)
    plane_origin = rg.Point3d(start_pt)
    plane_x_vector = rg.Vector3d(end_pt - start_pt)
    plane_y_vector = rg.Vector3d(mid_pt - start_pt)
    base_plane = rg.Plane(plane_origin, plane_x_vector, plane_y_vector)

    # transforming & projecting the curve & points to that plane

    transformer = rg.Transform.PlaneToPlane(base_plane, xz_plane)
    check_curve = curve.DuplicateCurve()
    check_curve.Transform(transformer)
    projected_curve = rg.Curve.ProjectToPlane(check_curve, xz_plane)

    curve_at_start = projected_curve.PointAtStart
    curve_at_end = projected_curve.PointAtEnd

    projected_points = []
    for point in points:
        transformed_point = rg.Point3d(point)
        transformed_point.Transform(transformer)
        projected_point = xz_plane.ClosestPoint(transformed_point)
        projected_points.append(projected_point)

    # constructing a boundary curve

    transformed_start_pt = rg.Point3d(start_pt)
    transformed_end_pt = rg.Point3d(end_pt)
    transformed_start_pt.Transform(transformer)
    transformed_end_pt.Transform(transformer)

    print curve.GetLength(), projected_curve.GetLength()

    x_increase = curve.GetLength() * .5
    x1, y1, z1 = transformed_start_pt.X, transformed_start_pt.Y, transformed_start_pt.Z
    x2, y2, z2 = transformed_end_pt.X, transformed_end_pt.Y, transformed_end_pt.Z
    x_val = (x1 + x2) * .5 + x_increase
    transformed_start_pt_2 = rg.Point3d(x_val, y1, z1)
    transformed_end_pt_2 = rg.Point3d(x_val, y2, z2)

    points = [curve_at_start, transformed_start_pt, transformed_start_pt_2, transformed_end_pt_2, transformed_end_pt_2, curve_at_end]
    # print points
    bounding_curve = rg.PolylineCurve(points)
    bound_curve = rg.Curve.JoinCurves([projected_curve, bounding_curve])[0]

    projected_curve = bound_curve

    # doing the containment operations

    inside = rg.PointContainment.Inside
    coincident = rg.PointContainment.Coincident
    outside = rg.PointContainment.Outside

    containment_values = []

    for pt in projected_points:
        local_containment_val = bound_curve.Contains(pt, xz_plane)
        if ((local_containment_val == inside) or (local_containment_val == coincident)):
            containment_val = 1
        elif (local_containment_val == outside):
            containment_val = -1
        containment_values.append(containment_val)

    return containment_values, bound_curve, projected_curve


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

    containment_info, bound_crv, proj_crv = curve_contain(curve, rel_curv_pt)

    return points, containment_info, bound_crv, v_vals, proj_crv

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

    containment_info, bound_crv, proj_crv = curve_contain(curve, v_vals)

    return points, containment_info, bound_crv, v_vals, proj_crv

global_points = []
global_curvature = []
bound_crvs = []
raw_points = []
raw_points_curvature = []

if (complex_divide):
    for i in range(curve_count):
        individual_points, curvature, bound_crv, curvature_point, proj_crv = divider_complex(curves[i], divisions, curvature_factor)
        global_points.append(individual_points)
        global_curvature.append(curvature)
        bound_crvs.append(bound_crv)
        [raw_points.append(pt) for pt in individual_points]
        [raw_points_curvature.append(pt) for pt in curvature_point]
else:
    for i in range(curve_count):
        individual_points, curvature, bound_crv, curvature_point, proj_crv = divider_simple(curves[i], divisions)
        global_points.append(individual_points)
        global_curvature.append(curvature)
        bound_crvs.append(bound_crv)
        [raw_points.append(pt) for pt in individual_points]
        [raw_points_curvature.append(pt) for pt in curvature_point]

print curvature

# for i in range (curve_count):
#     x_value = i
#     start_value = [0, 2, 1, 3][i % 4]
#     for j in range (divisions + 1):
