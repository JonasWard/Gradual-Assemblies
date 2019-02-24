"""Provides a scripting component.
    Inputs:
        x: The x script variable
        y: The y script variable
    Output:
        a: The a output variable"""

__author__ = "ytakzk"
__version__ = "2019.02.23"

import sys
import random
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import copy
import math

from geometry.joint_holes import JointHoles
from geometry.edge import *
from geometry.beam import Beam
from itertools import chain

import os

if os.name == 'posix':
    print "you're a Mac!"
    path_to_append = single_parent
    sys.path.append(path_to_append)

    print path_to_append

dowels = []
beams = []
tmp = []

class SharedEdge(object):

    def __init__(self, surface_1, surface_2, edge_1, edge_2):

        self.surface_1 = surface_1
        self.surface_2 = surface_2
        self.edge_1 = edge_1
        self.edge_2 = edge_2
    
    @staticmethod
    def generate(surfaces):
        
        u_shared_edges, v_shared_edges = [], []
        
        THRESHOLD = 1.0

        for i, s1 in enumerate(surfaces):
            
            for s2 in surfaces[i+1:]:

                if s1.top_pt.DistanceTo(s2.bottom_pt) < THRESHOLD:
                    
                    shared_edge = SharedEdge(s2, s1, V0, V1)
                    v_shared_edges.append(shared_edge)
                    
                elif s1.bottom_pt.DistanceTo(s2.top_pt) < THRESHOLD:
                    
                    shared_edge = SharedEdge(s1, s2, V0, V1)
                    v_shared_edges.append(shared_edge)
                    
                elif s1.right_pt.DistanceTo(s2.left_pt) < THRESHOLD:

                    shared_edge = SharedEdge(s2, s1, U0, U1)
                    u_shared_edges.append(shared_edge)
                    
                elif s1.left_pt.DistanceTo(s2.right_pt) < THRESHOLD:

                    shared_edge = SharedEdge(s1, s2, U0, U1)
                    u_shared_edges.append(shared_edge)
                    
                else:

                    continue
                    
                s1.shared_edges.append(shared_edge)
                s2.shared_edges.append(shared_edge)
        
        return list(set(u_shared_edges)), list(set(v_shared_edges))

class LocalNetwork(object):
    
    def __init__(self, surface_network, has_loop = False):
        
        self.beams = []
        self.has_loop = has_loop
        self.u_div = surface_network[0][0].u_div
        self.v_div = surface_network[0][0].v_div
        
        for v_index, v_sequence in enumerate(surface_network):
            
            beams_2d = []
            
            for u_index, surface in enumerate(v_sequence):
                
                if u_index % 2 == 0:
                    
                    beams = list(surface.beams)
                    
                else:
                    
                    beams = list(reversed(surface.beams))

                if len(beams_2d) == 0:
                    
                    beams_2d = list(beams)
                
                else:
                    
                    for src_beams, new_beams in zip(beams_2d, beams):
                        
                        src_beams.extend(new_beams)
                        
            self.beams.extend(beams_2d)

