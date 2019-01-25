# l_system

# import Rhino.Geometry as rg
#
# # grasshopper variables
#
# seed_location
# angle
# spacing
# layer_count

# joint class, so far using box representations
# based on a seed point an angle of the inclination of the 2nd plane
# the previous frame and a length parameter

class Joint(object):

    def __init__(self, start_frame, angle_in_plane, angle_perp_to_plain, spacing):
        pt_0, pt_h, pt_1, pt_2 = rg.Point3d(0, 0, 0), rg.Point3d(spacing, 0, 0), rg.Point3d(2 * spacing, 0, 0), rg.Point3d(2 * spacing, 0, 0)
        rotation_a = rg.Transform.Rotation(angle, pt_h)
        rotation_b = rg.Transform.Rotation(angle, pt_0)
        translate = rg.Transform.Translation(start_point)
        pt_2.Transform(rotation_a)
        pt_1.Transform(rotation_b), pt_h.Transform(rotation_b)
        pt_2.Transform(translate), pt_1.Transform(translate), pt_0.Transform(traslate), pt_h.Transform(translate)

# l-system logic

# setting up some pattern

pattern_map = [['A', 'B'], [['A', 'B'], ['B', 'A']]]
pattern_variaties = len(pattern_map[0])

# starting positions

seed = []
seed.append(['A'])

# going through the loop and appending to the system

for i in range (1, 10, 1):
    local_seeds = seed[i - 1]
    new_seed_list = []
    for uni_seed in local_seeds:
        for k in range(pattern_variaties):
            pattern = pattern_map[0][k]
            if uni_seed == pattern:
                [new_seed_list.append(replace) for replace in pattern_map[1][k]]
    seed.append(new_seed_list)
    print seed

# generating the grid
#
# for i in range
