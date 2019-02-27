"""Provides a scripting component.
    Inputs:
        x: The x script variable
        y: The y script variable
    Output:
        a: The a output variable"""

__author__ = "ytakzk"
__version__ = "2019.02.23"


import Rhino.Geometry as rg

import os

if os.name == 'posix':
    geometry_lib_path = "/Users/jonas/Dropbox/0.dfab/Trimester 2/Project I - Gradual Assemblies/Gradual-Assemblies/UR_Control"
    print geometry_lib_path
    sys.path.append(geometry_lib_path)

    import geometry.beam as beam
    import geometry.dowel as dowel
    import geometry.hole as hole
    import geometry.joint_holes as joint_holes
    import geometry.local_network as local_network
    import geometry.global_network as global_network
    import geometry.surface as surface
    import geometry.shared_edge as shared_edge
    import geometry.surface_keystone as keystone

    reload(beam)
    reload(dowel)
    reload(hole)
    reload(joint_holes)
    reload(local_network)
    reload(surface)
    reload(global_network)
    reload(shared_edge)
    reload(keystone)

from geometry import GlobalNetwork, LocalNetwork

dowels = []
beams = []
tmp = []

global_network = GlobalNetwork(surfaces)

local_networks = global_network.local_networks

for local_network in local_networks:

    local_dowels = local_network.add_three_beams_connection()
    dowels.extend(local_dowels)

    local_dowels = local_network.add_two_beams_connection()
    dowels.extend(local_dowels)

    local_beams = [b.brep_representation(make_holes=False) for b in local_network.get_flatten_beams()]
    beams.extend(local_beams)
