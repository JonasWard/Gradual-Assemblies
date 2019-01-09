import math
import Rhino.Geometry as rg

global x_delta, z_delta, pd_min, pd_max, pd_range

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
pd_default = .5
default_spacing = 20.0

## grasshopper informed

x_count = x_count
z_count = z_count

base_layer_count = base_layer_count

perp_bool = perp_bool

pd_range = pd_max - pd_min

# function
iteration_count = iteration_count
deviation_value = deviation_value

## pre-calculations

tau = math.pi * 2
start_x_count = x_count + (z_count - 1 - z_count % 2)
total_list = []
useful_list = []
pipe_list = []
previous_list = []
new_list= []
plane_list = []
curve_list = []

def topFlatCount(last_point_list):
    z_list = []
    for p in last_point_list:
        z_list.append(p.Z)
    # calculating the height delta in the row
    min_z = min(z_list)
    max_z = max(z_list)
    h_delta = max_z - min_z
    row_count = math.ceil((max_z-min_z) / (pd_range * pigeon_height))
    top_line_z = max_z + row_count * pd_max * pigeon_height
    return row_count, top_line_z

def perpVector(point0, point1):
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

def piping(plane, height):
    radius = pigeon_width / 2.0
    circle = rg.Circle(plane, radius)
    pipe = rg.Cylinder(circle, -height)
    return pipe

for j in range(z_count):
    # previous_list cleaning
    previous_list = new_list

    #except for 2nd last & last list
    if (j == z_count - 1):
        second_last_list = new_list
    new_list = []

    # piramid scheme and filtering
    local_x_count_len = start_x_count - j
    start_useful = (local_x_count_len + (j + 1) % 2 - x_count) / 2
    end_useful = start_useful + x_count - (j + 1) % 2 - 1

    z_val_unitized = j * z_space

    if (j < base_layer_count):
        perp_vec = rg.Vector3d(0,0,1)
        z_val = pigeon_height * pd_default * j
        z_val_top = pigeon_height * pd_default
        for i in range(local_x_count_len):
            x_val_unitized = (- float(local_x_count_len) / 2 + i)
            x_val = x_val_unitized * default_spacing
            x_val_unitized *= x_space
            base_point = rg.Point3d(x_val, 0, z_val)
            top_point = rg.Point3d(x_val, 0, z_val + z_val_top)
            new_list.append(top_point)
            total_list.append(base_point)
            if (i >= start_useful) and (i <= end_useful):
                useful_list.append(base_point)
                top_plane = rg.Plane(top_point, perp_vec)
                plane_list.append(top_plane)
                pipe_list.append(piping(top_plane, z_val_top))
    else:
        for i in range(local_x_count_len):
            # setting the x_value fot the function
            x_val_unitized = (- float(local_x_count_len) / 2 + i) * x_space
            # calculating the midpoints of the previous top_points
            pt0 = previous_list[i]
            pt2 = previous_list[i+1]
            x_val, y_val, z_val, perp_vec = perpVector(pt0, pt2)
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
    curve = rg.PolylineCurve(new_list)
    curve_list.append(curve)

# flattening the top off
last_listA = new_list
last_listB = second_last_list
top_rowCount, top_z = topFlatCount(last_list)

for j in range(top_rowCount):
    division_factor = top_rowCount - j

    even_list = last_listA
    uneven_list = last_listB
    last_listA = []
    last_listB = []
    # if even amount of z layers
    # meaning that the last layer (layerA) is the long one
    local_perp_vec_list = []
    temp_plane_list = []
    temp_pipe_list = []
    temp_last_listB = []
    temp_last_listA = []
    if (z_count % 2 == 0):
        if (j % 2 == 0):
            for k in range(x_count - 1):
                pt0 = even_list[k]
                pt2 = even_list[k+1]
                x_val, y_val, z_val, perp_vec = perpVector(pt0, pt2)
                local_height = (top_z - z_val) / division_factor
                base_point = rg.Point3d(x_val, y_val, z_val)
                if (shift_x_bool):
                    delta_pt = perp_vec / math.sqrt(perp_vec * perp_vec) * local_height
                else:
                    delta_pt = rg.Point3d(0, 0, local_height)
                top_point = base_point + delta_pt
                last_listA.append(top_point)
                total_list.append(base_point)
                useful_list.append(base_point)
                top_plane = rg.Plane(top_point, perp_vec)
                plane_list.append(top_plane)
                pipe_list.append(piping(top_plane, local_height))
        else:
            for k in range(1, x_count - 1, 1):
                pt0 = uneven_list[k]
                pt2 = uneven_list[k+1]
                x_val, y_val, z_val, perp_vec = perpVector(pt0, pt2)
                local_height = (top_z - z_val) / division_factor
                base_point = rg.Point3d(x_val, y_val, z_val)
                if (shift_x_bool):
                    delta_pt = perp_vec / math.sqrt(perp_vec * perp_vec) * local_height
                else:
                    delta_pt = rg.Point3d(0, 0, local_height)
                top_point = base_point + delta_pt
                temp_last_listB.append(top_point)
                total_list.append(base_point)
                useful_list.append(base_point)
                top_plane = rg.Plane(top_point, perp_vec)
                temp_plane_list.append(top_plane)
                temp_pipe_list.append(piping(top_plane, local_height))
                if (k == 1):
                    local_perp_vec_list.append(perp_vec)
                elif (k == x_count - 2):
                    local_perp_vec_list.append(perp_vec)
            # first point
            z_val = (top_z - even_list[0].Z) / (division_factor + 2)
            first_point = even_list[0] + rg.Point3d(0, 0, z_val * 2)
            top_plane = rg.Plane(first_point, local_perp_vec_list[0])
            last_listB.append(first_point)
            plane_list.append(top_plane)
            pipe_list.append()
            # all other planes
            for pts in temp_last_listB:
                last_listB.append(pts)
            for pln in temp_plane_list:
                plane_list.append(pts)
            for pip in temp_pipe_list:
                pipe_list.append(pip)
            # last point
            z_val = (top_z - even_list[x_count].Z) / (division_factor + 2)
            first_point = even_list[x_count] + rg.Point3d(0, 0, z_val * 2)
            top_plane = rg.Plane(first_point, local_perp_vec_list[1])
            last_listB.append(first_point)
            plane_list.append(top_plane)
            pipe_list.append()

    else:
        if (j % 2 == 0):
            for k in range(1, x_count -1, 1):
                pt = last_listA[k]
                xA, yA, zA = pt.X, pt.Y, pt.Z

        else:
            for pt in last_listB:
                xB, yB, zB = pt.X, pt.Y, pt.Z


a = plane_list
