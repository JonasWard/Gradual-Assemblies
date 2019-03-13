# snippet to find the extra drill lines for the screw Holes

import math as m

def get_screw_holes(self):
    # drill parameters
    drill_angle = 55            # in reference to the plain
    drill_depth = 20            # length drill line in wood
    drill_start_tolerance = 40  # extension drill line outside of the beam
    x_spacing = 30              # how much x deviates from the average position


    # getting the average location of the start & end joint groups on the beam
    dowel_pts = [dowel.Origin for dowel in self.holes]

    # getting the even spacing in between the dowel_lines
    new_line_neg = 0.0
    new_line_neg_count = 0
    new_line_pos = 0.0
    new_line_pos_count = 0

    # seperating and tallying up the negative from the positive values
    for dowel_pt in dowel_pts:
        if dowel_pt.X > 0:
            new_line_pos_count += 1
            new_line_pos = dowel_pt.X
        else:
            new_line_neg_count += 1
            new_line_neg = dowel_pt.X

    # average x locations of the joints on the beam
    start_x = new_line_neg / new_line_neg_count
    end_x = new_line_pos / new_line_pos_count
    delta_x = end_x - start_x

    spacing_x = delta_x * .25
    if spacing_x < 150.0:
        spacing_x = 150

    # setting the raw locations where the holes should be
    neg_x_loc = start_x + spacing_x
    pos_x_loc = end_x - spacing_x

    y_delta = m.sin(m.radians(drill_angle))
    z_delta = m.cos(m.radians(drill_anlge))

    # locations on the beam
    int_y_coordinate = self.dy * .5 - 50
    int_z_coordinate = self.dz

    # locations in the beam
    bot_y_coordinate = int_y_coordinate - y_delta * drill_depth
    bot_z_coordinate = int_z_coordinate - z_delta * drill_depth

    # locations outside of the beam
    top_y_coordinate = int_y_coordinate + y_delta * drill_start_tolerance
    top_z_coordinate = int_z_coordinate + z_delta * drill_start_tolerance

    # setting up all the point_set
    #    ---------------------------------------------------
    #   |     o     ln_0 -> *          * <- ln_1      o     |
    #   |  o    o       --------------------        o    o  |
    #   |    o      * <- ln_2      -   ln_3 -> *       o    |
    #    ---------------------------------------------------

    # ln_0
    # pt inside the beam
    x0 = start_x + x_spacing
    y0 = bot_y_coordinate
    z0 = bot_y_coordinate
    pt_0 = rg.Point3d(x0, y0, z0)
    # pt inside the beam
    x1 = start_x + x_spacing
    y1 = top_y_coordinate
    z1 = top_z_coordinate
    pt_1 = rg.Point3d(x1, y1, z1)
    ln_0 = rg.Line(pt_0, pt_1)

    # ln_1
    # pt inside the beam
    x0 = end_x - x_spacing
    y0 = bot_y_coordinate
    z0 = bot_y_coordinate
    pt_0 = rg.Point3d(x0, y0, z0)
    # pt inside the beam
    x1 = end_x - x_spacing
    y1 = top_y_coordinate
    z1 = top_z_coordinate
    pt_1 = rg.Point3d(x1, y1, z1)
    ln_1 = rg.Line(pt_0, pt_1)

    # ln_2
    # pt inside the beam
    x0 = start_x - x_spacing
    y0 = - bot_y_coordinate
    z0 = bot_y_coordinate
    pt_0 = rg.Point3d(x0, y0, z0)
    # pt inside the beam
    x1 = start_x - x_spacing
    y1 = - top_y_coordinate
    z1 = top_z_coordinate
    pt_1 = rg.Point3d(x1, y1, z1)
    ln_2 = rg.Line(pt_0, pt_1)

    # ln_3
    # pt inside the beam
    x0 = end_x + x_spacing
    y0 = - bot_y_coordinate
    z0 = bot_y_coordinate
    pt_0 = rg.Point3d(x0, y0, z0)
    # pt inside the beam
    x1 = end_x + x_spacing
    y1 = - top_y_coordinate
    z1 = top_z_coordinate
    pt_1 = rg.Point3d(x1, y1, z1)
    ln_3 = rg.Line(pt_0, pt_1)
