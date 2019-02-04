from compas.datastructures import Mesh
from compas.datastructures import Network

from compas_rhino.artists import MeshArtist
from compas_rhino.artists import NetworkArtist

# params
s_x = 500
s_y = 120
s_z = 40

# create a network
network = Network()

# add vertices
for i in range(5):
    for j in range(3):
        network.add_vertex(str(i)+':'+str(j), {'x':i*200, 'y':j*200, 'z':0, 'type':'beam'})

# draw network (artist concept)
artist = NetworkArtist(network, layer='MAS::network')
artist.clear_layer()
artist.draw_vertices()
artist.draw_edges()
artist.redraw()
