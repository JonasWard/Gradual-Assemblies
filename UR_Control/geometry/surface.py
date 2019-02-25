import Rhino.Geometry as rg
from geometry.beam import Beam
import copy
import math

class Surface(object):

    def __init__(self, surface, u_div=5, v_div=3, offset_value=20):

        domain = rg.Interval(0, 1)
        surface.SetDomain(0, domain)
        surface.SetDomain(1, domain)

        self.surface = surface
        self.shared_edges = []

        self.bottom_curve = surface.IsoCurve(0, 0)
        self.top_curve    = surface.IsoCurve(0, 1)
        self.left_curve   = surface.IsoCurve(1, 0)
        self.right_curve  = surface.IsoCurve(1, 1)

        self.bottom_pt = self.bottom_curve.PointAt(0.5)
        self.top_pt    = self.top_curve.PointAt(0.5)
        self.left_pt   = self.left_curve.PointAt(0.5)
        self.right_pt  = self.right_curve.PointAt(0.5)

        self.u_div = u_div
        self.v_div = v_div
        self.offset_value = offset_value

        self.__instantiate_beams()

    def __instantiate_beams(self):

        self.beams = []

        surface = self.__offset_sides_surface(self.surface, self.offset_value)
        self.surface = self.__seam_regrades(surface)

        surface = self.surface

        for u in range(self.u_div + 1):

            inner_arr = []

            for v in range(self.v_div):

                if (u % 2 == 0 and v % 2 == 1) or (u % 2 == 1 and v % 2 == 0):
                    continue

                p1 = surface.PointAt(float(u)/self.u_div, float(v)/self.v_div)
                p2 = surface.PointAt(float(u)/self.u_div, float(v+1)/self.v_div)

                length = p1.DistanceTo(p2)

                center = rg.Point3d((p1 + p2) / 2)

                _, uu, vv = surface.ClosestPoint(center)

                normal = surface.NormalAt(uu, vv)
                x_axis = rg.Vector3d(p1) - rg.Vector3d(p2)
                x_axis.Unitize()
                y_axis = rg.Vector3d.CrossProduct(normal, x_axis)

                plane = rg.Plane(center, x_axis, normal)

                beam = Beam(plane, length, 80, 20)

                inner_arr.append(beam)

            self.beams.append(inner_arr)

    def __offset_sides_surface(self ,surface, offset_dis=20, sides = 2, sampling_count = 25):
        """ method that returns a slightly shrunk version of the surface along the v direction
            :param offset_dis:      Offset Distance (default 20)
            :param sides:           Which sides should be offseted (0 = left, 1 = right, 2 = both, default)
            :param sampling_count:  Precision at which the surface should be rebuild
            :return temp_srf:       The trimmed surface
        """
        temp_surface = copy.deepcopy(surface)

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

    def __seam_regrades(self, surface, grading_percentage = .5, grading_side = 2, precision = 25):
        """ method that makes the beams move closer to each other at the seams
            :param grading_percentage:  Percent of the surface that is being regraded (default .5)
            :param grading_sides:       Which sides of the surface have to be regraded (0 = left, 1 = right, 2 = both, default)
            :return regraded_srf:       The uv_regraded_srf
        """

        local_srf = copy.deepcopy(surface)
        u_extra_precision = int(math.ceil(25 / grading_percentage)) - precision
        half_pi = math.pi / 2.0
        half_pi_over_precision = half_pi / (precision - 1)

        # setting up the base grading t_vals
        ini_t_vals = []
        total_t_vals = u_extra_precision
        for i in range(precision):
            alfa = half_pi_over_precision * i
            local_t_val = math.sin(alfa)
            ini_t_vals.append(local_t_val)
            total_t_vals += local_t_val

        [ini_t_vals.append(1) for i in range(u_extra_precision)]

        # setting up the grading list for the amount of sides
        local_t_val = 0
        if (grading_side == 0):
            # only on the left side
            t_vals = []
            for t_val in ini_t_vals:
                local_t_val += t_val
                t_vals.append(local_t_val)
        elif (grading_side == 1):
            # only on the right side
            t_vals = []
            ini_t_vals.reverse()
            local_ini_t_vals = [0]
            local_ini_t_vals.extend(ini_t_vals[:-1])
            for t_val in local_ini_t_vals:
                local_t_val += t_val
                t_vals.append(local_t_val)
        elif (grading_side == 2):
            # on both sides
            t_vals = []
            local_ini_t_vals = ini_t_vals[:]
            ini_t_vals.reverse()
            local_ini_t_vals.extend(ini_t_vals[:-1])
            for t_val in local_ini_t_vals:
                local_t_val += t_val
                t_vals.append(local_t_val)

        # getting the v isocurves
        val_0, val_1 = t_vals[0], t_vals[-1]
        local_srf.SetDomain(1, rg.Interval(0, precision - 1))
        temp_srf_iscrv_set = [local_srf.IsoCurve(0, v_val) for v_val in range(precision)]
        pt_list = [[] for i in range(len(t_vals))]
        for isocrv in temp_srf_iscrv_set:
            t_start, t_end = isocrv.Domain[0], isocrv.Domain[1]
            t_delta = t_end - t_start
            t_differential = t_delta / val_1
            [pt_list[i].append(isocrv.PointAt(t_start + t_val * t_differential)) for i, t_val in enumerate(t_vals)]

        # constructing new isocurves
        loft_curves = [rg.NurbsCurve.Create(False, 3, pt_set) for pt_set in pt_list]
        loft_type = rg.LoftType.Tight
        local_srf = rg.Brep.CreateFromLoftRebuild(loft_curves, rg.Point3d.Unset, rg.Point3d.Unset, loft_type, False, 50)[0]
        # getting the loft as a nurbssurface out of the resulting brep
        new_srf = local_srf.Faces.Item[0].ToNurbsSurface()

        domain = rg.Interval(0, 1)
        new_srf.SetDomain(0, domain)
        new_srf.SetDomain(1, domain)

        return new_srf