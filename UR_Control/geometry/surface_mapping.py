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

        self.srf_list = o_srf_list

    def __surface_initialization_check(self, srf_set):
        if (srf_set == None):
            



    def AddSurface(self, o_srf):


    def Split(self):
        """ method that split the surface set in the middle to allow for uv-continuity """


class OrganisedSurface(object):
    def __init__(self, srf, v_div, u_div, start_val = 0, create_set = False):
        """ initialization

        :param srf:         The surface geometry to consider
        :param u_div:       The amount of u_divisions the surface has to consider or another surface
        :param v_div:       The amount of v_divisions the surface has to consider or another surface
        :parap start_val:   Defines the starting condition of the surface (0 or 1 - default = 0)
        :param create_set:  Whether to create or not create or add set depending on in the case u_div or v_div was a surface (default False)
        """
