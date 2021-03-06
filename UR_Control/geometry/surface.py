import Rhino.Geometry as rg
from geometry.beam import Beam
import copy
import math

class Surface(object):

    def __init__(self, surface, u_div=5, v_div=3, beam_width = 160, beam_thickness = 40):
        """ Initialization

        :param surface:         Base rg.geometry object that will be edited
        :param u_div:           How many divisions this surface will have in the u_direction (default = 5)
        :param v_div:           How many divisions this surface will have in the v_direction (default = 3)
        :param beam_width:      The initial width of the beams (default = 160)
        :param beam_thickness:  The initial thickness of the different beams (default = 40)
        """

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

    def instantiate_beams(self, mapping_type = 0, seam_type = 0, warp_type = 3, will_flip = False, flush_beam_count = 2):
        """ Function that instatiates the beam generation

        :param mapping_type:    Some default types of surface logics applied ([1] = even - default, [2/3, 1] = seaming type)
        :param seam_type:       Which type of seam this object has (0 = single flush - default, 1 = multi flush left, 2 = multi flush right, 3 = multi flush both sides)
        :param warp_type:       How the surface is being warped (0 = no warping - default, 1 = left, 2 = right, 3 = both sides)
        :param will_flip:       Whether the surface will flip or not (default = False)
        """

        self.mapping_type = [[1], [2/3, 1]][mapping_type]
        self.seam_type = seam_type
        self.warp_type = warp_type
        self.will_flip = will_flip
        self.flush_beam_count = flush_beam_count

        self.warped_srf = copy.deepcopy(self.surface)

        # changing the u_div count in relation to the mapping_type
        total_flush_beam_count = math.round(self.seam_type / 2.0) * self.flush_beam_count
        self.mapping_pattern_length = len(self.mapping_type)

        # checking whether there are enough u_div to map out a surface in the middle
        if self.u_div < total_flush_beam_count:
            self.main_srf_div = 2
            self.u_div = self.main_srf_div * self.mapping_pattern_length + total_flush_beam_count

        # checking whether the amount of splits in the middle is a multiple of it's mapping_pattern_len
        elif not(int(self.u_div - total_flush_beam_count) % self.mapping_pattern_length == 0):
            self.main_srf_div = math.ceil((self.u_div - total_flush_beam_count) / self.mapping_pattern_length)
            self.u_div = self.main_srf_div * self.mapping_pattern_length + total_flush_beam_count

        # initializing the beam set
        self.beams = []

        if self.will_flip:

            # flip
            domain = rg.Interval(0, 1)
            self.surface.Reverse(0, True)
            self.surface.SetDomain(0, domain)

        self.end_isocrvs = [self.surface.GetIsocurve(0, 0), self.surface.GetIsocurve(0, 1)]

        # setting up how and what needs to be run in order
        # does flipping matter here ???

        o_half_t = .5 * self.beam_t
        o_flush_seam = (self.flush_beam_count - .5) * self.beam_t

        # starting condition of the beam instantiation
        self.div_counter = 0

        # single - flush condition
        if self.seam_type == 0:
            # simple even condition
            # absolute offset of half the beam_t
            self.__offset_sides_surface(offset_dis = o_half_t, sides = 3)
            self.__warp_surface()
            self.__instantiate_main_beams(start_beams = True, end_beams = True)

        # multi - flush condition on the left
        elif self.seam_type == 1:
            # flush condition on the left
            # initializing the flush beams
            self.__multi_flush_seams(location = 0)

            self.__offset_sides_surface(offset_dis = o_flush_seam, sides = 1)
            self.__offset_sides_surface(offset_dis = o_half_t, sides = 2)
            self.__warp_sides_surface()
            self.__instantiate_main_beams(start_beams = False, end_beams = True)

        # multi - flush condition on the right
        elif self.seam_type == 2:
            # flush condition on the right
            self.__offset_sides_surface(offset_dis = o_flush_seam, sides = 2)
            self.__offset_sides_surface(offset_dis = o_half_t, sides = 1)
            self.__warp_sides_surface()
            self.__instantiate_main_beams(start_beams = True, end_beams = False)

            # initializing the flush beams
            self.__multi_flush_seams(location = 1)

        # multi - flush conditon on both sides
        elif self.seam_type == 3:
            # flush condition on both sides
            # initializing the first set of flush conditions
            self.__multi_flush_seams(location = 0)

            self.__offset_sides_surface(offset_dis = o_flush_seam, sides = 3)
            self.__warp_sides_surface()

            # initializing the second set of flush conditions
            self.__multi_flush_seams(location = 1)

        if will_flip:

            # flip back
            domain = rg.Interval(0, 1)
            self.surface.Reverse(0, True)
            self.surface.SetDomain(0, domain)
            # reversing the direction of the base_plane of the beam
            self.beams = list(reversed(self.beams))

    def __instantiate_main_beams(self, start_beams = False, end_beams = False):
        """ internal method that sets out the beams on the main surface

        :param start_beams:     Whether the main surface is mapped from the left edge of the surface or skips over the first one
        :param end_beams:       Whether the main surface is mapped until the end on the right or the last one is ignored
        """

        division_range = (int(start_beams) + self.main_srf_div - 1 + int(end_beams))
        u_val_list = []
        [u_val_list.extend([(u_map_set_val + u_val / division_range) for u_map_set_val in self.mapping_type]) for u_val in range(int(start_beams), int(start_beams) + self.main_srf_div, 1)]

        for u in u_val_list:

            inner_arr = []

            for v in range(self.v_div):

                if (self.div_counter % 2 == 0 and v % 2 == 1) or (self.div_counter % 2 == 1 and v % 2 == 0):
                    continue

                p1 = self.warped_srf.PointAt(u, float(v)/self.v_div)
                p2 = self.warped_srf.PointAt(u, float(v+1)/self.v_div)

                length = p1.DistanceTo(p2)

                center = rg.Point3d((p1 + p2) / 2)

                _, uu, vv = self.warped_srf.ClosestPoint(center)

                normal = self.warped_srf.NormalAt(uu, vv)
                x_axis = rg.Vector3d(p1) - rg.Vector3d(p2)
                x_axis.Unitize()
                y_axis = rg.Vector3d.CrossProduct(normal, x_axis)

                plane = rg.Plane(center, x_axis, normal)

                beam = Beam(plane, length, self.beam_w, self.beam_t)

                inner_arr.append(beam)

            self.beams.append(inner_arr)
            self.div_counter += 1

    def __multi_flush_seams(self, location = 0, will_flip = False):
        """ method to create a flush seam with n amount of beams

        :param location:    Whether you're considering the end or the start of the system (defualt = 0)
        :param will_flip:   What the start condition is (default = False)
        """

        # getting the correct isocurve of the surface
        local_curve = self.end_isocrvs[location]

        # getting the domain of the curve
        t_start, t_end = local_curve.Domain[0], local_curve.Domain[1]
        t_delta = t_end - t_start
        t_set = [t_start, (t_end + t_start) / 2, t_end]
        pt_set = [local_curve.PointAt(t_val) for t_val in t_set]
        curve_plane = rg.Plane(pt_set[0], pt_set[1], pt_set[2])

        # getting the t_values on that curve to describe the beam lines
        t_vals = [t_start + t_delta * v / (self.v_div + 1) for v in range (self.v_div + 1)]

        # generating the move vectors for the curves
        # to check whether you're at the start or the end of the surface
        if (location == 0):
            switch_flag = 0
        else:
            switch_flag = - self.flush_beam_count

        mv_vectors = [curve_plane.ZAxis * self.beam_t * (switch_flag + .5 + i) for i in range(self.flush_beam_count )]

        # # getting the lines
        # if (will_flip):

        for mv_vector in mv_vectors:

            temp_curve = copy.deepcopy(local_curve)
            temp_curve.Translate(mv_vector)

            inner_arr = []

            for v in range(self.v_div):

                if (self.div_counter % 2 == 0 and v % 2 == 1) or (self.div_counter % 2 == 1 and v % 2 == 0):
                    continue

                p1 = temp_curve.PointAt(t_vals[v])
                p2 = temp_curve.PointAt(t_vals[v + 1])

                length = p1.DistanceTo(p2)

                center = rg.Point3d((p1 + p2) / 2)

                z_axis = curve_plane.ZAxis
                x_axis = rg.Vector3d(p1) - rg.Vector3d(p2)
                x_axis.Unitize()
                y_axis = rg.Vector3d.CrossProduct(z_axis, x_axis)

                plane = rg.Plane(center, x_axis, y_axis)

                beam = Beam(plane, length, self.beam_w, self.beam_t)

                inner_arr.append(beam)

            self.beams.append(inner_arr)
            self.div_counter += 1

    def __offset_sides_surface(self , offset_dis=20, rel_or_abs = False, sides = 0, sampling_count = 25):
        """ method that returns a slightly shrunk version of the surface along the v direction

            :param offset_dis:      Offset Distance (abs or relative)
            :param rel_or_abs:      Flag that states whether you offset the surface absolutely or relative - if relative u domain has to be set correctly!!! (rel = True, abs = False, default = False)
            :param sides:           Which sides should be offseted (0 = nothing - default, 1 = left, 2 = right, 3 = both)
            :param sampling_count:  Precision at which the surface should be rebuild
        """

        # first of all checking whether you have to do anything at all
        if not (sides == 0):
            local_srf = self.warped_srf

            # case that surface offset is relative
            if rel_or_abs:
                u_div = local_srf.Domain(0)
                if (sides == 1):
                    offsets = 1
                elif (sides == 2):
                    offsets = 1
                elif (sides == 3):
                    offsets = 2
                # making sure you don't make the surface dissappear
                if offset_dis * offsets > .9 * u_div:
                    offset_dis = .9 * u_div / offsets

            local_srf.SetDomain(1, rg.Interval(0, sampling_count - 1))
            temp_isocurves = [local_srf.IsoCurve(0, v_val) for v_val in range(sampling_count)]

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
                if (sides == 1):
                    start_t_new = start_t + t_shift
                    splits = [start_t_new]
                    data_to_consider = 1
                elif (sides == 2):
                    end_t_new = end_t - t_shift
                    splits = [end_t_new]
                    data_to_consider = 0
                elif (sides == 3):
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
            local_srf = rg.Brep.CreateFromLoftRebuild(uv_switched_curves, rg.Point3d.Unset, rg.Point3d.Unset, loft_type, False, 50)[0]
            # getting the loft as a nurbssurface out of the resulting brep
            local_srf = local_srf.Faces.Item[0].ToNurbsSurface()

            domain = rg.Interval(0, 1)
            local_srf.SetDomain(0, domain)
            local_srf.SetDomain(1, domain)

            self.warped_srf = local_srf
        else:
            # in case you don't have to do anything at all you do nothing at all !?
            pass

    def __warp_sides_surface(self, grading_percentage = .5, precision = 25):
        """ method that makes the beams move closer to each other at the seams
            :param grading_percentage:  Percent of the surface that is being regraded (default .5)
        """

        # first of all checking whether you have to do anything at all
        if not(self.warp_type == 0):
            local_srf = self.warped_srf
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
            if (self.warp_type == 1):
                # only on the left side
                t_vals = []
                for t_val in ini_t_vals:
                    local_t_val += t_val
                    t_vals.append(local_t_val)
            elif (self.warp_type == 2):
                # only on the right side
                t_vals = []
                ini_t_vals.reverse()
                local_ini_t_vals = [0]
                local_ini_t_vals.extend(ini_t_vals[:-1])
                for t_val in local_ini_t_vals:
                    local_t_val += t_val
                    t_vals.append(local_t_val)
            elif (self.warp_type == 3):
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
            self.warped_srf = local_srf
        else:
            # in case you don't have to do anything at all you do nothing at all !?
            pass
