# skip over

import Rhino.Geometry as rg

# parameters

points
how_many
side_step

first_length = len(points)
lines = []
lines_list = []

for k in range(first_length):
    start_value = k % side_step
    amount = len(point_list)
    point_list = points[k]
    local_line_list = []
    for i in range(start_value, amount - 1, how_many):
        local_line = rg.LineCurve(point_list[i], point_list[i + 1])
        local_line_list.append(local_line)
        lines.append(local_line)
    lines_list.append(local_line_list)

# dowels = []
# beams = []
# for k in range (1, len(lines) - 1, 1):
#     local_lines = lines[k]
#     local_dowels = []
#     local_beams = []
#     for i in range(1, len(local_lines) - 1, 1):
#         local_line = local_lines[i]
#
#         rg.Intersection
