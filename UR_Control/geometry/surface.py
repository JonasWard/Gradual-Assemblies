import Rhino.Geometry as rg
from geometry.beam import Beam
import copy
import math

class Surface(object):

    def __init__(self, surface, u_div=5, v_div=3, beam_width = 160, beam_thickness = 40):

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

        self.beam_w = beam_width
        self.beam_t = beam_thickness

    def instantiate_beams_even(self, will_flip=False):
        """ Method that instantiates the beams
        :param will_flip:       Whether the beam grid start with a or no beam
        """
        self.beams = []

        surface = self.__offset_sides_surface(self.surface, self.beam_t  / 2)
        self.surface = self.__seam_regrades(surface)

        surface = self.surface

        if will_flip:

            # flip
            domain = rg.Interval(0, 1)
            surface.Reverse(0, True)
            surface.SetDomain(0, domain)

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

                beam = Beam(plane, length, self.beam_w, self.beam_t)

                inner_arr.append(beam)

            self.beams.append(inner_arr)

        if will_flip:

            # flip back
            domain = rg.Interval(0, 1)
            surface.Reverse(0, True)
            surface.SetDomain(0, domain)
            self.beams = list(reversed(self.beams))

    def instantiate_beams_u_shift_pattern(self, will_flip=False, u_split_pattern = [1/3, 2/3]):

        self.beams = []

        self.multi_flush_seams(0, False, count = len(u_split_pattern))
        surface = self.__offset_sides_surface(self.surface, self.offset_value)
        self.surface = self.__seam_regrades(surface)

        surface = self.surface

        if will_flip:

            # flip
            domain = rg.Interval(0, 1)
            surface.Reverse(0, True)
            surface.SetDomain(0, domain)

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

                beam = Beam(plane, length, 160, 40)

                inner_arr.append(beam)

            self.beams.append(inner_arr)

        if will_flip:

            # flip back
            domain = rg.Interval(0, 1)
            surface.Reverse(0, True)
            surface.SetDomain(0, domain)
            self.beams = list(reversed(self.beams))

    def double_flush_seams(self, location = 0, will_flip = False, count = 2):
        """ method to create a flush seam with n amount of beams

        :param location:    Whether you're considering the end or the start of the system (defualt = 0)
        :param will_flip:   What the start condition is (default = False)
        :param count:       How many beams (default 2)
        """

        # remapping the domain of the surface
        self.Surface.SetDomain(0, rg.Interval(0, 1))
        # getting the isocurve of the surface at the given location
        curve = self.surface.GetIsocurve(0, location)
        # getting the domain of the curve
        t_start, t_end = curve.Domain[0], curve.Domain[1]
        t_set = [t_start, (t_end + t_start) / 2, t_end]
        pt_set = [curve.PointAt(t_val) for t_val in t_set]
        curve_plane = rg.Plane(pt_set[0], pt_set[1], pt_set[2])

        # to check whether you're at the start or the end of the surface
        if (location == 0):
            switch_flag = 0
        else:
            switch_flag = -count
        mv_vectors = [curve_plane.ZAxis * self.beam_t * (switch_flag + .5 + i) for i in range(count)]

        # getting the lines
        if (will_flip):
            
        for i, mv_vector in enumerate(mv_vectors):
            local_curve = c.deepcopy(curve)
            pt_0 = []
            line = rg.Line()











    def __offset_sides_surface(self ,surface, offset_dis=20, rel_or_abs = False, sides = 2, sampling_count = 25):
        """ method that returns a slightly shrunk version of the surface along the v direction

            :param surface:         Input surface
            :param offset_dis:      Offset Distance (if int input -> distance, if float input relative)
            :param rel_or_abs:      Flag that states whether you offset the surface absolute or relative - if relative u domain has to be set correctly!!! (rel = True, abs = False, default = False)
            :param sides:           Which sides should be offseted (0 = left, 1 = right, 2 = both, default)
            :param sampling_count:  Precision at which the surface should be rebuild
            :return temp_srf:       The trimmed surface
        """
        temp_surface = copy.deepcopy(surface)

        # case that surface offset is relative
        if rel_or_abs:
            u_div = surface.Domain(0)
            if (sides == 0):
                offsets = 1
            elif (sides == 1):
                offsets = 1
            elif (sides == 2):
                offsets = 2
            # making sure you don't make the surface dissappear
            if offset_dis * offsets > .9 * u_div:
                offset_dis = .9 * u_div / offsets

        temp_surface.SetDomain(1, rg.Interval(0, sampling_count - 1))
        temp_isocurves = [temp_surface.IsoCurve(0, v_val) for v_val in range(sampling_count)]

        temp_isocurves_shortened = []

        for isocurve in temp_isocurves:
            # getting the length and the domain of every isocurve
            start_t, end_t = isocurve.Domain[0], isocurve.Domain[1]
            t_delta = end_t - start_t
            # calculating how much the offset_dis result in t_val change
            if rel_or_abs:
                t_shift = t_delta * offset_dis
            else:
                length = isocurve.GetLength()
                t_differential = t_delta / length
                t_shift = t_differential * offset_dis

            # creating variations for the different offset options
            start_t_new, end_t_new = start_t, end_t
            if (sides == 0):
                start_t_new = start_t + t_shift
                splits = [start_t_new]
                data_to_consider = 1
            elif (sides == 1):
                end_t_new = end_t - t_shift
                splits = [end_t_new]
                data_to_consider = 0
            elif (sides == 2):
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
