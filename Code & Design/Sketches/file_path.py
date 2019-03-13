# Python code to run within a grasshopper python component to get the .gh's
# file location.

import os

ghComp = ghenv.Component
ghDoc = ghComp.OnPingDocument()

file_name = "SurfaceNetwork.py"
gh_file_location = ghDoc.FilePath
parent = os.path.dirname(os.path.realpath(gh_file_location))

single_parent = os.path.dirname(os.path.realpath(parent))
double_parent = os.path.dirname(os.path.realpath(single_parent))

file_path = os.path.join(parent, file_name)
print file_path

# hacky-hacky run-fun
execfile(file_path)
