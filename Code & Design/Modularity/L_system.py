# l_system

import Rhino.Geometry as rg
# import geometry as beamclass
#
# grasshopper variables

# seed_location
# angle
# spacing
# layer_count

# joint class, so far using box representations
# based on a seed point an angle of the inclination of the 2nd plane
# the previous frame and a length parameter

# geometric axioms:
# if the lower beam, flush to the base beam, doesn't deviate from the centerRod
# axis, namely low_beam_angle_in_plane = 0, it can (and should) be taken as if
# it were one beam

# relationships definition:
# 0 > next beam - on top ; angled beam - up out of the plane
# 1 > next beam - on top ; angled beam - down out of the plane
# 2 > next beam - on bottom ; angled beam - up out of the plane
# 3 > next beam - on bottom ; angled beam - down out of the plane

# top or bottom:
# top_bottom == True: 2nd beam is on top of the base frame
# top_bottom == False: 2nd beam in beneath top of the base frame

# general type definition
# type = [low_beam_angle_in_plane, up_beam_angle_y_axis_to_plane, up_beam_angle_in_plane, length, overlap, top_bottom, relation, height, width]
type_A = [.2, .15, .25, 1200, 120, True, 1, 40, 100]
type_B = [1, .5, .4, 1200, 120, False, 3, 40, 100]
type_C = [.2, .5, .5, 1200, 120, True, 1, 40, 100]
types = [type_A, type_A, type_A, type_A, type_A, type_C]

