from compas.datastructures import Network

from compas_rhino.artists import NetworkArtist

# create Network
network = Network()
print network.vertex

# add vertices
for i in range(5):
    for j in range(3):
        if i%2 == 0:
            network.add_vertex(str(i)+':'+str(j),{'x':i*200,'y':j*300, 'z':0, 'type':'beam'})
        else:
            network.add_vertex(str(i)+':'+str(j),{'x':i*200,'y':j*300, 'z':0, 'type':'nothing'})

# iterate through the vertex dictionary of the network and add a mesh in each vertex that
# has type: beam
print network.vertex
for key in network.vertex:
    print key


# draw by artist
artist = NetworkArtist(network, layer='MAS::network')
artist.clear_layer()
artist.draw_vertices()
artist.draw_vertexlabels()
artist.draw_edges()
artist.redraw()