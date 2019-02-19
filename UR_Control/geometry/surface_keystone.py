# surface keystone strategy

import Rhino.Geometry as rg
import math as m
import copy

# grasshopper inputs

srf_1
srf_2
srf_3
srf_4

# local inputs

surface_set = [srf_1, srf_2, srf_3, srf_4]
surface_count = len(srf_set)

u_div = 11
v_div = 11

isocurve_visualisation = []
isocurve_set = []

for surface in srf_set:
    surface.SetDomain(0, rg.Interval(0, u_div))
    surface.SetDomain(1, rg.Interval(0, v_div))
    local_isocurve_set = []
    for v_val in range(v_div + 1):
        local_isocurve = surface.IsoCurve(0, v_val)
        isocurve_visualisation.append(local_isocurve)
        local_isocurve_set.append(local_isocurve)
    isocurve_set.append(local_isocurve_set)

blended_curves = [[] for i in range(surface_count)]
blend_crvs_vis = []

blend_curve_count = int(m.ceil(v_div / 2.0))
blend_curve_average_length = 0

for i in range (blend_curve_count):
    for j in range(surface_count):
        curve_0 = isocurve_set[j][i]
        curve_1 = isocurve_set[(j - 1) % surface_count][v_div - i]
        t0, t1 = curve_0.Domain[0], curve_1.Domain[0]
        blend_con = rg.BlendContinuity.Tangency
        blend_curve = rg.Curve.CreateBlendCurve(curve_0, t0, True, blend_con, curve_1, t1, True, blend_con)
        blend_curve = blend_curve.Rebuild(30, 3, False)
        blended_curves[j].append(blend_curve)
        blend_curve_average_length += blend_curve.GetLength()
        blend_crvs_vis.append(blend_curve)

blend_curve_average_length /= (blend_curve_count * surface_count)

average_spacing = 200.0

blend_div_count = int(m.ceil(blend_curve_average_length / average_spacing))
blend_div_count += (blend_div_count + 1)%2

structured_point_cloud = []
visualization_point_cloud = []
blended_curve_divisions = []

start_shift = 0 / (2 * (blend_div_count - 1))
shift_start = 1 - .1 * surface_count
shift_max = .025 * surface_count
start_split_index = int(shift_start * blend_curve_count)
split_difference = blend_curve_count - start_split_index
split_differential = shift_max / (split_difference)
shift_variation = (1 - (1 - shift_max) ** 2) / split_difference ** 2

t_vals_srf = []
for i in range(blend_curve_count):
    local_t_vals = []
    if (i < start_split_index):
        diff = start_shift
        local_t_vals = [.5 - diff, .5 + diff]
    else:
        n_var = i + 1 - start_split_index
        diff = (1 - m.sqrt( 1 - shift_variation * n_var ** 2)) / 2 + start_shift
        local_t_vals = [.5 - diff, .5 + diff]
    t_vals_srf.append(local_t_vals)

print t_vals_srf

temp_new_sets_pos = []
temp_new_sets_neg = []

crv_vis = []

for i in range(surface_count):
    local_pos_list = []
    local_neg_list = []
    for j in range(blend_curve_count):
        start_t, end_t = blended_curves[i][j].Domain[0], blended_curves[i][j].Domain[1]
        t_delta = end_t - start_t
        local_t_vals = [start_t + t_delta*t_val for t_val in t_vals_srf[j]]
        tmp_crvs = blended_curves[i][j].Split(local_t_vals)
        tmp_crv_0, tmp_crv_1 = tmp_crvs[0], tmp_crvs[-1]
        tmp_crv_1.Reverse()
        local_pos_list.append(tmp_crv_0)
        local_neg_list.append(tmp_crv_1)
        crv_vis.append(tmp_crv_0)
        crv_vis.append(tmp_crv_1)
    local_neg_list.reverse()
    temp_new_sets_pos.append(local_pos_list)
    temp_new_sets_neg.append(local_neg_list)

new_sets = []
for j in range(surface_count):
    local_set = temp_new_sets_pos[j]
    local_set.extend(temp_new_sets_neg[(j + 1) % surface_count])
    new_sets.append(local_set)

new_surfaces = []
visualize_uv_switched_crvs = []
for j in range(surface_count):
    # inverting the surface directions

    sampling_count = 5
    # switching the uv direction back to where it should be! -> rebuilding the surface
    point_list = [[] for i in range(sampling_count)]
    for temp_curve in new_sets[j]:
        length = temp_curve.GetLength()
        start_t, end_t = temp_curve.Domain[0], temp_curve.Domain[1]
        t_delta = end_t - start_t
        t_differential = t_delta / (sampling_count - 1)
        # calculating how much the offset_dis result in t_val change
        point_set = [temp_curve.PointAt(t_val * t_differential + start_t) for t_val in range(0, sampling_count, 1)]
        for i, point in enumerate(point_set):
            point_list[i].append(rg.Point3d(point))

    uv_switched_curves = []
    for point_set in point_list:
        local_curve = rg.NurbsCurve.Create(False, 3, point_set)
        uv_switched_curves.append(local_curve)
        visualize_uv_switched_crvs.append(local_curve)

    loft_type = rg.LoftType.Tight
    new_surface = rg.Brep.CreateFromLoftRebuild(uv_switched_curves, rg.Point3d.Unset, rg.Point3d.Unset, loft_type, False, 50)[0]
    new_surface.Faces.Item[0].ToNurbsSurface()
    new_srf = copy.deepcopy(new_surface)
    new_surfaces.append(new_surface)
