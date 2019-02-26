import itertools

from compas.datastructures import Mesh
from compas_rhino.artists import MeshArtist

from compas.datastructures import Network
from compas_rhino.artists import NetworkArtist

from collections import OrderedDict

stuff = ["x", "y", "z", "x_s", "y_s", "z_s"]

x = 0
y = 0
z = 0
s_x = 100
s_y = 40
s_z = 10

# create a mesh
mesh = Mesh()

# add vertices
variable_list = [x, y, z, x+s_x, y+s_y, z+s_z]

temp_list = []

for p in itertools.product(variable_list, repeat=3):
    if p[0] == x or p[0] == x+s_x:
        if p[1] == y or p[1] == y+s_y:
            if p[2] == z or p[2] == z+s_z:
                temp_list.append(p)

new_list = list(set(temp_list))

new_list.sort(reverse = False)

print new_list

count = 0

for p in new_list:
    mesh.add_vertex(count, {'x': p[0], 'y': p[1], 'z': p[2]})
    count += 1

#add faces
mesh.add_face([0,1,2,3])
mesh.add_face([4,5,6,7])
mesh.add_face([4,5,6,7])

#draw mesh in Rhino
artist = MeshArtist(mesh, layer="MAS")
artist.clear_layer()
artist.draw_vertices()
artist.draw_vertexlabels()
#artist.draw_edges()
#artist.draw_edgelabels()
#artist.draw_faces()
artist.redraw()