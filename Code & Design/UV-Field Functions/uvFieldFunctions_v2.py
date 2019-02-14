# uvFieldFunction_v2.py
# second iteration of the uv_field function
# uv_swap and u & v changes done AFTER THE FACTS
# only one def per operation
# choosing which (u or v) direction you want to manipulate

import Rhino.Geometry as rg
import math as m

# grasshopper variables

# general surface
surfaces

# uv-organisation variables

u_divisions
v_divisions

swap_uv
change_direction

# whether the edges of the new surface should match the ones from the old surface

boundary_easing

# the type of change that gets applied to the given surfac
warp_type
warp_directions

# the no-change (except for uv-manipulation)
warp_0 = [0]
# sin waves
amplitude, period, iterations, u_shift, function_type = sin_parameters
warp_1 = [1, amplitude, period, iterations, u_shift, function_type]
# reference  surface
warp_2 = [2, reference_surface]
warp_types = [warp_0, warp_1, warp_2]

class Surface(object):
    """ Surface with manipulated uv-field
    """

    def __init__(self, srf, u_div, v_div, swap_uv = False, chng_dir = 0, warp_type = [0], warp_dir = 0, bound_eaz = True):
        """ Base initialization of raw uv related parameters

            :param srf:         the original surface that will be manipulated
            :param u_div:       the amount of divisions in the u-direction (related to the original surface!)
            :param v_div:       the amount of divisions in the v-direction (related to the original surface!)
            :param swap_uv:     whether you want to transpose the surface or not (default = False)
            :param chng_dir:    depending on this value, either u (1), v (2), both (3) or none (0) will change direction (default = 0)
            :param warp_type:   list which contains a set of values which will be used to inform the uv-field manipulation functions (default = 0, none-function)
            :param warp_dir:    depending on this value, either v (0), u (1) or both u & v (2) will be warped according to the given function
            :param bound_eaz:   bool whether or not you want to make the edges of the new surface match those of the old one (default = True)
        """
        self.srf = self.surface_to_nurbs_surface(srf)
        self.swap_uv = swap_uv
        self.v_div = int(v_div)
        self.u_div = int(u_div)
        self.chng_dir = chng_dir
        self.warp_dir = warp_dir
        self.bound_eaz = boundary_easing

        # sets up the correct uv direction of the surface
        self.__uv_management()

        # initializes the warp_type to be applied
        self.__warp_type_set(warp_type)

    def surface_to_nurbs_surface(self, surface_to_check):
        """ internal method that tries to turn a surface into a nurbssurface

            :param surface_to_check:    surface to check and if fails, to transform
            :return:                    the edited or same surface depending on the case
        """
        if type(surface_to_check) == rg.Surface:
            nurbed_surface = surface_to_check.ToNurbsSurface()
            if nurbed_surface != rg.NurbsSurface:
                print "I tried to convert you but I failed :("
            return nurbed_surface
        else:
            return surface_to_check

    def __uv_management(self):
        """ rebuild the surface based uv parameters & a given resolution """
        self.__uv_swap()
        # initialize self.uv_list & self.uv_list_base
        self.__uv_regrade()
        # # rearranges the base_list if necessary
        # self.__uv_dir_management()

    def __uv_swap(self):
        """ internal method that orients the uv-directions of your surfaces """

        if (self.swap_uv):
            self.u_interval = rg.Interval(0, self.v_div)
            self.v_interval = rg.Interval(0, self.u_div)
        else:
            self.u_interval = rg.Interval(0, self.u_div)
            self.v_interval = rg.Interval(0, self.v_div)

        self.srf.SetDomain(0, self.u_interval)
        self.srf.SetDomain(1, self.v_interval)

    def __uv_dir_management(self):
        """ private method that changes the apparant direction of the control points """

        # False, False | True, False | False, True | True, True
        self.invert_u = (self.chng_dir % 2 == 1)
        self.invert_v = (self.chng_dir > 1)

        if (self.invert_u):
            temp_uv_list = []
            temp_uv_list_base = []

            for u in range(self.u_div + 1):
                temp_uv_list.append(self.uv_list[self.u_div - u])
                temp_uv_list_base.append(self.uv_list_base[self.u_div - u])

            self.uv_list = temp_uv_list
            self.uv_list_base = temp_uv_list_base

        if (self.invert_v):
            temp_uv_list = []
            temp_uv_list_base = []
            for u in range(self.u_div + 1):
                temp_v_list = []
                temp_v_list_base = []
                for v in range(self.v_div + 1):
                    temp_v_list.append(self.uv_list[u][self.v_div - v])
                    temp_v_list_base.append(self.uv_list_base[u][self.v_div - v])
                temp_uv_list.append(temp_v_list)
                temp_uv_list_base.append(temp_v_list_base)
            self.uv_list = temp_uv_list
            self.uv_list_base = temp_uv_list_base

    def __uv_regrade(self):
        """ internal method creates simple [v_list[u,v]] list """
        self.uv_list_base = []  # the one that describes the surface as it is
        self.uv_list = []       # the one that will be changed
        for u in range(self.u_div + 1):
            v_list = []
            v_list_base = []
            for v in range(self.v_div + 1):
                v_list.append([u, v])
                v_list_base.append([u, v])
            self.uv_list_base.append(v_list_base)
            self.uv_list.append(v_list)


    def __warp_type_set(self, warp_type):
        """ private method that sets the warp type, if you want to set your own later on, use the self.reset_warp_type() method """
        value_count = len(warp_type)
        self.warp_values_list = [warp_type[i] for i in range(1, value_count)]
        self.warp_type_ok = True
        self.warp_type = int(warp_type[0])

        # same as the regrading function aka the None-Function
        if self.warp_type == 0:
            self.value_type_names = ["No Modifications"]

        # sin waves
        elif self.warp_type == 1:
            # error_check
            self.value_type_names = ["Sin-Wave", "Amplitude", "Revolutions", "Iterations", "U Shift Value", "Sin-Function Type"]
            self.value_types_required = [float, float, int, float, int]
            # initialization of the values
            self.amp = self.warp_values_list[0]                     # amplitude in reference to the amount unitized v
            self.rev = self.warp_values_list[1]                     # period in relationship to the unitized u
            self.iter = int(self.warp_values_list[2])               # amount of iterations for the sin_wave sums
            self.val_shift = self.warp_values_list[3]               # amount every row shifts compared to the other
            self.sin_function_type = int(self.warp_values_list[4])  # which function to use
            self.warp_values_list = [self.amp, self.rev, self.iter, self.val_shift, self.sin_function_type]
            self.__error_message_warp_text_generator()
            if (self.warp_type_ok):
                self.per = m.pi * 2.0 * self.rev
                self.multipliers = [self.iter ** (i - 2) for i in range(self.iter)]
                print self.multipliers

        # other rectangular surface
        elif self.warp_type == 2:
            self.value_type_names = ["Reference Surface", "Surface"]
            self.value_types_required = [rg.NurbsSurface]
            # initialization of the values
            self.reference_surface = self.warp_values_list[0]
            # quick check whether the surface is a nurbs surface or not, if not tries and sets it to one
            self.reference_surface = self.surface_to_nurbs_surface(self.reference_surface)
            self.__error_message_warp_text_generator()

        # runs the warp_type or prints error_text in case the initialization failed
        if (self.warp_type_ok):
            self.__warp_management()
        else:
            print self.warp_error_text

    def __warp_functions(self):
        """ private method in which the operations are called upon """
        if self.warp_type == 0:
            pass
        elif self.warp_type == 1:
            self.__warp_sin_function()
        elif self.warp_type == 2:
            self.__warp_reference_surface()

    def __warp_management(self):
        """ private method that links most of the code together """
        self.__warp_functions()
        self.__boundary_easing()
        self.__generate_new_surface()

    def reset_warp_type(self, new_warp_type = 0, u_div = None, v_div = None):
        """ Method that allows you to rerun the script on the same surface but with a different warp type

            :param new_warp_type:   the values that will be used for the second manipulation of the surface
            :param u_div:           new u division count
            :param v_div:           new v division count
            :return:                outputs that new surface or an error message
        """

        self.__set_warp_type(new_warp_type)

        # initialization of most of the script, will only run if the warp variables are set correctly
        if (self.warp_type_ok):
            self.__uv_management()
            return self.new_surface
        else:
            print self.warp_error_text

    def __error_message_if_vowel(self, char):
        """ private function that checks the whether the first letter in the next list in a vowel to know whether it has to add an -n to the article """
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

    def __error_message_warp_text_generator(self):
        """ private error message generation method """
        listed_numbers = ["first ", "second", "third", "fourth", "fifth", "sixth"]
        warp_text_list = ["For the ", self.value_type_names[0], " function your "]
        for i, type_variable in enumerate(self.value_types_required):
            if not(type_variable == type(self.warp_values_list[i])):
                warp_text_list.append(listed_numbers[i + 1])
                warp_text_list.append(" value, the ")
                warp_text_list.append(self.value_type_names[i + 1])
                warp_text_list.append(" value, should be a")
                warp_text_list.append(self.__error_message_if_vowel((str(type_variable))[7]))
                warp_text_list.append(str(type_variable)[7: -2])
                warp_text_list.append(" and not a")
                warp_text_list.append(self.__error_message_if_vowel(str(type(self.warp_values_list[i]))[7]))
                warp_text_list.append(str(type(self.warp_values_list[i]))[7: -2])
                warp_text_list.append(", ")
                self.warp_type_ok = False
        self.warp_error_text = ''.join(warp_text_list)[0: -1]

    def __boundary_easing(self):
        """ private method that coerces the boundaries of the new surface to match those of the old one """
        if (self.bound_eaz):
            temp_uv_list = []
            for u in range(self.u_div + 1):
                temp_v_list = []
                for v in range(self.v_div + 1):
                    u0, v0 = self.uv_list_base[u][v][0] * 1.0, self.uv_list_base[u][v][1] * 1.0
                    u1, v1 = self.uv_list[u][v][0] * 1.0, self.uv_list[u][v][1] * 1.0
                    # print (u0, v0, " - (de)constructive easing - "),
                    # correcting the edge issues
                    # weighing of differnt values defined by circle mapping
                    u0_new = ((u0 / self.u_div) * 2.0 - 1)
                    u_easing = m.sqrt(1 - (u0_new) ** 2)
                    v0_new = ((v0 / self.v_div) * 2.0 - 1)
                    # print ("u0: ", u0, ", u1: ", u1, " v0: ", v0, " v1: ", v1)
                    # print (u0_new ** 2, v0_new **2)
                    v_easing = m.sqrt(1 - (v0_new) ** 2)
                    constructive_easing = u_easing * v_easing
                    deconstructive_easing = 1 - constructive_easing

                    # print (constructive_easing, deconstructive_easing)

                    u_apparant = u0 * deconstructive_easing + u1 * constructive_easing
                    v_apparant = v0 * deconstructive_easing + v1 * constructive_easing

                    # print u_apparant, v_apparant

                    temp_v_list.append([u_apparant, v_apparant])
                temp_uv_list.append(temp_v_list)
            self.uv_list = temp_uv_list
        else:
            "I won't be easied into anything I don't want to be!"

    def __warp_sin_general_function(self, value):
        """ internal method for sine wave progagation
            should only be used in combination with __warp_sin_function
            or you have to initialize self.iter in another way

            :return:    sin value
        """
        if (self.sin_function_type == 0):
            local_value = 0
            for i in range(self.iter):
                local_value += m.sin(value / self.iter ** i)
            local_value /= self.iter

        elif (self.sin_function_type == 1):
            local_value = 0
            for multiplier in self.multipliers:
                local_value += m.sin(value * multiplier)
            local_value /= self.iter

        return local_value

    def __warp_sin_function(self):
        """ internal method for the sin field-warp """
        if ((self.warp_dir == 0) or (self.warp_dir == 2)):
            # means v is going to be manipulated
            value_shift = 0
            for u in range(self.u_div + 1):
                value_u = value_shift + u
                for v in range(self.v_div + 1):
                    value = (v + value_u) / self.per
                    v_app = v + self.__warp_sin_general_function(value) * self.amp
                    self.uv_list[u][v][1] = v_app
                value_shift += self.val_shift
        if ((self.warp_dir == 1) or (self.warp_dir == 2)):
            # means u is going to be manipulated
            value_shift = 0
            for v in range(self.v_div + 1):
                value_v = value_shift + v
                for u in range(self.u_div + 1):
                    value = (u + value_v) / self.per
                    u_app = u + self.__warp_sin_general_function(value) * self.amp
                    self.uv_list[u][v][0] = u_app
                value_shift += self.val_shift

    def __warp_reference_surface(self):
        """ internal method for the warping based on a reference surface """
        self.reference_surface.SetDomain(0, rg.Interval(0, self.u_div))
        self.reference_surface.SetDomain(1, rg.Interval(0, self.v_div))

        pt_0 = self.reference_surface.PointAt(0, 0)
        pt_1 = self.reference_surface.PointAt(self.u_div, 0)
        pt_2 = self.reference_surface.PointAt(0, self.v_div)
        pt_3 = self.reference_surface.PointAt(self.u_div, self.v_div)

        line_a = rg.Line(pt_0, pt_1)
        line_b = rg.Line(pt_2, pt_3)

        length_a, length_b = line_a.Length, line_b.Length
        u_spacing, v_spacing = length_a / self.u_div, length_b / self.v_div

        line_list = [line_a.ToNurbsCurve(), line_b.ToNurbsCurve()]
        loft_type = rg.LoftType.Tight
        base_surface = rg.Brep.CreateFromLoftRebuild(line_list, rg.Point3d.Unset, rg.Point3d.Unset, loft_type, False, 50)[0]
        print base_surface.ToNurbsSurface()

        print base_surface

        self.uv_list = []

        for u in range(self.u_div + 1):
            v_list = []
            for v in range(self.v_div + 1):
                actual_pt = rg.Point3d(self.srf.PointAt(u, v))
                base_pt = rg.Point3d(base_surface.PointAt(u, v))
                relative_pt = actual_pt - base_pt
                uv_val = [u + relative_pt.X / u_spacing, v + relative_pt.Y / v_spacing]
                v_list.append(uv_val)
            self.uv_list.append(v_list)

    def __show_points(self):
        pts = []

        self.__uv_dir_management()

        if (self.swap_uv):
            uv_0 = 1
            uv_1 = 0
        else:
            uv_0 = 0
            uv_1 = 1

        for v_list in self.uv_list:
            pts_v = []
            for uv in v_list:
                local_pt = rg.Point3d(self.srf.PointAt(uv[uv_0], uv[uv_1]))
                pts_v.append(local_pt)
            pts.append(pts_v)
        return pts

    def show_points(self):
        pts = []
        for v_point_list in self.__show_points():
            for point in v_point_list:
                pts.append(point)
        return pts

    def show_isocurves(self):
        points = self.__show_points()

        curve_list_u = []
        curve_list_v = []
        for i in range(len(points[0])):
            u_curve_points = [point_list[i] for point_list in points]
            curve_list_u.append(rg.NurbsCurve.Create(False, 3, u_curve_points))
        for v_point_list in points:
            curve_list_v.append(rg.NurbsCurve.Create(False, 3, v_point_list))
        return curve_list_u, curve_list_v

    def __generate_new_surface(self):
        curve_list_u, curve_list_v = self.show_isocurves()
        loft_type = rg.LoftType.Tight
        new_srf = rg.Brep.CreateFromLoftRebuild(curve_list_v, rg.Point3d.Unset, rg.Point3d.Unset, loft_type, False, 50)
        self.new_srf = new_srf[0]

warp_type_parameters = warp_types[warp_type]

# srf, u_div, v_div, swap_uv = False, chng_dir = 0, warp_type = [0], warp_dir = 0, bound_eaz = True

classed_surface = Surface(surfaces, u_divisions, v_divisions, swap_uv, change_direction, warp_type_parameters, warp_directions, boundary_easing)
isocurves_u, isocurves_v = classed_surface.show_isocurves()
surface = classed_surface.new_srf
# pts = classed_surface.show_points()
