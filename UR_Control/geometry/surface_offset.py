# snippet of code that offsets a surface with a certain value along the v direction

import Rhino.Geometry as rg
import copy

def offset_sides_surface(srf, value = 20):
    """ method that returns a slightly shrunk version of the surface along the v direction

        :param value:       Offset Distance (default 20)
        :return temp_srf:   The trimmed surface
    """
    sampling_count = 25

    temp_surface = copy.deepcopy(srf)

    temp_surface.SetDomain(1, rg.Interval(0, sampling_count - 1))
    print temp_surface.Domain(1)
    temp_isocurves = [temp_surface.IsoCurve(0, v_val) for v_val in range(sampling_count)]

    temp_isocurves_shortened = []
    for isocurve in temp_isocurves:
        length = isocurve.GetLength()
        start_t, end_t = isocurve.Domain[0], isocurve.Domain[1]
        t_delta = end_t - start_t
        t_differential = t_delta / length
        t_shift = t_differential * value
        start_t_new = start_t + t_shift
        end_t_new = end_t - t_shift
        new_isocurve = isocurve.Split([start_t_new, end_t_new])[1]
        temp_isocurves_shortened.append(new_isocurve)

    loft_type = rg.LoftType.Tight
    new_surface = rg.Brep.CreateFromLoftRebuild(temp_isocurves_shortened, rg.Point3d.Unset, rg.Point3d.Unset, loft_type, False, 50)[0]
    print new_surface.ToNurbsSurface()


    return temp_isocurves_shortened, new_surface

# grasshopper variables

srf
value

# return values
isocurves, temp_surface = offset_sides_surface(srf, value)
