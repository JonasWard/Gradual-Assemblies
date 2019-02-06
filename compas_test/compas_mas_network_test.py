from compas.datastructures import Mesh
from compas_rhino.artists import MeshArtist

from compas.datastructures import Network
from compas_rhino.artists import NetworkArtist

def create_beam(x, y, z):

    s_x = 100
    s_y = 40
    s_z = 10

    # create a mesh
    mesh = Mesh()
    mesh.attributes = {'name': 'test', 'project': 'Dundee', 'type': 'beam'}

    # add vertices
    mesh.add_vertex(x=x, y=y, z=z)
    mesh.add_vertex(x=x+s_x, y=y+0, z=z)
    mesh.add_vertex(x=x+s_x, y=y+s_y, z=z)
    mesh.add_vertex(x=x, y=y+s_y, z=z)
    mesh.add_vertex(x=x, y=y, z=z+s_z)
    mesh.add_vertex(x=x+s_x, y=y, z=z+s_z)
    mesh.add_vertex(x=x+s_x, y=y+s_y, z=z+s_z)
    mesh.add_vertex(x=x, y=y+s_y, z=z+s_z)

    mesh.add_face([0, 1, 2, 3])
    mesh.add_face([0, 1, 5, 4])
    mesh.add_face([1, 2, 6, 5])
    mesh.add_face([2, 3, 7, 6])
    mesh.add_face([3, 0, 4, 7])
    mesh.add_face([4, 5, 6, 7])
    
    return mesh

# create a network
network = Network()

# add vertices
for i in range(5):
    for j in range(3):
        
        if i % 2 == 0:
            network.add_vertex('%s:%s' % (i, j), {'x': i * 200, 'y': j * 300, 'z': 0, 'type': 'beam'})
        else:
            network.add_vertex('%s:%s' % (i, j), {'x': i * 200, 'y': j * 300, 'z': 0, 'type': 'nothing'})

# iterate through the vertex dictionary of the network and add a mesh in each vertext that has type: beam

beams = []

for key in network.vertex:
    
    type, x, y, z = network.get_vertex_attributes(key, ['type', 'x', 'y', 'z'])
    
    if type == 'beam':
        
        beam = create_beam(x, y, z)
        beams.append(beam)
        
artist = NetworkArtist(network, layer='MAS::network')
artist.clear_layer()
artist.draw_vertices()
artist.draw_vertexlabels()
artist.draw_edges()
#artist.redraw()

for i, beam in enumerate(beams):

    # draw mesh in rhino (artist concept)
    artist = MeshArtist(beam, layer='MAS::test_mesh')
    
    if i == 0:
        artist.clear_layer()
    artist.draw_vertices()
    artist.draw_edges()
    artist.draw_faces(join_faces=True)

artist.redraw()
