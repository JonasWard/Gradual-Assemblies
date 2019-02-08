# rhino script that remaps the uv-values according to a certain function

import Rhino.Geometry as rg
import math as m

# grasshoppers variabels

surfaces

print type(surfaces)
print surfaces

if isinstance(surfaces, rg.Surface):
    print "I tried!"


u_divisions
v_divisions

warp_type

swap_uv
change_direction

edge_flattening


class Surface(object):

    def __init__(self, srf, u_div, v_div, warp_type = 0, swap_uv = False, chng_dir = 0):
        self.srf = srf
        self.swap_uv = swap_uv

        self.v_div = int(v_div)
        self.u_div = int(u_div)

        self.warp_type = self.warp_types(warp_type)

        self.dir_management(chng_dir)
        print "ok"
        self.uv_function_regrade()
        print "ok"
        self.uv_functions()
        print "ok"
        self.boundary_easing()
        print "ok"
        self.new_surface = self.new_surface()
        print "ok"

    def warp_types(self, value):
        if value == 0:
            # same as the regrading function
            return [[0]]
        elif value == 1:
            # sin waves
            amplitude = 7.0  # amplitude in reference to the amount unitized v
            period = 50.0   # period in relationship to the unitized u
            iterations = 10
            u_shift = 4.0   # amount every row shifts compared to the other
            return [[1], [amplitude, period, iterations, u_shift]]

    def dir_management(self, change_direction = 0):
        # def that changes the apparant direction of the control points

        # change certain directions if need be
        if (change_direction == 0):
            # no change
            self.swap_u = False
            self.swap_v = False
        elif (change_direction == 1):
            # invert u direction
            self.swap_u = True
            self.swap_v = False
        elif (change_direction == 2):
            # invert u direction
            self.swap_u = False
            self.swap_v = True
        elif (change_direction == 3):
            # invert u & v direction
            self.swap_u = True
            self.swap_v = True

        self.u_interval = rg.Interval(0, self.u_div)
        self.v_interval = rg.Interval(0, self.v_div)

        self.srf.SetDomain(0, self.u_interval)
        self.srf.SetDomain(1, self.v_interval)

    def boundary_easing(self):
        # boundary easing
        for i, u_or_v_list in enumerate(self.uv_list):
            for j, uv_vals in enumerate(u_or_v_list):
                u0, v0 = self.uv_list_base[i][j][0], self.uv_list_base[i][j][1]
                u1, v1 = uv_vals[0], uv_vals[1]
                # shifting value to match atan function normalised for max_value atan being 4
                u_easing = m.atan(abs((u0 - self.u_div) * 2 / self.u_div) * 4) / 1.32581766
                print u_easing
                v_easing = m.atan(abs((v0 - self.v_div) * 2 / self.v_div) * 4) / 1.32581766
                print v_easing

                u_apparant = u0 * (1 - u_easing) + u1 * u_easing
                v_apparant = v0 * (1 - v_easing) + v1 * v_easing

                self.uv_list[i][j] = [u_apparant, v_apparant]

    def show_points(self):
        pts = []
        for v_list in self.uv_list:
            pts_v = []
            for uv in v_list:
                local_pt = rg.Point3d(self.srf.PointAt(uv[0], uv[1]))
                pts_v.append(local_pt)
            pts.append(pts_v)

        return pts

    def show_isocurves(self):
        points = self.show_points()

        curve_list_u = []
        curve_list_v = []
        for i in range(len(points[0])):
            u_curve_points = [point_list[i] for point_list in points]
            curve_list_u.append(rg.NurbsCurve.Create(False, 3, u_curve_points))
        for v_point_list in points:
            curve_list_v.append(rg.NurbsCurve.Create(False, 3, v_point_list))
        return curve_list_u, curve_list_v

    def new_surface(self):
        curve_list_u, curve_list_v = self.show_isocurves()
        loft_type = rg.LoftType.Tight
        new_srf = rg.Brep.CreateFromLoftRebuild(curve_list_v, rg.Point3d.Unset, rg.Point3d.Unset, loft_type, False, 50)

        return new_srf[0]

    def uv_function_regrade(self):
        self.uv_list_base = []
        if not(self.swap_uv):
            for u in range(self.u_div + 1):
                if self.swap_u:
                    u_app = self.u_div - u
                else:
                    u_app = u
                v_list = []
                for v in range(self.v_div + 1):
                    if self.swap_v:
                        v_app = self.v_div - v
                    else:
                        v_app = v
                    v_list.append([u_app, v_app])
                self.uv_list_base.append(v_list)
        else:
            for v in range(self.v_div + 1):
                if self.swap_v:
                    v_app = self.v_div - v
                else:
                    v_app = v
                u_list = []
                for u in range(self.u_div + 1):
                    if self.swap_u:
                        u_app = self.u_div - u
                    else:
                        u_app = u
                    u_list.append([u_app, v_app])
                self.uv_list_base.append(u_list)

        return self.uv_list_base

    def sin_functions(self, iterations, value):
        # this function outputs a value that goes through the loop n amount of times
        local_value = 0
        for i in range(iterations):
            local_value += m.sin(value / iterations ** i)

        local_value /= iterations
        return local_value

    def uv_functions(self):
        # the actual uv_shifting
        tau = m.pi * 2

        if (self.warp_type[0][0] == 0):
            # nothing at all to see here !
            self.uv_list = self.uv_function_regrade()
        elif (self.warp_type[0][0] == 1):
            # the sin-wave warp warp
            amplitude = self.warp_type[1][0]
            period = self.warp_type[1][1]
            iteration_count = self.warp_type[1][2]
            value_shifter = self.warp_type[1][3]

            self.uv_list = []
            if not(self.swap_uv):
                value_shift = 0
                for u in range(self.u_div + 1):
                    if self.swap_u:
                        u_app = self.u_div - u
                    else:
                        u_app = u
                    v_list = []
                    for v in range(self.v_div + 1):
                        if self.swap_v:
                            v_app = self.v_div - v
                        else:
                            v_app = v
                        value = (v_app + value_shift + u_app) / period * tau
                        v_app += self.sin_functions(iteration_count, value) * amplitude
                        v_list.append([u_app, v_app])
                    self.uv_list.append(v_list)
                    value_shift += value_shifter
            else:
                value_shift = 0
                for v in range(self.v_div + 1):
                    if self.swap_v:
                        v_app = self.v_div - v
                    else:
                        v_app = v
                    u_list = []
                    for u in range(self.u_div + 1):
                        if self.swap_u:
                            u_app = self.u_div - u
                        else:
                            u_app = u
                        value = (u_app + value_shift + u_app) / period * tau
                        u_app += self.sin_functions(iteration_count, value) * amplitude
                        u_list.append([u_app, v_app])
                    self.uv_list.append(u_list)
                    value_shift += value_shifter

classed_surface = Surface(surfaces, u_divisions, v_divisions, warp_type, swap_uv, change_direction)
point_lists = classed_surface.show_points()
isocurves_u, isocurves_v = classed_surface.show_isocurves()

point_list = []
for point_ls in point_lists:
    for point in point_ls:
        point_list.append(point)

print classed_surface.uv_list
print classed_surface.uv_list_base

surface = classed_surface.new_surface
# print surface

# setting out the grid of point values

# regrading the warping of the surface based on proximity to the edges
