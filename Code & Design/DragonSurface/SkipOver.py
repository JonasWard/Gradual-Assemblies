# skip over

import Rhino.Geometry as rg

# parameters

points
how_many
side_step

first_length = len(points)
lines = []

for k in range(first_length):
    start_value = k % side_step
    amount = len(point_list)
    point_list = points[k]
    for i in range(start_value, amount - 1, how_many):
        local_line = rg.LineCurve(point_list[i], point_list[i + 1])
        lines.append(local_line)