class Joint(object):

    def __init__(self, type, types, start_frame):

        # setting the numerical variables
        print type
        print types[type]
        self.type = type
        self.ang_bottom, self.ang_top_b, self.ang_top_a, self.spacing, self.overlap, self.t_or_b, self.relation, self.h, self.w = types[type]
        self.prev_frame = start_frame

        print self.ang_bottom, self.ang_top_b, self.ang_top_a, self.spacing, self.overlap, self.t_or_b, self.relation, self.h, self.w

        self.h_interval = rg.Interval(- self.h * .5, self.h * .5)
        self.w_interval = rg.Interval(- self.w * .5, self.w * .5)

        if (self.ang_bottom < .001):
            self.one_beam_bottom = True
        else:
            self.one_beam_bottom = False

        self.relations()
        self.generate_base_frames()
        self.positioning()
        self.box_rep()

    def generate_base_frames(self):
        xy_plane = rg.Plane.WorldXY

        if (self.one_beam_bottom):
            # main_beam

            main_beam_frame = rg.Plane(xy_plane)
            main_beam_length = (self.spacing + self.overlap) * 2.0
            main_beam_location = rg.Vector3d(self.spacing, 0, 0)
            main_beam_translate = rg.Transform.Translation(main_beam_location)
            main_beam_frame.Transform(main_beam_translate)
            main_beam = [main_beam_frame, main_beam_length]

            # top_beam

            top_beam_frame = rg.Plane(xy_plane)
            top_beam_length = self.spacing + self.overlap

            top_beam_pt_0_x = self.spacing * 1.5
            top_beam_pt_0 = rg.Vector3d(top_beam_pt_0_x, 0, self.h)
            top_beam_translation = rg.Transform.Translation(top_beam_pt_0)

            top_rotation_pt_a_x = self.spacing - self.overlap * .5
            top_rotation_pt_a = rg.Point3d(top_rotation_pt_a_x, 0, .5 * self.h)
            top_rotation_a_vec = rg.Vector3d(0, -1, 0)
            top_beam_rotation_a = rg.Transform.Rotation(self.ang_top_a, top_rotation_a_vec, top_rotation_pt_a)

            top_rotation_pt_b_x = self.spacing
            top_rotation_pt_b = rg.Point3d(top_rotation_pt_b_x, 0, .5 * self.h)
            top_rotation_b_vec = rg.Vector3d(0, 0, 1)
            top_beam_rotation_b = rg.Transform.Rotation(self.ang_top_b, top_rotation_b_vec, top_rotation_pt_b)

            top_beam_frame.Transform(top_beam_translation)
            top_beam_frame.Transform(top_beam_rotation_a)
            top_beam_frame.Transform(top_beam_rotation_b)
            top_beam = [top_beam_frame, top_beam_length]

            # end_frames

            # bottom_end_frame

            bottom_end_frame = rg.Plane(xy_plane)
            bottom_end_frame_location = rg.Vector3d(2 * self.spacing, 0, 0)
            bottom_end_frame_transformation = rg.Transform.Translation(bottom_end_frame_location)
            bottom_end_frame.Transform(bottom_end_frame_transformation)

            self.bottom_end_frame = bottom_end_frame

            # top_end_frame

            top_end_frame = rg.Plane(xy_plane)
            top_end_frame_location_x = self.spacing * 2.0 - self.overlap * .5
            top_end_frame_location = rg.Vector3d(top_end_frame_location_x, 0, self.h)
            top_end_frame_translation = rg.Transform.Translation(top_end_frame_location)
            top_end_frame.Transform(top_end_frame_translation)
            top_end_frame.Transform(top_beam_rotation_a)
            top_end_frame.Transform(top_beam_rotation_b)

            self.top_end_frame = top_end_frame

            beams = [main_beam, top_beam]

        else:

            # main_beam

            main_beam_frame = rg.Plane(xy_plane)
            main_beam_length = self.spacing + self.overlap * 2.0
            main_beam_location = rg.Vector3d(self.spacing * .5, 0, 0)
            main_beam_translate = rg.Transform.Translation(main_beam_location)
            main_beam_frame.Transform(main_beam_translate)
            main_beam = [main_beam_frame, main_beam_length]

            # bottom_beam

            if self.t_or_b:
                h_bottom = self.h
                h_top = self.h * 2
            else:
                h_bottom = -self.h
                h_top = self.h

            bottom_beam_frame = rg.Plane(xy_plane)
            bottom_beam_length = self.spacing + self.overlap * 2

            bottom_beam_pt_0_x = self.spacing * 1.5
            bottom_beam_pt_0 = rg.Vector3d(bottom_beam_pt_0_x, 0, h_bottom)
            bottom_beam_translation = rg.Transform.Translation(bottom_beam_pt_0)

            bottom_rotation_pt_x = self.spacing
            bottom_rotation_pt = rg.Point3d(bottom_rotation_pt_x, 0, .5 * h_bottom)
            bottom_rotation_vec = rg.Vector3d(0, 0, 1)
            bottom_beam_rotation = rg.Transform.Rotation(self.ang_bottom, bottom_rotation_vec, bottom_rotation_pt)

            bottom_beam_frame.Transform(bottom_beam_translation)
            bottom_beam_frame.Transform(bottom_beam_rotation)
            bottom_beam = [bottom_beam_frame, bottom_beam_length]

            # top_beam

            top_beam_frame = rg.Plane(xy_plane)
            top_beam_length = self.spacing + self.overlap

            top_beam_pt_0_x = self.spacing * 1.5
            top_beam_pt_0 = rg.Vector3d(top_beam_pt_0_x, 0, h_top)
            top_beam_translation = rg.Transform.Translation(top_beam_pt_0)

            top_rotation_pt_a_x = self.spacing - self.overlap * .5
            top_rotation_pt_a = rg.Point3d(top_rotation_pt_a_x, 0, .5 * h_top)
            top_rotation_a_vec = rg.Vector3d(0, -1, 0)
            top_beam_rotation_a = rg.Transform.Rotation(self.ang_top_a, top_rotation_a_vec, top_rotation_pt_a)

            top_rotation_pt_b_x = self.spacing
            top_rotation_pt_b = rg.Point3d(top_rotation_pt_b_x, 0, .5 * h_top)
            top_rotation_b_vec = rg.Vector3d(0, 0, 1)
            top_beam_rotation_b = rg.Transform.Rotation(self.ang_top_b, top_rotation_b_vec, top_rotation_pt_b)

            top_beam_frame.Transform(top_beam_translation)
            top_beam_frame.Transform(top_beam_rotation_a)
            top_beam_frame.Transform(top_beam_rotation_b)
            top_beam = [top_beam_frame, top_beam_length]

            # end_frames

            # bottom_end_frame

            bottom_end_frame = rg.Plane(xy_plane)
            bottom_end_frame_location = rg.Vector3d(2 * self.spacing, 0, 0)
            bottom_end_frame_translation = rg.Transform.Translation(bottom_end_frame_location)
            bottom_end_frame.Transform(bottom_end_frame_translation)
            bottom_end_frame.Transform(bottom_beam_rotation)

            self.bottom_end_frame = bottom_end_frame

            # top_end_frame

            top_end_frame = rg.Plane(xy_plane)
            top_end_frame_location_x = self.spacing * 2.0 - self.overlap * .5
            top_end_frame_location = rg.Vector3d(top_end_frame_location_x, 0, self.h)
            top_end_frame_translation = rg.Transform.Translation(top_end_frame_location)
            top_end_frame.Transform(top_end_frame_translation)
            top_end_frame.Transform(top_beam_rotation_a)
            top_end_frame.Transform(top_beam_rotation_b)

            self.top_end_frame = top_end_frame

            beams = [main_beam, bottom_beam, top_beam]

        self.beams = beams

    def relations(self):
        world_xy = rg.Plane.WorldXY

        if (self.relation == 1):

            # trans_vector = rg.Vector3d(self.prev_frame.Normal) * - self.h
            # move_trans = rg.Transform.Translation(trans_vector)
            self.base_frame = rg.Plane(self.prev_frame)
            # self.base_frame.Transform(move_trans)

            self.base_frame_trans = rg.Transform.PlaneToPlane(world_xy, self.base_frame)

        elif (self.relation == 2):

            # trans_vector = rg.Vector3d(self.prev_frame.Normal) * - self.h
            # move_trans = rg.Transform.Translation(trans_vector)
            self.base_frame = rg.Plane(self.prev_frame)
            # self.base_frame.Transform(move_trans)
            origin = self.base_frame.Origin
            x_axis = self.base_frame.XAxis
            y_axis = self.base_frame.YAxis
            self.base_frame = rg.Plane(origin, x_axis, -y_axis)

            self.base_frame_trans = rg.Transform.PlaneToPlane(world_xy, self.base_frame)

        elif (self.relation == 3):

            # trans_vector = rg.Vector3d(self.prev_frame.Normal) * self.h
            # move_trans = rg.Transform.Translation(trans_vector)
            self.base_frame = rg.Plane(self.prev_frame)
            # self.base_frame.Transform(move_trans)
            origin = self.base_frame.Origin
            x_axis = self.base_frame.XAxis
            y_axis = self.base_frame.YAxis
            self.base_frame = rg.Plane(origin, x_axis, -y_axis)

            self.base_frame_trans = rg.Transform.PlaneToPlane(world_xy, self.base_frame)

        else:
            # if no relation value set, reverts to if self.relation == 0:
            # trans_vector = rg.Vector3d(self.prev_frame.Normal) * self.h
            # move_trans = rg.Transform.Translation(trans_vector)
            self.base_frame = rg.Plane(self.prev_frame)
            # self.base_frame.Transform(move_trans)

            self.base_frame_trans = rg.Transform.PlaneToPlane(world_xy, self.base_frame)

    def positioning(self):

        for beam in self.beams:
            beam[0].Transform(self.base_frame_trans)

        self.top_end_frame.Transform(self.base_frame_trans)
        self.bottom_end_frame.Transform(self.base_frame_trans)

    def box_rep(self):
        self.beam_boxes = []
        for beam in self.beams:
            plane, length = beam
            l_interval = rg.Interval(- length * .5, length * .5)
            local_box = rg.Box(plane, l_interval, self.w_interval, self.h_interval)
            self.beam_boxes.append(local_box)