#        global tmp
#        for beams in self.beams:
#            for b in beams:
#                
#                tmp.append(b.brep_representation())
#        print self.beams

    def get_flatten_beams(self):

        return list(chain.from_iterable(self.beams))

    def add_three_beams_connection(self):

        dowels = []
        
        beams = self.beams
        
        # looping
        if self.has_loop:
            beams.append(beams[0])
        
        for i in range(len(beams) - 2):

            left_beams   = beams[i]
            middle_beams = beams[i + 1]
            right_beams  = beams[i + 2]

            if i % 2 == 0:

                for j in range(len(left_beams)):

                    if j < len(middle_beams):
                        left   = left_beams[j]
                        middle = middle_beams[j]
                        right  = right_beams[j]
                        
                        # apply a joint system
                        #
                        #   |
                        # | | |
                        # |   |
                        
                        joint_holes = JointHoles([left, middle, right], 0)
                        dowels.append(joint_holes.dowel)

                    if j > 0:

                        left   = left_beams[j]
                        middle = middle_beams[j-1]
                        right  = right_beams[j]

                        # apply a joint system
                        #
                        # |   |
                        # | | |
                        #   |
                        joint_holes = JointHoles([left, middle, right], 1)
                        dowels.append(joint_holes.dowel)

            else:

                for j in range(len(left_beams)):

                    left   = left_beams[j]
                    middle = middle_beams[j]
                    right  = right_beams[j]

                    # apply a joint system
                    #
                    # |   |
                    # | | |
                    #   |
                    joint_holes = JointHoles([left, middle, right], 1)
                    dowels.append(joint_holes.dowel)
                    
                    if j < len(middle_beams) - 1:
                        # apply a joint system
                        #
                        #   |
                        # | | |
                        # |   |

                        left   = left_beams[j]
                        middle = middle_beams[j+1]
                        right  = right_beams[j]
    
                        joint_holes = JointHoles([left, middle, right], 0)
                        dowels.append(joint_holes.dowel)
        
        return dowels
        
    def add_two_beams_connection(self):
        
        dowels = []
        
        beams = self.beams
        
        # looping
        if self.has_loop:
            
            return dowels
        
        # starting side
        
        left_beams  = beams[0]
        right_beams = beams[1]
        
        for i in range(len(right_beams)):
            
            left  = left_beams[i]
            right = right_beams[i]
        
            joint_holes = JointHoles([left, right], 1, 1)
            dowels.append(joint_holes.dowel)
            
            if len(left_beams) > i + 1:
                left  = left_beams[i+1]
                right = right_beams[i]
    
                joint_holes = JointHoles([left, right], 0, 1)
                dowels.append(joint_holes.dowel)

        # ending side
        
        right_beams = beams[-1]
        left_beams  = beams[-2]
        
        is_odd_division = bool(self.u_div % 2)
        
        for i in range(len(right_beams)):
            
            left  = left_beams[i]
            right = right_beams[i]
            
            joint_holes = JointHoles([left, right], 0 if is_odd_division else 1, 2)
            dowels.append(joint_holes.dowel)
            
            if len(left_beams) > i + 1:
                left  = left_beams[i+1]
                right = right_beams[i]
    
                joint_holes = JointHoles([left, right], 1 if is_odd_division else 0, 2)
                dowels.append(joint_holes.dowel)

        return dowels
        
        
