# simple surface warping program

import Rhino.Geometry as rg
import math as m

# grasshopper parameters

srf
grading_percentage
grading_side

def warp(srf, grading_percentage = .5, grading_side = 2):
    """ method that makes the beams move closer to each other at the seams

        :param srf:                 Input surface
        :param grading_percentage:  Percent of the surface that is being regraded (default .5)
        :param grading_sides:       Which sides of the surface have to be regraded (0 = left, 1 = right, 2 = both, default)
        :return regraded_srf:       The uv_regraded_srf
    """

    precision = 25
    u_extra_precision = int(m.ceil(25 / grading_percentage)) - precision
    half_pi = m.pi / 2.0
    half_pi_over_precision = half_pi / (precision - 1)

    # setting up the base grading t_vals
    ini_t_vals = []
    total_t_vals = u_extra_precision
    for i in range(precision):
        alfa = half_pi_over_precision * i
        local_t_val = m.sin(alfa)
        ini_t_vals.append(local_t_val)
        total_t_vals += local_t_val

    [ini_t_vals.append(1) for i in range(u_extra_precision)]

    # setting up the grading list for the amount of sides
    local_t_val = 0
    if (grading_side == 0):
        t_vals = []
        for t_val in ini_t_vals:
            local_t_val += t_val
            t_vals.append(local_t_val)
    elif (grading_side == 1):
        t_vals = []
        ini_t_vals.reverse()
        local_ini_t_vals = [0]
        local_ini_t_vals.extend(ini_t_vals[:-1])
        for t_val in local_ini_t_vals:
            local_t_val += t_val
            t_vals.append(local_t_val)
    elif (grading_side == 2):
        t_vals = []
        local_ini_t_vals = ini_t_vals[:]
        ini_t_vals.reverse()
        local_ini_t_vals.extend(ini_t_vals[:-1])
        for t_val in local_ini_t_vals:
            local_t_val += t_val
            t_vals.append(local_t_val)

    # getting the v isocurves
    val_0, val_1 = t_vals[0], t_vals[-1]
    srf.SetDomain(1, rg.Interval(0, precision - 1))
    temp_srf_iscrv_set = [srf.IsoCurve(0, v_val) for v_val in range(precision)]
    pt_list = [[] for i in range(len(t_vals))]
    for isocrv in temp_srf_iscrv_set:
        t_start, t_end = isocrv.Domain[0], isocrv.Domain[1]
        t_delta = t_end - t_start
        t_differential = t_delta / val_1
        [pt_list[i].append(isocrv.PointAt(t_start + t_val * t_differential)) for i, t_val in enumerate(t_vals)]

    print pt_list[0]

    # constructing new isocurves
    loft_curves = [rg.NurbsCurve.Create(False, 3, pt_set) for pt_set in pt_list]
    loft_type = rg.LoftType.Tight
    srf = rg.Brep.CreateFromLoftRebuild(loft_curves, rg.Point3d.Unset, rg.Point3d.Unset, loft_type, False, 50)[0]
    # getting the loft as a nurbssurface out of the resulting brep
    new_srf = srf.Faces.Item[0].ToNurbsSurface()

    domain = rg.Interval(0, 1)
    new_srf.SetDomain(0, domain)
    new_srf.SetDomain(1, domain)

    return new_srf, loft_curves, temp_srf_iscrv_set

new_srf, crvs, isocrvs = warp(srf, grading_percentage, grading_side)