# l-system logic

# setting up some pattern

pattern_map = [[0, 1, 2, 3, 4, 5], [[0, 1], [0, 2], [3], [4], [5], []]]
pattern_variaties = len(pattern_map[0])

print pattern_variaties

# starting positions

seed = [0]
frame = [rg.Plane.WorldZX]
Joints = [Joint(seed[0], types, frame[0])]

Joint_list = [Joints]

# going through the loop and appending to the system

if iteration_count > 12:
    iteration_count = 12

for i in range (1, iteration_count, 1):
    new_Joint_list = []
    for joint in Joint_list[i - 1]:
        special = False
        killed = False
        for k in range(pattern_variaties):
            if (joint.type == k):
                print k
                if (len(pattern_map[1][k]) == 2):
                    type_1, type_2 = pattern_map[1][k]
                    break
                elif (len(pattern_map[1][k]) == 1):
                    type_1 = pattern_map[1][k][0]
                    special = True
                    break
                else:
                    killed = True
        if special:
            fr_1 = joint.top_end_frame
            joint_1 = Joint(type_1, types, fr_1)
            new_Joint_list.append(joint_1)
        elif killed:
            pass

        else:
            fr_1, fr_2 = joint.bottom_end_frame, joint.top_end_frame
            joint_1, joint_2 = Joint(type_1, types, fr_1), Joint(type_2, types, fr_2)
            new_Joint_list.append(joint_1)
            new_Joint_list.append(joint_2)
    Joint_list.append(new_Joint_list)

brep = []
for Joints in Joint_list:
    for joint in Joints:
        for beam in joint.beam_boxes:
            brep.append(beam)