class GlobalNetwork(object):

    def __init__(self, surfaces):
        
        self.surfaces = [Surface(s) for s in surfaces]
        
        u_shared_edges, v_shared_edges = SharedEdge.generate(self.surfaces)
        self.u_shared_edges = u_shared_edges
        self.v_shared_edges = v_shared_edges
        
        ###
        ### find sequences
        ###

        if len(self.u_shared_edges) == 0:

            u_sequence_list = []

        else:

            u_pairs = self.u_shared_edges[0]
            u_sequence_list = [[u_pairs.surface_2, u_pairs.surface_1]]
            
            u_shared_edges = list(u_shared_edges)[1:]
            
            while u_shared_edges:
                
                found_pair = False
                
                for i, shared_edge in enumerate(u_shared_edges):
                    
                    left, right = shared_edge.surface_2, shared_edge.surface_1
                    
                    for sequence in u_sequence_list:
                        
                        index = sequence.index(left) if left in sequence else -1
                        
                        if index > -1:
                            
                            if not right in sequence:
                                sequence.insert(index + 1, right)
                            found_pair = True

                        index = sequence.index(right) if right in sequence else -1
                        
                        if index > -1:
                            
                            if not left in sequence:
                                sequence.insert(index, left)
                            found_pair = True

                        if found_pair:
                            break
                        
                    if found_pair:
                        del u_shared_edges[i]
                        break
                        
                if not found_pair and u_shared_edges:
                    
                    shared_edge = u_shared_edges[0]
                    left, right = shared_edge.surface_2, shared_edge.surface_1
                    u_sequence_list.append([left, right])
                    
                    u_shared_edges = u_shared_edges[1:]


        if len(self.v_shared_edges) == 0:
            
            v_sequence_list = []

        else:
                
            v_pairs = self.v_shared_edges[0]
            v_sequence_list = [[v_pairs.surface_2, v_pairs.surface_1]]
            
            v_shared_edges = list(v_shared_edges)[1:]
            
            while v_shared_edges:
                
                found_pair = False
                
                for i, shared_edge in enumerate(v_shared_edges):
                    
                    bottom, top = shared_edge.surface_2, shared_edge.surface_1
                    
                    for sequence in v_sequence_list:
                        
                        index = sequence.index(bottom) if bottom in sequence else -1
                        
                        if index > -1:
                            
                            if not top in sequence:
                                sequence.insert(index + 1, top)
                            found_pair = True

                        index = sequence.index(top) if top in sequence else -1
                        
                        if index > -1:
                            
                            if not bottom in sequence:
                                sequence.insert(index, bottom)
                            found_pair = True

                        if found_pair:
                            break
                        
                    if found_pair:
                        del v_shared_edges[i]
                        break
                        
                if not found_pair and v_shared_edges:
                    
                    shared_edge = v_shared_edges[0]
                    bottom, top = shared_edge.surface_2, shared_edge.surface_1
                    v_sequence_list.append([bottom, top])
                    
                    v_shared_edges = v_shared_edges[1:]
        
        uv_pairs = []
        pair_index_list = []
        
        for i, v_sequence_1 in enumerate(v_sequence_list):
            
            for j, v_sequence_2 in enumerate(v_sequence_list[i+1:]):
                
                surface_1 = v_sequence_1[0]
                surface_2 = v_sequence_2[0]
                
                for shared_edge in surface_1.shared_edges:
                    
                    if shared_edge.surface_1 == surface_1 and \
                        shared_edge.surface_2 == surface_2:
                            
                            uv_pairs.append([v_sequence_2, v_sequence_1])
                            pair_index_list.extend([i, i + 1 + j])
                            
                    if shared_edge.surface_1 == surface_2 and \
                        shared_edge.surface_2 == surface_1:
                            
                            uv_pairs.append([v_sequence_1, v_sequence_2])
                            pair_index_list.extend([i, i + 1 + j])
        
        pair_index_list = list(reversed(list(set(pair_index_list))))
        
        # the surfaces which have no connection toward u-direction
        no_pairs = list(v_sequence_list)
        for pair_index in pair_index_list:
            del no_pairs[pair_index]

        surface_networks = [uv_pairs[0]] if len(uv_pairs) > 0 else []
        uv_pairs = uv_pairs[1:]
        
        while uv_pairs:
            
            for i, pair in enumerate(uv_pairs):
                
                found_pair = False
                
                for surface_network in surface_networks:
                    
                    if surface_network[-1][0] == pair[0][0]:
                        
                        surface_network.append(pair[1])
                            
                        del uv_pairs[i]
                        found_pair = True
                        break
                
                if found_pair:
                    break
            
            if not found_pair and uv_pairs:
                surface_networks.append(uv_pairs[0])
                uv_pairs = uv_pairs[1:]
        
        for no_pair in no_pairs:
            
            surface_networks.append([no_pair])
        
        # in case feeding a single surface
        if len(surface_networks) == 0:
            surface_networks.append([[self.surfaces[0]]])
        
        self.local_networks = []
        
        for surface_network in surface_networks:
            
            if len(surface_network) > 1 and surface_network[0][0] == surface_network[-1][0]:
                
                has_loop = True
                surface_network = surface_network[:-1]
            
            else:
                
                has_loop = False

            local_network = LocalNetwork(surface_network, has_loop)
            self.local_networks.append(local_network)
            
            global tmp
            tmp.extend([surface_network[0][0].surface])
            
