# surface keystone strategy

import Rhino.Geometry as rg
import math as m
import copy
import types

# grasshopper inputs

srf_set

# local inputs

class Keystone(object):
    def __init__(self, srf_set, v_div, blend_precision = None, dir = True, split_function = 0):
        self.srf_set = srf_set
        self.__nested_list_qm()
        self.srf_count = len(srf_set)

        self.blend_crv_count_f(blend_precision)
        self.dir = dir
        self.v_div = v_div

        self.blend_crv_split_f = split_function

    def __nested_list_qm(self):
        if isinstance(self.srf_set[0], types.ListType):
            self.nested_list = True
        else:
            self.nested_list = False

    def blend_crv_count_f(self, blend_precision):
        if blend_precision == None:
            self.blend_div = 10 * 2 + 1
            self.blend_crv_count = 10
            print "blend precision = None"
        else:
            self.blend_div = (blend_precision * 2 - 1)
            self.blend_crv_count = blend_precision
            print "blend precision = ", blend_precision

    def construct_srf(self, avg_spacing = 200, rebuild = False):
        self.isocurves()
        self.curve_blending(200, rebuild)
        self.blend_curve_split_function()
        self.curve_blend_splicing(0)
        self.invert_uv_isocurves()
        self.lofting_crvs()

        return self.keystone_srfs

    def isocurves(self):
        self.isocurve_vis = []
        self.isocurve_set = []

        for surface in self.srf_set:
            surface.SetDomain(0, rg.Interval(0, self.blend_div))
            surface.SetDomain(1, rg.Interval(0, self.blend_div))
            local_isocurve_set = []
            for v_val in range(self.blend_div + 1):
                local_isocurve = surface.IsoCurve(0, v_val)
                self.isocurve_vis.append(local_isocurve)
                local_isocurve_set.append(local_isocurve)
            self.isocurve_set.append(local_isocurve_set)

    def curve_blending(self, avg_spacing = 200, rebuild = False):
        self.blend_crvs = [[] for i in range(self.srf_count)]
        self.blend_crvs_vis = []
        self.avg_spacing = avg_spacing
        self.blend_crv_avg_len = 0

        for i in range (self.blend_crv_count):
            for j in range(self.srf_count):
                curve_0 = self.isocurve_set[j][i]
                curve_1 = self.isocurve_set[(j - 1) % self.srf_count][self.blend_div - i]
                if self.dir:
                    t0, t1 = curve_0.Domain[0], curve_1.Domain[0]
                else:
                    t1, t0 = curve_0.Domain[0], curve_1.Domain[0]
                blend_con = rg.BlendContinuity.Tangency
                local_blend_crv = rg.Curve.CreateBlendCurve(curve_0, t0, self.dir, blend_con, curve_1, t1, self.dir, blend_con)
                if rebuild:
                    local_blend_crv = local_blend_crv.Rebuild(30, 3, False)
                self.blend_crvs[j].append(local_blend_crv)
                self.blend_crv_avg_len += local_blend_crv.GetLength()
                self.blend_crvs_vis.append(local_blend_crv)

        self.blend_crv_avg_len /= (self.blend_crv_count * self.srf_count)
        self.blend_div_count = int(m.ceil(self.blend_crv_avg_len / self.avg_spacing))
        self.blend_div_count += (self.blend_div_count + 1)%2

    def blend_curve_split_function(self):

        # TODO Implement v_div as a variable
        if (self.blend_crv_split_f == 0):
            start_shift = 0 / (2 * (self.blend_div_count - 1))
            shift_start = 1 - .05 * self.srf_count
            shift_max = .025 * self.srf_count
            start_split_index = int(shift_start * self.blend_crv_count)
            split_difference = self.blend_crv_count - start_split_index
            split_differential = shift_max / (split_difference)
            shift_variation = (1 - (1 - shift_max) ** 2) / split_difference ** 2

            self.t_vals_srf = []
            for i in range(self.blend_crv_count):
                local_t_vals = []
                if (i < start_split_index):
                    diff = start_shift
                    local_t_vals = [.5 - diff, .5 + diff]
                else:
                    n_var = i + 1 - start_split_index
                    diff = (1 - m.sqrt( 1 - shift_variation * n_var ** 2)) / 2 + start_shift
                    local_t_vals = [.5 - diff, .5 + diff]
                self.t_vals_srf.append(local_t_vals)

    def curve_blend_splicing(self, function_type = 0):
        self.struct_pt_cloud = []
        self.vis_pt_cloud = []
        self.blend_crv_split_set = []
        self.vis_blend_crv_split = []
        self.blend_crv_split_f = function_type

        print self.t_vals_srf

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
                local_curve = rg.NurbsCurve.Create(False, 5, point_set)
                self.vis_uv_switched_pt_set.extend(point_set)
                uv_switched_crvs.append(local_curve)
                self.vis_uv_switched_crvs.append(local_curve)
            self.uv_switched_crvs_set.append(uv_switched_crvs)

    def lofting_crvs(self):
        self.keystone_srfs = []
        loft_type = rg.LoftType.Tight
        for uv_switched_crvs in self.uv_switched_crvs_set:
            local_new_srf = rg.Brep.CreateFromLoftRebuild(uv_switched_crvs, rg.Point3d.Unset, rg.Point3d.Unset, loft_type, False, 50)[0]
            local_new_srf.Faces.Item[0].ToNurbsSurface()
            local_new_srf = copy.deepcopy(local_new_srf)
            self.keystone_srfs.append(local_new_srf)

keystone = Keystone(srf_set, v_div, blend_precision, dir)
keystone_srfs = keystone.construct_srf(200, True)
split_crvs = keystone.vis_blend_crv_split
uv_switched_crvs = keystone.vis_uv_switched_crvs
uv_switched_pts = keystone.vis_uv_switched_pt_set
