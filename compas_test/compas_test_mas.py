from compas.datastructures import Mesh
# from compas.datastructures import Network

from compas_rhino.artists import MeshArtist
# from compas_rhino.artists import NetworkArtist

# params
s_x = 500
s_y = 120
s_z = 40

# create a Mesh instance
mesh = Mesh()
print mesh


# add vertices
# lower ones
mesh.add_vertex(x=0,y=0,z=0)
mesh.add_vertex(x=s_x,y=0,z=0)
mesh.add_vertex(x=s_x,y=s_y,z=0)
mesh.add_vertex(x=0,y=s_y,z=0)

# upper ones
mesh.add_vertex(x=0,y=0,z=s_z)
mesh.add_vertex(x=s_x,y=0,z=s_z)
mesh.add_vertex(x=s_x,y=s_y,z=s_z)
mesh.add_vertex(x=0,y=s_y,z=s_z)

# add faces
mesh.add_face([0,1,2,3])
mesh.add_face([4,5,6,7])
mesh.add_face([0,1,5,4])
mesh.add_face([2,3,7,6])
mesh.add_face([1,2,6,5])
mesh.add_face([3,0,4,7])

# edges are automatically added, half-edge representations

# drawing (artist concept)
artist = MeshArtist(mesh, layer='COMPAS::MeshArtist')
artist.clear_layer()
artist.draw_faces(join_faces=True)
artist.draw_vertices()
artist.draw_vertexlabels()
artist.draw_edges()
artist.redraw()