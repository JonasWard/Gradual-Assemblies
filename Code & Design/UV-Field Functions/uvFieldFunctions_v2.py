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

edge_flattening

# the type of change that gets applied to the given surfac
warp_type

# the no-change (except for uv-manipulation)
warp_0 = [0]
# sin waves
amplitude, period, iterations, u_shift = sin_parameters
warp_1 = [1, amplitude, period, iterations, u_shift]
# reference  surface
warp_2 = [2, reference_surface]
warp_types = [warp_0, warp_1, warp_2]

class Surface(object):
    """ Surface with manipulated uv-field
    """

    def __init__(self, srf, u_div, v_div, swap_uv = False, chng_dir = 0, warp_type = [0], bound_eaz = True):
        """ Base initialization of raw uv related parameters

            :param srf:         the original surface that will be manipulated
            :param u_div:       the amount of divisions in the u-direction (related to the original surface!)
            :param v_div:       the amount of divisions in the v-direction (related to the original surface!)
            :param swap_uv:     whether you want to transpose the surface or not (default = False)
            :param chng_dir:    depending on the value, either u (1), v (2), both (3) or none (0) will change direction (default = 0)
            :param warp_type:   list which contains a set of values which will be used to inform the uv-field manipulation functions (default = 0, none-function)
            :param bound_eaz:   bool whether or not you want to make the edges of the new surface match those of the old one (default = True)
        """
        self.srf = srf
        self.swap_uv = swap_uv
        self.v_div = int(v_div)
        self.u_div = int(u_div)
        self.chng_dir = chng_dir
        self.bound_eaz = boundary_easing

        self.__set_warp_type(warp_type)

        # initialization of most of the script, will only run if the warp variables are set correctly
        if (self.warp_type_ok):
            self.__uv_management()
        else:
            print self.warp_error_text

    def __set_warp_type(self, warp_type):
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
            self.value_type_names = ["Sin-Wave", "Amplitude", "Period", "Iterations", "U Shift Value"]
            self.value_types_required = [float, float, int, float]
            # initialization of the values
            self.amp = self.warp_values_list[0]             # amplitude in reference to the amount unitized v
            self.per = self.warp_values_list[1]             # period in relationship to the unitized u
            self.iter = int(self.warp_values_list[2])       # amount of iterations for the sin_wave sums
            self.val_shift = self.warp_values_list[3]       # amount every row shifts compared to the other
            self.warp_values_list = [self.amp, self.per, self.iter, self.val_shift]
            self.__error_message_warp_text_generator()

        # other rectangular surface
        elif self.warp_type == 2:
            self.value_type_names = ["Reference Surface", "Surface"]
            self.value_types_required = [rg.NurbsSurface]
            # initialization of the values
            self.reference_surface = self.warp_values_list[0]
            # quick check whether the surface is a nurbs surface or not, if not tries and sets it to one
            self.__surface_to_nurbs_surface()
            self.__error_message_warp_text_generator()

    def __uv_management(self):
        """ private method that links most of the code together """
        self.uv_function_regrade()
        self.uv_functions()
        self.__boundary_easing()
        self.__dir_management()
        self.new_surface = self.new_surface()

    def reset_warp_type(self, new_warp_type):
        """ Method that allows you to rerun the script on the same surface but with a different warp type

            :param new_warp_type:   the values that will be used for the second manipulation of the surface
            :return:                outputs that new surface or an error message
        """

        self.__set_warp_type(new_warp_type)

        # initialization of most of the script, will only run if the warp variables are set correctly
        if (self.warp_type_ok):
            self.__uv_management()
            return self.new_surface
        else:
            print self.warp_error_text

    def __surface_to_nurbs_surface(self):
        if type(self.reference_surface) == rg.Surface:
            self.reference_surface = self.reference_surface.ToNurbsSurface()
            if self.reference_surface != rg.NurbsSurface:
                print "I tried to convert you but I failed :("

    def __error_message_if_vowel(self, char):
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
        """ private method that cources the boundaries of the new surface to match those of the old one """
        if (self.bound_eaz):
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
        else:
            "I wont be easied into anything I don't want to be!"

    def __dir_management(self):
        """ private method that changes the apparant direction of the control points """
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
