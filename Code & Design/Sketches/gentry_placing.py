# pseudocode that might define location of the gentry
# for given placement point and static z_value, radius and angle

x1, y1, z1 = placement_plane.Origin
x0 = value
r = 1700    # in mm
alfa = 1.05

delta_z = .5 * r
z0 = z1 - delta_z
delta_x = x1 - x0
y0 = (r ** 2 - delta_z ** 2 - delta_x ** 2) ** .5    # has to change depending on the location

extra_value = 1000      # periscoper spacing?
gentry_location = pt(x0, y0, z0 + extra_value)
