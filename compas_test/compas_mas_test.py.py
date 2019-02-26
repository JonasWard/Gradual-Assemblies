from compas.datastructures import Mesh
from compas_rhino.artists import MeshArtist

s_x = 500
s_y = 120
s_z = 40

# create a mesh
mesh = Mesh()
mesh.attributes = {'name': 'test', 'project': 'Dundee', 'type': 'beam'}


# add vertices
mesh.add_vertex(x=0, y=0, z=0)
mesh.add_vertex(x=s_x, y=0, z=0)
mesh.add_vertex(x=s_x, y=s_y, z=0)
mesh.add_vertex(x=0, y=s_y, z=0)
mesh.add_vertex(x=0, y=0, z=s_z)
mesh.add_vertex(x=s_x, y=0, z=s_z)
mesh.add_vertex(x=s_x, y=s_y, z=s_z)
mesh.add_vertex(x=0, y=s_y, z=s_z)

mesh.add_face([0, 1, 2, 3])
mesh.add_face([0, 1, 5, 4])
mesh.add_face([1, 2, 6, 5])
mesh.add_face([2, 3, 7, 6])
mesh.add_face([3, 0, 4, 7])
mesh.add_face([4, 5, 6, 7])

print mesh

# draw mesh in rhino (artist concept)
artist = MeshArtist(mesh, layer='MAS::test_mesh')
artist.clear_layer()
artist.draw_vertices()
artist.draw_edges()
artist.draw_faces(join_faces=True)
artist.redraw()
