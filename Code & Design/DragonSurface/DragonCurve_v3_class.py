# dragon curve retake_easy

import Rhino.Geometry as rg
import math as m

# grasshopper inputs

global curves
global divisions
global complex_divide
global curvature_factor

curve_count = len(curves)

curve_count -= 2
curve_count = (curve_count - curve_count % 4)  + 2

curves = [curves[i] for i in range(curve_count)]

# global variables

global v_scale
v_scale = 10000.0

# function to regrade curves based on curvature

class DragonCurve (object):

    def __init__ (self, curve, divisions, complex_divide = False, curvature_factor = 1000, list_value = 0, profile_height = 40, profile_width = 100, extension_end = 120):



        self.crv = curve
        self.div_count = divisions
        self.is_complex = complex_divide
        self.curvature_f = curvature_factor
        self.list_number = list_value

        self.w = profile_width
        self.h = profile_height
        self.l_ex = extension_end

        self.w_interval = rg.Interval(- self.w * .5, self.w * .5)
        self.h_interval = rg.Interval(- self.h * .5, self.h * .5)

        self.curve_domain()

        if (self.is_complex):
            # self.text_string = " this curve is divided using the regrading algorithm"
            self.complex_divide()
        else:
            # self.text_string = " this curve is simply divided"
            self.simple_divide()

        self.curvature_in_point()

        self.beam_generator()
        self.box_generator()

    def curve_domain(self):

        self.t_start, self.t_end = self.crv.Domain[0], self.crv.Domain[1]
        self.t_length = self.t_end - self.t_start

    def two_pts_relations(self, pt_0, pt_1):

        # distance calculation
        x0, y0, z0 = pt_0.X, pt_0.Y, pt_0.Z
        x1, y1, z1 = pt_1.X, pt_1.Y, pt_1.Z
        xD, yD, zD = (x1 - x0)**2, (y1 - y0)**2, (z1 - z0)**2
        distance = (xD + yD + zD) ** .5

        # mid_point
        x2, y2, z2 = (x0 + x1) * .5, (y0 + y1) * .5, (z0 + z1) * .5
        mid_point = rg.Point3d(x2, y2, z2)

        return distance, mid_point

    def complex_divide(self):
        # function that divides the curve but first regrades it base on curvature

        range_value = self.t_length / (self.div_count)
        domain_list = []
        temp_vector_length_list = []
        for i in range (self.div_count + 1):
            local_t = self.t_start + i * range_value
            domain_list.append(local_t)
            local_curvature_vec = rg.Vector3d(self.crv.CurvatureAt(local_t))
            vector_length = local_curvature_vec.Length
            temp_vector_length_list.append(vector_length)

        temp_vector_length_partial_sums = []
        temp_point_list = []
        count = 0
        previous_value = 0
        for local_vec_l in (temp_vector_length_list):
            x_value = domain_list[count]
            y_value = previous_value * self.curvature_f
            local_pt = rg.Point3d(x_value, y_value, 0)
            temp_point_list.append(local_pt)
            temp_vector_length_partial_sums.append(previous_value)
            previous_value += local_vec_l
            count += 1

        curvature_crv = rg.Curve.CreateControlPointCurve(temp_point_list, 10)
        temp_points_curvature_crv = curvature_crv.DivideByCount(self.div_count, True)
        t_vals = [curvature_crv.PointAt(pt).X for pt in temp_points_curvature_crv]
        self.curvature_vecs = [self.crv.CurvatureAt(t_value) for t_value in t_vals]
        self.curvature_pts = [(self.crv.PointAt(t_vals[i]) + self.curvature_vecs[i] * v_scale) for i in range(self.div_count + 1)]
        self.division_pts = [self.crv.PointAt(t_val) for t_val in t_vals]

    def simple_divide(self):
        # function to divide curves in a straight-forward mather

        # resetting domain
        self.crv.Domain = rg.Interval(0.0, self.div_count * 1.0)
        self.curve_domain()

        # defining
        self.curvature_vecs = []
        self.curvature_pts = []
        self.division_pts = []

        for i in range (self.div_count + 1):
            local_pt = rg.Point3d(self.crv.PointAt(i))
            self.division_pts.append(local_pt)
            vec_at_t = self.crv.CurvatureAt(i)
            v_val_pt = local_pt + rg.Point3d(vec_at_t) * v_scale
            self.curvature_vecs.append(vec_at_t)
            self.curvature_pts.append(v_val_pt)

    def transform_project_pt(self, point):
        xz_plane = rg.Plane.WorldZX
        transformed_point = rg.Point3d(point)
        transformed_point.Transform(self.projection_transform)
        projected_point = xz_plane.ClosestPoint(transformed_point)

        return projected_point

    def curvature_in_point(self):

        xz_plane = rg.Plane.WorldZX

        # defining the domain of the curve

        extra_factor = .05

        t_start_extra = self.t_length * - extra_factor + self.t_start
        t_end_extra = self.t_length * extra_factor + self.t_end

        # getting a plane at extra lengths & mid_point

        start_pt, end_pt, mid_pt = self.crv.PointAt(t_start_extra), self.crv.PointAt(t_end_extra), self.crv.PointAt(self.t_end)
        plane_origin = rg.Point3d(start_pt)
        plane_x_vector = rg.Vector3d(end_pt - start_pt)
        plane_y_vector = rg.Vector3d(mid_pt - start_pt)
        base_plane = rg.Plane(plane_origin, plane_x_vector, plane_y_vector)

        # transforming & projecting the curve & points to that plane

        self.projection_transform = rg.Transform.PlaneToPlane(base_plane, xz_plane)
        check_curve = self.crv.DuplicateCurve()
        check_curve.Transform(self.projection_transform)
        projected_curve = rg.Curve.ProjectToPlane(check_curve, xz_plane)

        curve_at_start = projected_curve.PointAtStart
        curve_at_end = projected_curve.PointAtEnd

        self.proj_pts = [self.transform_project_pt(pt) for pt in self.curvature_pts]

        # constructing a boundary curve

        transformed_start_pt = rg.Point3d(start_pt)
        transformed_end_pt = rg.Point3d(end_pt)
        transformed_start_pt.Transform(self.projection_transform)
        transformed_end_pt.Transform(self.projection_transform)

        x_increase = self.crv.GetLength() * .5
        x1, y1, z1 = transformed_start_pt.X, transformed_start_pt.Y, transformed_start_pt.Z
        x2, y2, z2 = transformed_end_pt.X, transformed_end_pt.Y, transformed_end_pt.Z
        x_val = (x1 + x2) * .5 + x_increase
        transformed_start_pt_2 = rg.Point3d(x_val, y1, z1)
        transformed_end_pt_2 = rg.Point3d(x_val, y2, z2)

        bound_pts = [curve_at_start, transformed_start_pt, transformed_start_pt_2, transformed_end_pt_2, transformed_end_pt, curve_at_end]

        bounding_curve = rg.PolylineCurve(bound_pts)
        bound_curve = rg.Curve.JoinCurves([projected_curve, bounding_curve])[0]

        projected_curve = bound_curve

        # doing the containment operations

        inside = rg.PointContainment.Inside
        coincident = rg.PointContainment.Coincident
        outside = rg.PointContainment.Outside

        self.division_pts_containment_vals = []

        for pt in self.proj_pts:
            local_containment_val = bound_curve.Contains(pt, xz_plane)
            if (local_containment_val == inside):
                containment_val = 1
            elif (local_containment_val == outside):
                containment_val = -1
            elif (local_containment_val == coincident):
                containment_val = 0

            self.division_pts_containment_vals.append(containment_val)

        self.bound_crv = bound_curve
        self.projected_crv = projected_curve

    def beam_generator(self):
        if ((self.list_number % 4) == 0):
            first_value = 0
            self.special_case = False
        elif ((self.list_number % 4) == 1):
            first_value = 2
            self.special_case = False
        elif ((self.list_number % 4) == 2):
            first_value = 1
            self.special_case = True
        else:
            first_value = 3
            self.special_case = True

        if not(self.special_case):
            self.beam_frames = []
            self.lengths = []
            self.line_representation = []
            max_value = divisions - first_value - 1
            for i in range(first_value, max_value, 4):
                self.line_representation.append(rg.LineCurve(self.division_pts[i], self.division_pts[i + 1]))
                length, base_point = self.two_pts_relations(self.division_pts[i], self.division_pts[i + 1])
                vector_x = rg.Vector3d(self.division_pts[i + 1] - self.division_pts[i])
                vector_a, vector_b = self.curvature_vecs[i], self.curvature_vecs[i + 1]

                vector_z = rg.Vector3d.CrossProduct(vector_a, vector_b )
                if vector_z.Y < 0:
                    vector_z *= -1
                vector_y = rg.Vector3d.CrossProduct(vector_x, vector_z)
                self.beam_frames.append(rg.Plane(base_point, vector_x, vector_y))
                self.lengths.append(length)

        elif (self.special_case):
            self.beam_frames = []
            self.lengths = []
            self.line_representation = []
            max_value = divisions - first_value - 1
            rhythm = self.division_pts_containment_vals[first_value]
            i = first_value
            while i < max_value:
                self.line_representation.append(rg.LineCurve(self.division_pts[i], self.division_pts[i + 1]))
                length, base_point = self.two_pts_relations(self.division_pts[i], self.division_pts[i + 1])
                vector_x = rg.Vector3d(self.division_pts[i + 1] - self.division_pts[i])
                vector_a, vector_b = self.curvature_vecs[i], self.curvature_vecs[i + 1]

                vector_z = rg.Vector3d.CrossProduct(vector_a, vector_b )
                if vector_z.Y < 0:
                    vector_z *= -1
                vector_y = rg.Vector3d.CrossProduct(vector_x, vector_z)
                self.beam_frames.append(rg.Plane(base_point, vector_x, vector_y))
                self.lengths.append(length)

                sub = 0
                print i,
                if (i <= max_value - 4 and i > first_value):
                    if not(rhythm == self.division_pts_containment_vals[i + 4]):
                        print "yezz",
                        sub = - 2
                        rhythm = - rhythm
                i += sub + 4
                print i

    def box_generator(self):
        self.beam_boxes = []
        for i in range (len(self.beam_frames)):
            local_frame = self.beam_frames[i]
            local_length = self.lengths[i] + self.l_ex
            l_interval = rg.Interval(- .5 * local_length, .5 * local_length)
            local_box = rg.Box(local_frame, l_interval, self.w_interval, self.h_interval)
            self.beam_boxes.append(local_box)
            self.text_string = "I have added a box!"

    def intersecter_simple(self):
        pass

    def intersecter_complex(self):
        pass

raw_bound_curves = []
raw_divisions_pts = []
raw_boxes = []
raw_curvature_points = []
DragonCurve_s = []
for i in range(curve_count):
    local_dragon_curve = DragonCurve(curves[i], divisions, complex_divide, curvature_factor, i)
    # print local_dragon_curve.text_string
    [raw_boxes.append(box) for box in local_dragon_curve.beam_boxes]
    [raw_divisions_pts.append(pts) for pts in local_dragon_curve.division_pts]
    [raw_curvature_points.append(vec_pt) for vec_pt in local_dragon_curve.proj_pts]
    raw_bound_curves.append(local_dragon_curve.bound_crv)
    DragonCurve_s.append(local_dragon_curve)
    # print local_dragon_curve.division_pts_containment_vals
