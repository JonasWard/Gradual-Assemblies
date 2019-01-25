import Rhino.Geometry as rg

# reciprocal curve division

# grasshopper parameters

curves
spacing

count = len(curves)

# subdividing the curve

length = 0

for i in range(count):
    length += curves[i].GetLength()

items = int(length / (count * spacing))
new_domain = rg.Interval(0.0, (items - 1) * 1.0)

for i in range(count):
    curves[i].Domain = new_domain

points = []
for j in range(items):
    point = rg.Point3d(0,0,0)
    for i in range(count):
        point += curves[i].PointAt(j)
    point /= 3
    points.append(point)

new_curve = rg.Curve.CreateInterpolatedCurve(points, 3)

new_curve.Domain = new_domain

global_points = []
for j in range(items):
    point = new_curve.PointAt(j)
    point_list = []
    for i in range(count):
        ignore, t_value = curves[i].ClosestPoint(point, 30000)
        point_list.append(curves[i].PointAt(t_value))
    global_points.append(point_list)

print global_points
