"""Provides a scripting component.
    Inputs:
        x: The x script variable
        y: The y script variable
    Output:
        a: The a output variable"""

__author__ = "ytakzk"
__version__ = "2019.02.23"

import os
import sys
import Rhino.Geometry as rg

geometry_lib_path = os.path.join("/Users/jonas/Dropbox/0.dfab/Trimester 2/Project I - Gradual Assemblies/Gradual-Assemblies/UR_Control")
print geometry_lib_path
sys.path.append(geometry_lib_path)

import geometry.beam as B
import geometry.dowel as D
import geometry.hole as H
import geometry.joint_holes as JH
import geometry.local_network as LN
import geometry.global_network as GN
import geometry.surface as SrfC
import geometry.shared_edge as SE
import geometry.surface_keystone as Key

reload(B)
reload(D)
reload(H)
reload(JH)
reload(LN)
reload(SrfC)
reload(GN)
reload(SE)
reload(Key)

dowels = []
beams = []
tmp = []
local_networks = []

if (len(surface_network_index) != len(top_priority_index)):
    ValueError('surface_network_index must be the same size as top_priority_index')

# network

surface_network_sets = []
priorities = []

for string, priority_index in zip(surface_network_index, top_priority_index):

    values = string.split('&')

    surface_network = []

    priority_index_v = 0

    for v_values in values:

        surface_network_subset = []
        for v, index in enumerate(v_values.split(',')):

            index = int(index)

            if index == priority_index:

                priority_index_v = v

            surface = SrfC.Surface(surfaces[index])
            surface_network_subset.append(surface)

        surface_network.append(surface_network_subset)

    priorities.append(priority_index_v)

    surface_network_sets.append(surface_network)

for surface_network, has_loop, top_priority_v_index in zip(surface_network_sets, has_loops, priorities):

    local_network = LN.LocalNetwork(surface_network, has_loop, top_priority_v_index, type_args=[[40, 20, 20, True, False, False], long_list])

    local_dowels = local_network.add_three_beams_connection()
    dowels.extend([d.brep_representation() for d in local_dowels])

    local_dowels = local_network.add_two_beams_connection()
    dowels.extend([d.brep_representation() for d in local_dowels])

    local_beams = [b.brep_representation(make_holes=False) for b in local_network.get_flatten_beams()]
    beams.extend(local_beams)

    local_networks.append(local_network)

beam_0 = local_networks[0].beams[0][0]
beam_1 = local_networks[0].beams[1][0]
beam_2 = local_networks[0].beams[2][0]

# middle_beam = beam_0
# other_beams = [beam_0, beam_1, beam_2]
# o_beams = [o_beam.brep_representation() for o_beam in other_beams]
# lines = []
# joint_holess = JH.JointHoles(other_beams, type = 4, type_args=[[40, 20, 20, True, False, False], long_list])
# joint_holess.triple_joint_optimisation_f()
#
# lines.append(joint_holess.transformed_middle_beam.top_line)
# lines.append(joint_holess.transformed_middle_beam.bot_line)
# lines.append(joint_holess.transformed_other_beam.top_line)
# lines.append(joint_holess.transformed_other_beam.bot_line)
#
# pts = joint_holess.pts_set
# avg_pt = joint_holess.avg_pt
# diamond = joint_holess.diamond
# diamond_off = joint_holess.diamond_offset
# new_pts = joint_holess.new_pt_set

# top_line = joints.transformed_middle_beam.top_line
# bot_line = joints.transformed_middle_beam.bot_line
