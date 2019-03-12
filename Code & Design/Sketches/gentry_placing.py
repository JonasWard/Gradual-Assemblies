def placement_sequence_gentry_position(pick_pl, place_pl):

	# setting variables
	pick_b_pt = pick_pl.Origin
	place_b_pt = place_pl.Origin

	cos_angle = .7
	sphere_radius = 1700


	# picking position
	x1, y1, z1 = pick_b_pt.X, pick_b_pt.Y, pick_b_pt.Z
	x0 = x_plane.X 		# replace with gentry vals
	r = 1700    # in mm

	delta_z = cos_angle * sphere_radius       # cos 30 degree - could be slightly more or less if need be
	z0 = z1 - delta_z
	delta_x = x1 - x0
	delta_y = (sphere_radius ** 2 - delta_z ** 2 - delta_x ** 2) ** .5    # has to change depending on the location

	gentry_pick_pl = rg.Plane.WorldXY
	gentry_pick_pl.Translate(rg.Vector3d(x0, y1 - delta_y, z0))

	# placement position
	x1, y1, z1 = place_b_pt.X, place_b_pt.Y, place_b_pt.Z
	x0 = x_plane.X

	delta_z = cos_angle * sphere_radius       # cos 30 degree - could be slightly more or less if need be
	z0 = z1 - delta_z		# replace with gentry vals
	delta_x = x1 - x0
	delta_y = (sphere_radius ** 2 - delta_z ** 2 - delta_x ** 2) ** .5    # has to change depending on the location

	gentry_place_pl = rg.Plane.WorldXY
	gentry_place_pl.Translate(rg.Vector3d(x0, y1 + delta_y, z0))

	return gentry_pick_pl, gentry_place_pl
