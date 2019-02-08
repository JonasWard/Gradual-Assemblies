# rhino script that remaps the uv-values according to a certain function

import Rhino.Geometry as rg
import math as m

# grasshoppers variabels

surfaces

if isinstance(surfaces, rg.Surface):
    print "I tried!"

# uv organisation

u_divisions
v_divisions

swap_uv
change_direction

edge_flattening


# initialization of the warp types
warp_type

warp_0 = [0]
# sin waves
amplitude, period, iterations, u_shift = sin_parameters
warp_1 = [1, amplitude, period, iterations, u_shift]
# reference  surface
warp_2 = [2, reference_surface]
warp_types = [warp_0, warp_1, warp_2]

class Surface(object):

    def __init__(self, srf, u_div, v_div, swap_uv = False, chng_dir = 0):
        self.srf = srf
        self.swap_uv = swap_uv

        self.v_div = int(v_div)
        self.u_div = int(u_div)

        self.chng_dir = chng_dir

    def set_warp_type(self, warp_type):
        value_count = len(warp_type)
        self.warp_values_list = [warp_type[i] for i in range(1, value_count)]
        self.warp_type_ok = True
        self.warp_type = int(warp_type[0])

        if self.warp_type == 0:
            self.value_type_names = ["No Modifications"]
            # same as the regrading function
        elif self.warp_type == 1:
            # sin waves
            # error_check
            self.value_type_names = ["Sin-Wave", "Amplitude", "Period", "Iterations", "U Shift Value"]
            self.value_types_required = [float, float, int, float]
            # initialization of the values
            self.amp = self.warp_values_list[0]             # amplitude in reference to the amount unitized v
            self.per = self.warp_values_list[1]             # period in relationship to the unitized u
            self.iter = int(self.warp_values_list[2])       # amount of iterations for the sin_wave sums
            self.val_shift = self.warp_values_list[3]       # amount every row shifts compared to the other
            self.warp_values_list = [self.amp, self.per, self.iter, self.val_shift]
            self.warp_error_text_generator()
        elif self.warp_type == 2:
            # surfaces
            self.value_type_names = ["Reference Surface", "Surface"]
            self.value_types_required = [rg.NurbsSurface]
            # initialization of the values
            self.reference_surface = self.warp_values_list[0]
            self.surface_to_nurbs_surface()
            self.warp_error_text_generator()

        # initiazes most of the script

        if (self.warp_type_ok):
            self.dir_management()
            self.uv_function_regrade()
            self.uv_functions()
            self.boundary_easing()
            self.new_surface = self.new_surface()
        else:
            print self.warp_error_text

    def if_vowel(self, char):
        vowel_list = ["a", "e", "o", "u", "i"]

        vowel_value = False
        for vowel in vowel_list:
            if (char == vowel):
                vowel_value = True
                break
        if (vowel_value):
            return "n "
        else:
            return " "

    def surface_to_nurbs_surface(self):
        if type(self.reference_surface) == rg.Surface:
            self.reference_surface = self.reference_surface.ToNurbsSurface()

    def warp_error_text_generator(self):
        # error correction sentence
        listed_numbers = ["first ", "second", "third", "fourth", "fifth", "sixth"]
        warp_text_list = ["For the ", self.value_type_names[0], " function your "]
        for i, type_variable in enumerate(self.value_types_required):
            if not(type_variable == type(self.warp_values_list[i])):
                warp_text_list.append(listed_numbers[i + 1])
                warp_text_list.append(" value, the ")
                warp_text_list.append(self.value_type_names[i + 1])
                warp_text_list.append(" value, should be a")
                warp_text_list.append(self.if_vowel((str(type_variable))[7]))
                warp_text_list.append(str(type_variable)[7: -2])
                warp_text_list.append(" and not a")
                warp_text_list.append(self.if_vowel(str(type(self.warp_values_list[i]))[7]))
                warp_text_list.append(str(type(self.warp_values_list[i]))[7: -2])
                warp_text_list.append(", ")
                self.warp_type_ok = False
        self.warp_error_text = ''.join(warp_text_list)[0: -1]

    def dir_management(self):
        # def that changes the apparant direction of the control points

        # change certain directions if need be
        if (self.chng_dir == 0):
            # no change
            self.swap_u = False
            self.swap_v = False
        elif (self.chng_dir == 1):
            # invert u direction
            self.swap_u = True
            self.swap_v = False
        elif (self.chng_dir == 2):
            # invert u direction
            self.swap_u = False
            self.swap_v = True
        elif (self.chng_dir == 3):
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
                # correcting the edge issues
                # weighing of differnt values defined by circle mapping
                u0_new = (u0 / self.u_div * 2 - 1)
                u_easing = m.sqrt(1 - (u0_new) ** 2)
                v0_new = (v0 / self.v_div * 2 - 1)
                v_easing = m.sqrt(1 - (v0_new) ** 2)

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

    def reference_surface_mapping(self):
        u_len = self.reference_surface.IsoCurve(0, 0).GetLength()
        v_len = self.reference_surface.IsoCurve(1, 0).GetLength()

        b_pt = self.reference_surface.IsoCurve(0, 0).PointAt(0)
        # u_base, v_base = b_pt.X, b_pt.Y

        translation = rg.Transform.Translation(rg.Vector3d(- b_pt))
        self.reference_surface.Transform(translation)

        print u_len, v_len

        u_space = u_len / self.u_div
        v_space = v_len / self.v_div

        print u_space, v_space

        self.uv_list = []
        if not(self.swap_uv):
            self.u_interval = rg.Interval(0, self.u_div)
            self.v_interval = rg.Interval(0, self.v_div)

            self.reference_surface.SetDomain(0, self.u_interval)
            self.reference_surface.SetDomain(1, self.v_interval)

            for u in range(self.u_div + 1):
                u0 = u_space * u
                v_list = []
                for v in range(self.v_div + 1):
                    v0 = v_space * v
                    pt = self.reference_surface.PointAt(u, v)
                    u1, v1 = abs(pt.X), abs(pt.Y)
                    u_shift, v_shift = (u1 - u0) / u_space, (v1 - v0) / v_space
                    u_app, v_app = u_shift + u, v_shift + v
                    v_list.append([u_app, v_app])
                self.uv_list.append(v_list)
        else:

            self.v_interval = rg.Interval(0, self.u_div)
            self.u_interval = rg.Interval(0, self.v_div)

            self.reference_surface.SetDomain(0, self.u_interval)
            self.reference_surface.SetDomain(1, self.v_interval)

            for v in range(self.v_div + 1):
                v0 = u_space * v
                u_list = []
                for u in range(self.u_div + 1):
                    u0 = v_space * u
                    pt = self.reference_surface.PointAt(v, u)
                    u1, v1 = abs(pt.X), abs(pt.Y)
                    u_shift, v_shift = (u1 - u0) / v_space, (v1 - v0) / u_space
                    u_app, v_app = u_shift + u, v_shift + v
                    u_list.append([u_app, v_app])
                self.uv_list.append(u_list)
        print self.uv_list 

    def sin_functions(self, value):
        # this function outputs a value that goes through the loop n amount of times
        local_value = 0
        for i in range(self.iter):
            local_value += m.sin(value / self.iter ** i)

        local_value /= self.iter
        return local_value

    def uv_functions(self):
        # the actual uv_shifting
        tau = m.pi * 2

        if (self.warp_type == 0):
            # nothing at all to see here !
            self.uv_list = self.uv_function_regrade()
        elif (self.warp_type == 1):
            # the sin-wave warp warp
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
                        v_app += self.sin_functions(value) * self.amp
                        v_list.append([u_app, v_app])
                    self.uv_list.append(v_list)
                    value_shift += self.val_shift
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
                        u_app += self.sin_functions(value) * self.amp
                        u_list.append([u_app, v_app])
                    self.uv_list.append(u_list)
                    value_shift += self.val_shift
        elif (self.warp_type == 2):
            self.reference_surface_mapping()

# executrion of the script
warp_type_parameters = warp_types[warp_type]

classed_surface = Surface(surfaces, u_divisions, v_divisions, swap_uv, change_direction)

classed_surface.set_warp_type(warp_type_parameters)
point_lists = classed_surface.show_points()
isocurves_u, isocurves_v = classed_surface.show_isocurves()

point_list = []
for point_ls in point_lists:
    for point in point_ls:
        point_list.append(point)

surface = classed_surface.new_surface
# print surface

# setting out the grid of point values

# regrading the warping of the surface based on proximity to the edges
