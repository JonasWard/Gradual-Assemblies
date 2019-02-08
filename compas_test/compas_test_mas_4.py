from compas.datastructures import Network

from compas_rhino.artists import NetworkArtist

range_x = 10
range_y = 5

# create Network
network = Network()
print network.vertex


# add vertices
count = 0
for j in range(range_y):
    for i in range(range_x):
        #network.add_vertex(str(i)+':'+str(j),{'x':i*500,'y':j*100, 'z':0})
        network.add_vertex(count, {'x':i*500,'y':j*100, 'z':0})
        count += 1

# add edges for beams
for j in range(range_y):
    for i in range(range_x):
        if j%2 == 0:
            if i%2 == 0 and i < range_x - 1:
                network.add_edge(j*range_x + i, j*range_x + i+1, {'type':'beam'})
        else:
            if i%2 != 0 and i < range_x - 1:
                network.add_edge(j*range_x + i, j*range_x + i+1, {'type':'beam'})


# add edges for connections
for j in range(range_y):
    for i in range(range_x):
        if j%2 == 0 and j < range_y-1:
             if i > 0 and i < range_x - 1:
                 network.add_edge(j*range_x + i, (j+1)*range_x + i, {'type':'connection'})
                 network.add_edge((j+1)*range_x + i, (j+2)*range_x + i, {'type':'connection'})


# get different edge types
for key in network.edge:
    print network.edge[key]
for u,v in network.edges():
    print u,v






# draw by artist
artist = NetworkArtist(network, layer='MAS::network')
artist.clear_layer()
artist.draw_vertices()
artist.draw_vertexlabels()
artist.draw_edges(color = (255,0,0))
artist.draw_edgelabels()
artist.redraw()