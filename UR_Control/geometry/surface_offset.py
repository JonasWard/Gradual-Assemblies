# snippet of code that offsets a surface with a certain value along the v direction

import Rhino.Geometry as rg
import copy

### change srf to self, ^^^ NEED THE python.copy LIBRARY!!! ^^^
def __offset_sides_surface(self, offset_dis=20, sides = 2, sampling_count = 25):
    """ method that returns a slightly shrunk version of the surface along the v direction
        :param offset_dis:      Offset Distance (default 20)
        :param sides:           Which sides should be offseted (0 = left, 1 = right, 2 = both, default)
        :param sampling_count:  Precision at which the surface should be rebuild
        :return temp_srf:       The trimmed surface
    """
    temp_surface = copy.deepcopy(self.surface)

    temp_surface.SetDomain(1, rg.Interval(0, sampling_count - 1))
    temp_isocurves = [temp_surface.IsoCurve(0, v_val) for v_val in range(sampling_count)]

    temp_isocurves_shortened = []

    for isocurve in temp_isocurves:
        # getting the length and the domain of every isocurve
        length = isocurve.GetLength()
        start_t, end_t = isocurve.Domain[0], isocurve.Domain[1]
        t_delta = end_t - start_t
        t_differential = t_delta / length
        # calculating how much the offset_dis result in t_val change
        t_shift = t_differential * offset_dis
        # creating variations for the different offset options
        start_t_new, end_t_new = start_t, end_t
        if (sides == 0):
            start_t_new = start_t + t_shift
            splits = [start_t_new]
            data_to_consider = 1
        if (sides == 1):
            end_t_new = end_t - t_shift
            splits = [end_t_new]
            data_to_consider = 0
        if (sides == 2):
            start_t_new = start_t + t_shift
            end_t_new = end_t - t_shift
            splits = [start_t_new, end_t_new]
            data_to_consider = 1

        # splitting the curve at the values in the split list, picking the curve based on the split type
        new_isocurve = isocurve.Split(splits)[data_to_consider]
        temp_isocurves_shortened.append(new_isocurve)

    # switching the uv direction back to where it should be! -> rebuilding the surface
    point_list = [[] for i in range(sampling_count)]
    for temp_curve in temp_isocurves_shortened:
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
        local_isocurve = rg.NurbsCurve.Create(False, 3, point_set)
        uv_switched_curves.append(local_isocurve)

    # lofting those isocurves
    loft_type = rg.LoftType.Tight
    srf = rg.Brep.CreateFromLoftRebuild(uv_switched_curves, rg.Point3d.Unset, rg.Point3d.Unset, loft_type, False, 50)[0]
    # getting the loft as a nurbssurface out of the resulting brep
    srf = srf.Faces.Item[0].ToNurbsSurface()

    domain = rg.Interval(0, 1)
    srf.SetDomain(0, domain)
    srf.SetDomain(1, domain)

    return srf

# grasshopper variables

srf
value

# return values
temp_surface = offset_sides_surface(srf, value)
