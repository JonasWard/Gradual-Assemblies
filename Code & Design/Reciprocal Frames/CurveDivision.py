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

points_raw = []
global_points = []
for j in range(items):
    plane = new_curve.PerpendicularFrameAt(j)[1]
    point_list = []
    for i in range(count):
        local_point = rg.Intersect.Intersection.CurvePlane(curves[i], plane, 0.01)[0].PointB
        print local_point
        point_list.append(local_point)
        points_raw.append(local_point)

    global_points.append(point_list)
#
# print global_points
