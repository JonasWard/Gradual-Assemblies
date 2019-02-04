from compas.datastructures import Mesh

from compas_rhino.artists import MeshArtist


s_x = 500
s_y = 120
s_z = 40

# create a mesh
mesh = Mesh()
mesh.attributes['name'] = 'David'
mesh.attributes.update({'project':'Dundee','type':'beam'})

print mesh

# add vertices
mesh.add_vertex(x=0,y=0,z=0)
mesh.add_vertex(x=s_x,y=0,z=0)
mesh.add_vertex(x=s_x,y=s_y,z=0)
mesh.add_vertex(x=0,y=s_y,z=0)


# add faces
mesh.add_face([0,1,2,3])

# draw mesh in rhino (artist concept)
artist = MeshArtist(mesh, layer='MAS::test_mesh')
artist.clear_layer()
artist.draw_vertices()
artist.draw_edges()
artist.draw_faces()
artist.redraw()
