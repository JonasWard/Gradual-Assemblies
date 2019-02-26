# snippet of code that offsets a surface with a certain value along the v direction

import Rhino.Geometry as rg
import copy

### change srf to self, ^^^ NEED THE python.copy LIBRARY!!! ^^^
def offset_sides_surface(srf, offset_dis = 20):
    """ method that returns a slightly shrunk version of the surface along the v direction

        :param offset_dis:       Offset Distance (default 20)
        :return temp_srf:   The trimmed surface
    """
    sampling_count = 25

    temp_surface = copy.deepcopy(srf)

    temp_surface.SetDomain(1, rg.Interval(0, sampling_count - 1))
    temp_isocurves = [temp_surface.IsoCurve(0, v_val) for v_val in range(sampling_count)]

    temp_isocurves_shortened = []

    t_percent = .8

    for isocurve in temp_isocurves:
        # getting the length and the domain of every isocurve
        # length = isocurve.GetLength()
        start_t, end_t = isocurve.Domain[0], isocurve.Domain[1]
        t_delta = end_t - start_t
        # t_differential = t_delta / length
        # calculating how much the offset_dis result in t_val change
        t_shift = t_delta * t_percent
        split_val = start_t + t_shift
        # splitting the curve at those two new start & end points with and taking the middle piece
        new_isocurve = isocurve.Split([split_val])[0]
        temp_isocurves_shortened.append(new_isocurve)

    # switchign the uv direction back to where it should be! -> rebuilding the surface
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
    new_surface = rg.Brep.CreateFromLoftRebuild(uv_switched_curves, rg.Point3d.Unset, rg.Point3d.Unset, loft_type, False, 50)[0]
    # getting the loft as a nurbssurface out of the resulting brep
    print new_surface
    print new_surface.Faces.Item[0].ToNurbsSurface()

    return new_surface

# grasshopper variables

srf
value

# return values
temp_surface = offset_sides_surface(srf, value)
