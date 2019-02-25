# surface keystone strategy

import Rhino.Geometry as rg
import math as m
import copy as c
import types

class Keystone(object):
    def __init__(self, srf_set, v_div = 3, blend_precision = None, split_function = 0, f_args = [[0, 0, .15, .05], [0, 0, .2, .05], [0, 0, .2, .05]], loc_pat = [0, 1], blend_overlap = 5, dir = True):
        """ initialization of a surface class based on either a list of input srfs or a nested list of input srfs

            :param srf_set:         List or rg.NurbsSurface 's or nested list of srfs on which the keystone surface set will be based
            :param locat_pattern:   List that describes whether the surface_set is nested, which ones are on top, which ones are on the bottom (default = [0, 1])
            :param v_div:           Defines the amount of divisions in the V direction (if not even then it will be rounded up!)
            :param blend_precision: Int that describes the multiple of v_div that define the EXTRA blend curves that are created to describe the new surface set internally (if not even then it will be rounded up!), (default = None (= 2))
            :param dir:             Boolean used to indicate the direction of the blend creation (default = True)
            :param split_function:  Int that indicates which function defines the split function (default = 0)
            :param f_args:          Nested list of values that apply to the split function (default [[1, 0]])
        """

        # surface check parameters
        self.srf_set = srf_set
        self.__nested_list_qm()
        self.loc_pat = loc_pat
        self.loc = loc_pat[0]
        self.loc_pat_len = len(loc_pat)

        # blend curve parameters
        self.v_div = v_div
        self.blend_crv_count_f(blend_precision, blend_overlap)
        self.dir = dir
        self.blend_crv_split_f = split_function
        self.blend_crv_split_args = f_args[split_function]

        # execution
        if (self.nested_list):
            self.__surface_set_execution()
        else:
            self.loc = self.loc_pat[0]
            self.construct_srfs()

    def __nested_list_qm(self):
        """ Internal method that checks whether the function is fed a list of srf or a nested list """
        if isinstance(self.srf_set[0], types.ListType):
            self.nested_srf_set = c.deepcopy(self.srf_set)
            self.nested_list = True
            self.srf_nest_count = len(self.srf_set)
            print "nested list!"
        else:
            self.nested_list = False
            self.srf_count = len(self.srf_set)
            print "none nested list!"

    def __loc_pattern_based_parameters(self):
        """ Internal method that sets some variables based on what type of surface the keystone srf is """
        if (self.loc == 0):
            self.reverse_list = False
        elif (self.loc == 1):
            self.reverse_list = True
        self.seam_set_count = int(m.ceil(self.srf_nest_count / self.loc_pat_len))
        self.seam_set_item_count = [int(len(self.nested_srf_set[i])) for i in range(self.seam_set_count * 2)]
        print "seam set count: ", self.seam_set_count
        print "seams set items: ", self.seam_set_item_count

    def __surface_set_execution(self):
        """ Internal method that generates the different objects """
        # doing the calculations
        if (self.nested_list):
            self.nested_keystone_srf_list = []
            for i in range(self.srf_nest_count):
                self.srf_set = c.deepcopy(self.nested_srf_set[i])
                self.srf_count = len(self.srf_set)
                self.loc = self.loc_pat[i % self.loc_pat_len]
                self.__loc_pattern_based_parameters()
                if (self.reverse_list):
                    self.srf_set.reverse()
                temp_srfs = c.deepcopy(self.construct_srfs())
                if (self.reverse_list):
                    temp_srfs.reverse()
                    self.srf_set.reverse()
                self.nested_keystone_srf_list.append(temp_srfs)
        # relating all the surfaces
        # self.base_srf_list = source surfaces; self.keystone_srf_list = keystone surfaces
        self.base_srf_list = [[[] for j in range(self.seam_set_item_count[i])] for i in range(self.seam_set_count)]
        self.keystone_srf_list = [[[] for j in range(self.seam_set_item_count[i])] for i in range(self.seam_set_count)]
        for i in range(self.srf_nest_count):
            local_i = int((i - i % self.loc_pat_len) / self.loc_pat_len)
            for j in range(self.seam_set_item_count[local_i]):
                srf_ref = self.nested_srf_set[i][j]
                srf_keystone = self.nested_keystone_srf_list[i][j]
                self.base_srf_list[local_i][j].append(srf_ref)
                self.keystone_srf_list[local_i][j].append(srf_keystone)

        self.base_srf_pair_list = []
        self.keystone_pair_list = []
        for keystone_set in self.base_srf_list:
            for pair in keystone_set:
                self.base_srf_pair_list.append(pair)
        for keystone_set in self.keystone_srf_list:
            for pair in keystone_set:
                self.keystone_pair_list.append(pair)

    def blend_crv_count_f(self, blend_precision, blend_overlap):
        """ method that defines how many isocurves have to be generated and how many than have to be blendend

            :param blend_overlap:       In case it becomes usefull, how many extra blend curves will be considered to smoothen out the surface
            :param blend_precisions:    How much higher the resolution of the isocurves is set than required by the v_divs
        """

        #  making sure the v_div is set to an even value -> uneven amount of beams
        print "v_div = ", self.v_div
        self.v_div += self.v_div % 2
        print "v_div after rounding = ", self.v_div

        if (blend_precision is None or blend_precision == 0 or blend_precision == 2):
            # as if the blend_precision == 2
            self.blend_isocrvs_count = int(self.v_div * 2 - 1)
            self.blend_crv_count = int(self.v_div)
            self.blend_p = 2
            print "blend precision = None"
        else:
            # all other blend_precision values
            blend_precision += blend_precision % 2
            self.blend_p = blend_precision
            self.blend_crv_count = int((self.v_div + (self.v_div - 1) * self.blend_p) / 2)
            self.blend_isocrvs_count = int(self.blend_crv_count * 2 - 1)

        print "blend precision = ", self.blend_p
        print "blend curve count = ", self.blend_crv_count
        print "blend isocurve count = ", self.blend_isocrvs_count

        if (blend_overlap is None or blend_overlap == 0):
            self.blend_overlap = 5
            print "blend overlap = None"
        elif (blend_overlap > self.blend_isocrvs_count - self.blend_crv_count):
            self.blend_overlap = self.blend_isocrvs_count - self.blend_crv_count
        else:
            self.blend_overlap = blend_overlap

    def construct_srfs(self, avg_spacing = 200, rebuild = False):
        """ method that constructs, based on one surface_set, a set of keystone surface_set
            all the methods called in this function don't spit out any variables but rather (over)write properties of the class instance

            :param avg_spacing:         Value that is used to decide at which length +- the isocurves of the surface should be split
            :param rebuild:             Whether to rebuild the blend_crvs or not
            :return self.keystone_srfs: The resulting set of keystone_srfs
        """
        if not(self.nested_list):
            if (self.loc == 1):
                self.srf_set.reverse()

        self.isocurves()
        self.curve_blending(200, rebuild)
        self.blend_curve_split_function()
        self.curve_blend_splicing()
        self.invert_uv_isocurves()
        self.lofting_crvs()

        return self.keystone_srfs

    def isocurves(self):
        """ method that calculates the isocurves """
        self.isocurve_vis = []
        self.isocurve_set = []

        for surface in self.srf_set:
            surface.SetDomain(0, rg.Interval(0, self.blend_isocrvs_count))
            surface.SetDomain(1, rg.Interval(0, self.blend_isocrvs_count))
            local_isocurve_set = []
            for v_val in range(self.blend_isocrvs_count + 1):
                local_isocurve = surface.IsoCurve(0, v_val)
                self.isocurve_vis.append(local_isocurve)
                local_isocurve_set.append(local_isocurve)
            self.isocurve_set.append(local_isocurve_set)

    def curve_blending(self, avg_spacing = 200, rebuild = False):
        """ method that constructs the blend crvs

            :param avg_spacing:         Value that is used to decide at which length +- the isocurves of the surface should be split
            :param rebuild:             Whether to rebuild the blend_crvs or not
        """
        self.blend_crvs = [[] for i in range(self.srf_count)]
        self.blend_crvs_vis = []
        self.avg_spacing = avg_spacing
        self.blend_crv_avg_len = 0

        for i in range (self.blend_crv_count):
            for j in range(self.srf_count):
                curve_0 = self.isocurve_set[j][i]
                curve_1 = self.isocurve_set[(j - 1) % self.srf_count][self.blend_isocrvs_count - i]
                if self.dir:
                    t0, t1 = curve_0.Domain[0], curve_1.Domain[0]
                else:
                    t1, t0 = curve_0.Domain[0], curve_1.Domain[0]
                blend_con = rg.BlendContinuity.Tangency
                local_blend_crv = rg.Curve.CreateBlendCurve(curve_0, t0, self.dir, blend_con, curve_1, t1, self.dir, blend_con)
                if rebuild:
                    local_blend_crv = local_blend_crv.Rebuild(30, 5, False)
                self.blend_crvs[j].append(local_blend_crv)
                self.blend_crv_avg_len += local_blend_crv.GetLength()
                self.blend_crvs_vis.append(local_blend_crv)

        self.blend_crv_avg_len /= (self.blend_crv_count * self.srf_count)
        self.blend_isocrvs_count_count = int(m.ceil(self.blend_crv_avg_len / self.avg_spacing))
        self.blend_isocrvs_count_count += (self.blend_isocrvs_count_count + 1)%2

    def blend_curve_split_function(self):
        """ method that splits a blend_crv """
        #  to do implement average closest point to overlap curves / srf
        # setting up the boundary variables
        if (self.blend_crv_split_f == 0):
            # reading in the f_args
            start_i_shift, start_t_shift, max_t_shift, max_t_shift_diff = self.blend_crv_split_args

            # very very basic splicing function
            start_t_shift = 0 / (2 * (self.blend_isocrvs_count_count - 1))
            shift_start = 1 - .05 * self.srf_count
            shift_max = .025 * self.srf_count
            start_split_index = int(shift_start * self.blend_crv_count + start_i_shift)

        elif (self.blend_crv_split_f == 1 or self.blend_crv_split_f):
            # introducing the variables for intricate splicing function & the sin function
            start_i_shift, start_t_shift, max_t_shift, max_t_shift_diff = self.blend_crv_split_args
            # in case it would be usefull, a start shift can be set!
            if self.loc == 0:
                # means that the first beam is supposed to be flush with the beam on the next surface
                # implies that you only start splicing after the 2nd v split point
                start_split_index = int(self.blend_p * 3 / 2) + start_i_shift
                shift_max = max_t_shift

            elif self.loc == 1:
                # means that the first beam is spaced compored to the surface besides it
                # implies that you start splicing nearly straight away!
                start_split_index = int(self.blend_p / 2) + start_i_shift
                shift_max = max_t_shift + max_t_shift_diff

        # shared by all functions
        split_difference = self.blend_crv_count - start_split_index
        split_differential = shift_max / (split_difference)
        shift_variation = (1 - (1 - shift_max) ** 2) / split_difference ** 2

        # generating the t_vals
        self.t_vals_srf = []

        if (self.blend_crv_split_f < 2):
            # t_vals for the base splicing function and the more intricate one
            for i in range(self.blend_crv_count):
                local_t_vals = []
                if (i < start_split_index):
                    local_t_vals = [.5 - start_t_shift, .5 + start_t_shift]
                else:
                    n_var = i + 1 - start_split_index
                    diff = (1 - m.sqrt(1 - shift_variation * n_var ** 2)) / 2 + start_t_shift
                    local_t_vals = [.5 - diff, .5 + diff]
                self.t_vals_srf.append(local_t_vals)

        elif (self.blend_crv_split_f == 2):
            # setting domain of the sin wave curve
            # domain [a, b] -> [c, d] remapping f(x):
            # f(x) = (c - d) / (a - b) * (x - a) + c;
            # f(x) = p1 * (x - p2) + p3

            # from [indexes] to [-Pi / 2 to Pi / 2]
            a, b = start_split_index - 1, self.blend_crv_count - 1
            half_pi = m.pi / 2
            c, d = -half_pi, half_pi
            p1, p2, p3 = (c - d) / (a - b), a, c
            # from [-1 to 1] to [0, shift_max]
            a, b = -1, 1
            c, d = 0, shift_max
            p4, p5, p6 = (c - d) / (a - b), a, c
            # t_vals for the sin splicing function
            for i in range(self.blend_crv_count):
                local_t_vals = []
                if (i < start_split_index):
                    local_t_vals = [.5 - start_t_shift, .5 + start_t_shift]
                else:
                    # f1 remapping domain, f2 sin, f3 second remapping
                    f1_y = p1 * (i - p2) + p3
                    f2_y = m.sin(f1_y)
                    f3_y = p4 * (f2_y - p5) + p6
                    diff = f3_y + start_t_shift
                    local_t_vals = [.5 - diff, .5 + diff]
                self.t_vals_srf.append(local_t_vals)

    def curve_blend_splicing(self):
        """ method that controls how to split and merge the blend_crvs """

        self.struct_pt_cloud = []
        self.vis_pt_cloud = []
        self.blend_crv_split_set = []
        self.vis_blend_crv_split = []

        temp_new_sets_pos = []
        temp_new_sets_neg = []

        for i in range(self.srf_count):
            local_pos_list = []
            local_neg_list = []
            for j in range(self.blend_crv_count):
                start_t, end_t = self.blend_crvs[i][j].Domain[0], self.blend_crvs[i][j].Domain[1]
                t_delta = end_t - start_t
                local_t_vals = [(start_t + t_delta*t_val) for t_val in self.t_vals_srf[j]]
                tmp_crvs = self.blend_crvs[i][j].Split(local_t_vals)
                tmp_crv_0, tmp_crv_1 = tmp_crvs[0], tmp_crvs[-1]
                tmp_crv_1.Reverse()
                local_pos_list.append(tmp_crv_0)
                local_neg_list.append(tmp_crv_1)
                self.vis_blend_crv_split.append(tmp_crv_0)
                self.vis_blend_crv_split.append(tmp_crv_1)
            local_neg_list.reverse()
            temp_new_sets_pos.append(local_pos_list)
            temp_new_sets_neg.append(local_neg_list)

        for j in range(self.srf_count):
            local_set = temp_new_sets_pos[j]
            local_set.extend(temp_new_sets_neg[(j + 1) % self.srf_count])
            self.blend_crv_split_set.append(local_set)

    def invert_uv_isocurves(self):
        """ method that inverts the new uv_isocurves """
        self.vis_uv_switched_crvs = []
        self.uv_switched_crvs_set = []
        self.vis_uv_switched_pt_set = []
        for j in range(self.srf_count):
            # inverting the surface directions

            sampling_count = 7
            # switching the uv direction back to where it should be! -> rebuilding the surface
            point_list = [[] for i in range(sampling_count)]
            for temp_curve in self.blend_crv_split_set[j]:
                length = temp_curve.GetLength()
                start_t, end_t = temp_curve.Domain[0], temp_curve.Domain[1]
                t_delta = end_t - start_t
                t_differential = t_delta / (sampling_count - 1)
                # calculating how much the offset_dis result in t_val change
                point_set = [temp_curve.PointAt(t_val * t_differential + start_t) for t_val in range(0, sampling_count, 1)]
                for i, point in enumerate(point_set):
                    point_list[i].append(rg.Point3d(point))

            uv_switched_crvs = []
            for point_set in point_list:
                local_curve = rg.NurbsCurve.Create(False, 4, point_set)
                self.vis_uv_switched_pt_set.extend(point_set)
                uv_switched_crvs.append(local_curve)
                self.vis_uv_switched_crvs.append(local_curve)
            self.uv_switched_crvs_set.append(uv_switched_crvs)

    def lofting_crvs(self):
        """ method that create the keystone srfs """
        self.keystone_srfs = []
        loft_type = rg.LoftType.Tight
        for uv_switched_crvs in self.uv_switched_crvs_set:
            local_new_srf = rg.Brep.CreateFromLoftRebuild(uv_switched_crvs, rg.Point3d.Unset, rg.Point3d.Unset, loft_type, False, 50)[0]
            local_new_srf = c.deepcopy(local_new_srf.Faces.Item[0].ToNurbsSurface())
            self.keystone_srfs.append(local_new_srf)

    def output(self):
        """ method that returns the organised surfaces
        :return reference_srf_set, keystone_srf_set:    As the name says, either 2 x list of srfs or 2 x a nested list of srfs, grouped together based on the assembly logic
        """
        if self.nested_list:
            keystone_srf_set = self.keystone_pair_list
            reference_srf_set = self.base_srf_pair_list
        else:
            keystone_srf_set = self.keystone_srfs
            reference_srf_set = self.srf_set

        return reference_srf_set, keystone_srf_set
