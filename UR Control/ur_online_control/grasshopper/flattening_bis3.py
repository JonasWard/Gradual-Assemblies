import math
import Rhino.Geometry as rg

global x_delta, z_delta, pd_min, pd_max, pd_range
global top_z, angle_scale

## python set variables
# controlling the pd function
# x_delta = 10.0
# z_delta = 10.0
# pd_min = .1
# pd_max = .65

# grid spacing for functions
# z_space = .5
# x_space = 1.0

# x_count = 6
# z_count = 21

# pigeon parameters

pigeon_height = 15.0
pigeon_width = 18.0
pd_default = .3
default_spacing = 20.0

## grasshopper informed

x_count = x_count
z_count = z_count

base_layer_count = base_layer_count

perp_bool = perp_bool

pd_range = pd_max - pd_min

x0 = base_point.X
y0 = base_point.Y
z0 = base_point.Z

# regular function
iteration_count = iteration_count
deviation_value = deviation_value

# distance function

angle_scale = cancer

pt_list = []

spacing = 150.0
for i in range(8):
    x_val = (i - 3.5) * spacing / 2.0
    for j in range(6):
        z_val = (j + float(i % 2) / 2.0) * spacing
        point = rg.Point3d(x_val, 0, z_val)
        pt_list.append(point)

## pre-calculations

tau = math.pi * 2

def topFlatCount(last_point_list):
    z_list = []
    for p in last_point_list:
        z_list.append(p.Z)
    # calculating the height delta in the row
    min_z = min(z_list)
    max_z = max(z_list)
    h_delta = max_z - min_z
    print "delta: ", h_delta
    row_count = math.ceil((max_z-min_z) / (pd_range * pigeon_height))
    top_line_z = max_z + row_count * pd_min * pigeon_height
    return int(row_count), top_line_z

xz_plane = rg.Plane(rg.Point3d(0, 0, 0), rg.Vector3d(0, 1, 0))

def perpVector(point0, point1, surface = xz_plane):
    p0x, p0y, p0z = point0.X, point0.Y, point0.Z
    p1x, p1y, p1z = point1.X, point1.Y, point1.Z
    x_val, y_val, z_val = (p0x + p1x) / 2, (p0y + p1y) / 2, (p0z + p1z) / 2
    if (perp_bool):
        # translate to origin
        x1, y1, z1 = p0x - x_val, p0y - y_val, p0z - z_val
        # rotation around y-axis
        x2, y2, z2 = z1, y1, -x1
        perp_vec = rg.Vector3d(x2, y2, z2)
    else:
        perp_vec = rg.Vector3d(0,0,1)
    return x_val, y_val, z_val, perp_vec

def pdFunction(x_val_unitized, z_val_unitized):
    angle_x = x_val_unitized % x_delta * tau / x_delta
    angle_z = z_val_unitized % z_delta * tau / z_delta
    angle = angle_x + angle_z
    # superposition values
    graded_sin_sum = 0
    for k in range(iteration_count):
        graded_sin_sum += math.sin(deviation_value*angle/float(k + 1))
    graded_sin_sum /= float(iteration_count)
    local_pd_unit = (graded_sin_sum + 1.0)/2
    local_pd = local_pd_unit * pd_range
    local_pd += pd_min
    return local_pd

def pdDistanceFunction(x_val, z_val, angle_scale):
    local_distance = []
    x_val -= x0
    z_val -= z0
    for pt in pt_list:
        dist = ((pt.X - x_val * x_space)**2 + (pt.Z - z_val * z_space)**2)**.5
        local_distance.append(dist)
    distance = min(local_distance)
    print distance
    abstract = start - distance
    value = (abstract + abs(abstract)) / (2 * start)
    local_pd_unit = value
    local_pd = local_pd_unit * pd_range
    local_pd += pd_min
    return local_pd

def piping(plane, height):
    radius = pigeon_width / 2.0
    circle = rg.Circle(plane, radius)
    pipe = rg.Cylinder(circle, -height)
    return pipe

