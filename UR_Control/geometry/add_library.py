# snippet of code to make this python component look for it's code in the parent folder of the .gh file

import os, sys

ghComp = ghenv.Component
ghDoc = ghComp.OnPingDocument()

file_name = "posSpace.py"
gh_file_location = ghDoc.FilePath
parent = os.path.dirname(os.path.realpath(gh_file_location))
parent = os.path.dirname(os.path.realpath(parent))
parent = os.path.dirname(os.path.realpath(parent))

geometry_lib_path = os.path.join(parent, 'UR_CONTROL')
sys.path.append(geometry_lib_path)

import geometry.beam as beam
import geometry.dowel as dowel
import geometry.hole as hole
