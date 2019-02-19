# surface keystone strategy

import Rhino.Geometry as rg
import math as m

# grasshopper inputs

srf_1
srf_2
srf_3
srf_4

# local inputs

surface_set = [srf_1, srf_2, srf_3, srf_4]
surface_count = len(surface_set)

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
for i in range (int(m.ceil(v_div / 2.0))):
    for j in range(surface_count):
        curve_0 = isocurve_set[j][i]
        curve_1 = isocurve_set[(j - 1) % surface_count][v_div - i]
        t0, t1 = curve_0.Domain[0], curve_1.Domain[0]
        blend_con = rg.BlendContinuity.Tangency
        blend_curve = rg.Curve.CreateBlendCurve(curve_0, t0, True, blend_con, curve_1, t1, True, blend_con)
        blended_curves[j].append(blend_curve)
        blend_crvs_vis.append(blend_curve)