def pointGeneration(top_layer_count):

    # pre calculations
    start_x_count = x_count + (z_count - 1 - z_count % 2) + top_layer_count
    total_list, useful_list, pipe_list, previous_list = [], [], [], []
    new_list, plane_list, curve_list = [], [], []

    range_length = int(z_count + top_layer_count)

    for j in range(range_length):
        # previous_list cleaning
        previous_list = new_list
        new_list = []

        # piramid scheme and filtering
        local_x_count_len = start_x_count - j
        start_useful = int((local_x_count_len + (j + 1) % 2 - x_count) / 2)
        end_useful = int(start_useful + x_count - (j + 1) % 2 - 1)

        z_val_unitized = j * z_space

        if (j < base_layer_count):
            perp_vec = rg.Vector3d(0,0,1)
            z_val = pigeon_height * pd_default * j
            z_val_top = pigeon_height * pd_default
            for i in range(local_x_count_len):
                x_val_unitized = (- float(local_x_count_len) / 2 + i)
                x_val = x_val_unitized * default_spacing
                x_val_unitized *= x_space
                base_point = rg.Point3d(x_val + x0, y0, z_val + z0)
                top_point = rg.Point3d(x_val + x0, y0, z_val + z_val_top + z0)
                new_list.append(top_point)
                total_list.append(base_point)
                if (i >= start_useful) and (i <= end_useful):
                    useful_list.append(base_point)
                    top_plane = rg.Plane(top_point, perp_vec)
                    plane_list.append(top_plane)
                    pipe_list.append(piping(top_plane, z_val_top))
        elif (j < z_count):
            for i in range(local_x_count_len):
                # setting the x_value fot the function
                x_val_unitized = (- float(local_x_count_len) / 2 + i) * x_space
                # calculating the midpoints of the previous top_points
                pt0 = previous_list[i]
                pt2 = previous_list[i+1]
                x_val, y_val, z_val, perp_vec = perpVector(pt0, pt2)
                if (distance_function):
                    pd = pdDistanceFunction(x_val, z_val, angle_scale)
                else:
                    pd = pdFunction(x_val_unitized, z_val_unitized)
                local_height = pigeon_height * pd
                base_point = rg.Point3d(x_val, y_val, z_val)
                if (shift_x_bool):
                    delta_pt = perp_vec / math.sqrt(perp_vec * perp_vec) * local_height
                else:
                    delta_pt = rg.Point3d(0, 0, local_height)
                top_point = base_point + delta_pt
                new_list.append(top_point)
                total_list.append(base_point)
                if (i >= start_useful) and (i <= end_useful):
                    useful_list.append(base_point)
                    top_plane = rg.Plane(top_point, perp_vec)
                    plane_list.append(top_plane)
                    pipe_list.append(piping(top_plane, local_height))
        else:
            division_factor = top_layer_count - (j - z_count)
            for i in range(local_x_count_len):
                pt0 = previous_list[i]
                pt2 = previous_list[i+1]
                x_val, y_val, z_val, perp_vec = perpVector(pt0, pt2)
                local_height = (top_z - z_val) / division_factor
                base_point = rg.Point3d(x_val, y_val, z_val)
                if (shift_x_bool):
                    delta_pt = perp_vec / math.sqrt(perp_vec * perp_vec) * local_height
                else:
                    delta_pt = rg.Point3d(0, 0, local_height)
                top_point = base_point + delta_pt
                new_list.append(top_point)
                total_list.append(base_point)
                if (i >= start_useful) and (i <= end_useful):
                    useful_list.append(base_point)
                    top_plane = rg.Plane(top_point, perp_vec)
                    plane_list.append(top_plane)
                    pipe_list.append(piping(top_plane, local_height))
        curve = rg.PolylineCurve(new_list)
        curve_list.append(curve)
    return new_list, plane_list, pipe_list, curve_list

# actual output
last_list, plane_list, pipe_list, curve_list = pointGeneration(0)

# setting the values for flattening the top off
top_rowCount, top_z = topFlatCount(last_list)

last_list, plane_list, pipe_list, curve_list = pointGeneration(top_rowCount)

a = plane_list
