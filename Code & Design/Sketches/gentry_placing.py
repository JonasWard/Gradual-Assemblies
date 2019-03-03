# pseudocode that might define location of the gentry
# for given placement point and static z_value, radius and angle

import Rhino.Geometry as rg

x1, y1, z1 = placement_pt.X, placement_pt.Y, placement_pt.Z
x0 = x_plane.X
r = 1700    # in mm

sphere = rg.Sphere(placement_pt, r).ToBrep()
print sphere
x_plane = rg.Plane.WorldYZ
x_plane.Translate(rg.Vector3d(x0, 0, 0))
ignore, curves, ignore = rg.Intersect.Intersection.BrepPlane(sphere, x_plane, .01)
a = curves

delta_z = .7 * r       # cos 30 degree - could be slightly more or less if need be
z0 = z1 - delta_z
delta_x = x1 - x0
delta_y = (r ** 2 - delta_z ** 2 - delta_x ** 2) ** .5    # has to change depending on the location

extra_value = 1000      # periscoper spacing?
gentry_location = rg.Point3d(x0, y1 - delta_y, z1  - delta_z)
