# simple surface divisions

import sys

# import the beam_class
path_to_append = ''.join([double_parent, "/UR_Control"])
sys.path.append(path_to_append)

print path_to_append

import geometry.beam as beam

# new hole class
path_to_append = single_parent

print path_to_append
sys.path.append(path_to_append)

print path_to_append

import Joints.hole_class as hc

import Rhino.Geometry as rg

# surface class based on surface_sets

class SurfaceSet(object):
    def __init__(self, o_srf_list = None, v_or_u_continious = 0, loop = False):
        """ initialization

        :param srf_class_list:      Empty, Organised Surface or Inemurable list Org. Srfs. Which Define it's geometry
        :param v_or_u_continious:   Whether the surface set is continious in the v or u direction
        :parap loop:                Whether the SurfaceSet runs into itself at the end locations
        """

        self.srf_list = []
        self.__surface_add_check(o_srf_list)

    def AddSurface(self, o_srf, v_or_u_continious = 0, loop = False):
        self.__surface_add_check(o_srf)

    def __surface_add_check(self, srf_set):
        if (srf_set == None):
            self.empty_srf = True
            self.srf_list = []
        elif (type(srf_set) == OrganisedSurface()):
            self.empty_srf = False
            self.srf_list = [srf_set]
        elif (type(srf_set[0]) == OrganisedSurface()):
            self.empty_srf = False
            self.srf_list = srf_set
        else:
            self.error = True
            self.error_text = "Invalid Surface Input"

        self.__error_display()

    def __error_display(self):
        if(self.error):
            print self.error_text

    def Generate_BeamNetwork(self):
        """ generating the beam relations """
        pass

    def __surface_loop_check(self):
        """ internal method to fix uneven amount of divisions in the loop direction """
        pass

    def Split(self):
        """ method that split the surface set in the middle to allow for uv-continuity """
        pass

class OrganisedSurface(object):
    def __init__(self, srf, v_div, u_div, start_val = 0, create_set = False):
        """ initialization

        :param srf:         The surface geometry to consider
        :param u_div:       The amount of u_divisions the surface has to consider or another surface
        :param v_div:       The amount of v_divisions the surface has to consider or another surface
        :parap start_val:   Defines the starting condition of the surface (0 or 1 - default = 0)
        :param create_set:  Whether to create or not create or add set depending on in the case u_div or v_div was a surface (default False)
        """
        self.__srf_check(srf)
        self.start_val_set = False
        self.div_vals = [0, 0]
        self.__division_check(v_div, 0)
        self.__division_check(u_div, 0)
        if not(self.start_val_set):
            self.start_val = start_val


    def __srf_check(self, srf):
        if (type(srf) == rg.NurbsSurface()):
            self.srf = srf
        elif (type(srf) == rg.Surface()):
            self.srf = srf.ToNurbsSurface()
        else:
            self.error = True
            self.error_text = "Invalid Surface Input"

        self.__error_display()

    def __division_check(self, div_val, dir):
        if((type(div_val) == OrganisedSurface()) and self.start_val_set):
            self.error = True
            self.error_text = "For now, this shouldn't happen (: )"
        elif((type(div_val) == OrganisedSurface()) and not(self.start_val_set)):
            self.div_vals[dir] = div_val.div_vals[dir]
            self.start_val = (div_val.start_val + div_val.div_vals[dir]) % 2
            self.start_val_set = True
        elif((type(div_val) == int) or (type(div_val) == int)):
            self.div_vals[dir] = div_val
        else:
            self.error = True
            self.error_text = ''.join(["Invalid Direction Input for direction ", dir])

        self.__error_display()

    def __create_set(self):
        pass

    def __error_display(self):
        if(self.error):
            print self.error_text
