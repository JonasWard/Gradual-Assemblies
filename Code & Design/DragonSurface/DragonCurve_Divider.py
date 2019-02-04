# Dragon Curve Divider

import Rhino.Geometry as rg

# inherinted values

DragonCurve_s
divisions

# reading outs

for DragonCurve in DragonCurve_s:

    if ((DragonCurve.ID % 4) == 0):
        first_value = 0
        special_case = False
    elif ((DragonCurve.ID % 4) == 1):
        first_value = 2
        special_case = False
    elif ((DragonCurve.ID % 4) == 2):
        first_value = 1
        special_case = True
    else:
        first_value = 3
        special_case = True

    if not(special_case):
    max_value = divisions - first_value - 1
    for i in range(first_value, max_value, 4):
        rg.LineCurve(DragonCurve.division_pts[i], DragonCurve.division_pts[i + 1])
