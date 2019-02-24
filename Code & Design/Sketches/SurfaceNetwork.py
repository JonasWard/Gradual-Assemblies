"""Provides a scripting component.
    Inputs:
        x: The x script variable
        y: The y script variable
    Output:
        a: The a output variable"""

__author__ = "ytakzk"
__version__ = "2019.02.23"


import Rhino.Geometry as rg

from geometry import GlobalNetwork, LocalNetwork

import os

if os.name == 'posix':
    print "you're a Mac!"
    path_to_append = single_parent
    sys.path.append(path_to_append)

    print path_to_append

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