class Surface(object):

    def __init__(self, surface):

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

        self.u_div = 5
        self.v_div = 3
        
        self.__instantiate_beams()

    def __instantiate_beams(self):

        self.beams = []

        surface = self.__offset_sides_surface(self.surface, 200)
        surface = self.__seam_regrades(surface)
        
        for u in range(self.u_div + 1):

            inner_arr = []

            for v in range(self.v_div):

                if (u % 2 == 0 and v % 2 == 1) or (u % 2 == 1 and v % 2 == 0):
                    continue

                p1 = surface.PointAt(u/self.u_div, v/self.v_div)
                p2 = surface.PointAt(u/self.u_div, (v+1)/self.v_div)

                length = p1.DistanceTo(p2)

                center = rg.Point3d((p1 + p2) / 2)

                _, uu, vv = surface.ClosestPoint(center)

                normal = surface.NormalAt(uu, vv)
                x_axis = rg.Vector3d(p1) - rg.Vector3d(p2)
                x_axis.Unitize()
                y_axis = rg.Vector3d.CrossProduct(normal, x_axis)

                plane = rg.Plane(center, x_axis, normal)

                beam = Beam(plane, length, 180, 40)

                inner_arr.append(beam)

            self.beams.append(inner_arr)

    def __offset_sides_surface(self ,surface, offset_dis=20, sides = 2, sampling_count = 25):
        """ method that returns a slightly shrunk version of the surface along the v direction
            :param offset_dis:      Offset Distance (default 20)
            :param sides:           Which sides should be offseted (0 = left, 1 = right, 2 = both, default)
            :param sampling_count:  Precision at which the surface should be rebuild
            :return temp_srf:       The trimmed surface
        """
        temp_surface = copy.deepcopy(surface)

        temp_surface.SetDomain(1, rg.Interval(0, sampling_count - 1))
        temp_isocurves = [temp_surface.IsoCurve(0, v_val) for v_val in range(sampling_count)]

        temp_isocurves_shortened = []

        for isocurve in temp_isocurves:
            # getting the length and the domain of every isocurve
            length = isocurve.GetLength()
            start_t, end_t = isocurve.Domain[0], isocurve.Domain[1]
            t_delta = end_t - start_t
            t_differential = t_delta / length
            # calculating how much the offset_dis result in t_val change
            t_shift = t_differential * offset_dis
            # creating variations for the different offset options
            start_t_new, end_t_new = start_t, end_t
            if (sides == 0):
                start_t_new = start_t + t_shift
                splits = [start_t_new]
                data_to_consider = 1
            if (sides == 1):
                end_t_new = end_t - t_shift
                splits = [end_t_new]
                data_to_consider = 0
            if (sides == 2):
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
        srf = rg.Brep.CreateFromLoftRebuild(uv_switched_curves, rg.Point3d.Unset, rg.Point3d.Unset, loft_type, False, 50)[0]
        # getting the loft as a nurbssurface out of the resulting brep
        srf = srf.Faces.Item[0].ToNurbsSurface()

        domain = rg.Interval(0, 1)
        srf.SetDomain(0, domain)
        srf.SetDomain(1, domain)

        return srf

    def __seam_regrades(self, surface, grading_percentage = .5, grading_side = 2, precision = 25):
        """ method that makes the beams move closer to each other at the seams
            :param grading_percentage:  Percent of the surface that is being regraded (default .5)
            :param grading_sides:       Which sides of the surface have to be regraded (0 = left, 1 = right, 2 = both, default)
            :return regraded_srf:       The uv_regraded_srf
        """

        local_srf = copy.deepcopy(surface)
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
        if (grading_side == 0):
            # only on the left side
            t_vals = []
            for t_val in ini_t_vals:
                local_t_val += t_val
                t_vals.append(local_t_val)
        elif (grading_side == 1):
            # only on the right side
            t_vals = []
            ini_t_vals.reverse()
            local_ini_t_vals = [0]
            local_ini_t_vals.extend(ini_t_vals[:-1])
            for t_val in local_ini_t_vals:
                local_t_val += t_val
                t_vals.append(local_t_val)
        elif (grading_side == 2):
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

        return new_srf

global_network = GlobalNetwork(surfaces)

local_networks = global_network.local_networks

for local_network in local_networks:
    
    local_dowels = local_network.add_three_beams_connection()
    dowels.extend(local_dowels)

    local_dowels = local_network.add_two_beams_connection()
    dowels.extend(local_dowels)

    local_beams = [b.brep_representation(make_holes=False) for b in local_network.get_flatten_beams()]
    beams.extend(local_beams)