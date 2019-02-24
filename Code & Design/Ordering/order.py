# python code to order a set of random rectangles

# generating the rectangle set

import random as r
import math as m

class point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.solved = False

    def get_distance_to(self, pt):
        dis = m.sqrt((self.x - pt.x) ** 2 + (self.y - pt.y) ** 2)
        return dis

class rectangle(object):
    def __init__(self, base_pt, index_value = [0, 0], treshold = .1):
        self.treshhold = treshold
        self.solved = False
        self.index_value = index_value

        x_list = [0, 1, 1]
        y_list = [1, 1, 0]
        self.pt_list = [point(base_pt.x, base_pt.y)]
        for i in range(3):
            x_val = base_pt.x + x_list[i]
            y_val = base_pt.y + y_list[i]
            self.pt_list.append(point(x_val, y_val))

    def get_pts_with_indexes(self, indexes):
        output_points = [self.pt_list[index] for index in indexes]
        return output_points

    def random_pt_shuffle(self):
        reverse_or_not = bool(r.getrandbits(1))
        shift_list = r.randint(0, 3)
        if reverse_or_not:
            self.pt_list.reverse()
        temp_pts = self.pt_list[:]
        self.pt_list = []
        [self.pt_list.append(temp_pts[(i + shift_list) % 4]) for i in range(4)]

    def set_solved(self):
        self.solved = True

    def set_solved_for_pts_indexes(self, indexes):
        self.solved = True
        for index in indexes:
            self.pt_list[index].solved = True

    def set_unsolved_for_pts_indexes(self, indexes):
        for index in indexes:
            self.pt_list[index].solved = True

    def set_all_solved(self):
        self.solved = True
        for pt in self.pt_list:
            pt.solved = True

    def set_unsolved(self):
        self.solved = False
        for pt in self.pt_list:
            pt.solved = False

    def get_distances_to_pt(self, pt):
        output = False
        contact_index = None
        for i, corner_pt in enumerate(self.pt_list):
            if (corner_pt.get_distance_to(pt) < self.treshhold):
                output = True
                contact_index = i
                break

        return output, contact_index

    def get_overlap_count_with_pts(self, pts):
        overlaps = 0
        contact_list = []
        for pt in pts:
            contact_qm, contact_index = self.get_distances_to_pt(pt)
            if (contact_qm):
                overlaps += 1
                contact_list.append(contact_index)

        # print "get overlap", contact_list
        return overlaps, contact_list

    def get_overlap_count_with_unsolved_pts_rec(self, other_rec):
        working_pt_set = []
        local_index_list = []
        for index, corner_pt in enumerate(other_rec.pt_list):
            if not(corner_pt.solved):
                working_pt_set.append(corner_pt)
                local_index_list.append(index)
        # print "unsolved get overlap", local_index_list

        return self.get_overlap_count_with_pts(working_pt_set)

    def get_solved_indexes(self):
        solved_index = []
        for i, pt in enumerate(self.pt_list):
            if (pt.solved):
                solved_index.append(i)

        return solved_index

    def get_unsolved_indexes(self):
        unsolved_index = []
        for i, pt in enumerate(self.pt_list):
            if not(pt.solved):
                unsolved_index.append(i)

        return unsolved_index

    def get_unsolved_points(self):
        unsolved_pts = [self.pt_list[i] for i in self.get_unsolved_indexes()]
        return unsolved_pts

class surface_ordering(object):
    def __init__(self, srfs, treshhold = .1):
        self.srfs = srfs
        self.srf_count = len(srfs)
        self.treshhold = treshhold
        self.dir_loop = [False, False]

        self.get_to_sides()
        self.organise()

    def check_amount_of_contact_pts(self, rec0, rec1):
        contact_values = 0
        contact_list = []
        for i, pt in enumerate(rec0.pt_list):
            if(rec1.get_distance_to_pt(pt)):
                contact_values += 1
                contact_list.append(i)
        return contact_values, contact_list

    def side_loop(self, work_surface_index, dir = 0, start_srf_index = 0, start_srf_i_values = [0, 1]):
        self.reached_side = True
        for srf_index, srf in enumerate(self.srfs):
            # print "statement 1 - srf_index:", srf_index, " srf_solve : ", srf.solved
            if not(srf.solved):
                overlap_count, contact_index_list = srf.get_overlap_count_with_unsolved_pts_rec(self.srfs[work_surface_index])
                # print overlap_count
                if (overlap_count == 2):
                    print "statement 2 - overlap count:", overlap_count, " rec_index : ", self.srfs[work_surface_index].index_value
                    self.srfs[work_surface_index].set_all_solved()
                    self.srfs[srf_index].set_solved_for_pts_indexes(contact_index_list)
                    self.reached_side = False
                    break
        if self.reached_side:
            print "you've reached an end!", " rec_index : ", self.srfs[work_surface_index].index_value
            print "this was the start index: ", start_srf_index, " - this was the end index: ", work_surface_index
            # checking for overlap with the first one
            overlap_count, contact_index_list = self.srfs[start_srf_index].get_overlap_count_with_pts(self.srfs[0].get_pts_with_indexes(start_srf_i_values))
            if (overlap_count == 2):
                print "this one loops"
                self.dir_loop[dir] = True
            srf_index = work_surface_index
        return srf_index

    def get_to_sides(self):
        # direction 1
        work_surface_index = 0
        start_surface_location = work_surface_index
        new_srf_i_values = [2, 3]
        self.srfs[work_surface_index].set_solved_for_pts_indexes(new_srf_i_values)

        self.reached_side = False
        while not(self.reached_side):
            old_work_surface_index = work_surface_index
            work_surface_index = self.side_loop(work_surface_index, 0, start_surface_location, new_srf_i_values)

        last_srf_i_values = self.srfs[work_surface_index].get_solved_indexes()
        start_surface_location = work_surface_index

        # direction 2
        new_srf_i_values = [(index - 1) % 4 for index in last_srf_i_values]
        print last_srf_i_values, new_srf_i_values
        self.set_unsolved()
        self.srfs[work_surface_index].set_solved_for_pts_indexes(new_srf_i_values)

        self.reached_side = False
        while not(self.reached_side):
            old_work_surface_index = work_surface_index
            work_surface_index = self.side_loop(work_surface_index, 1, start_surface_location, new_srf_i_values)

        # setting up the loops for the surface organising
        last_srf_i_values = self.srfs[work_surface_index].get_solved_indexes()
        self.dir_0_index = [(index - 1) % 4 for index in last_srf_i_values]
        self.corner_srf_index = work_surface_index
        self.set_unsolved()

    def organise(self):
        # start value
        new_srf_i_values = self.dir_0_index
        work_surface_index = self.corner_srf_index
        start_surface_location = work_surface_index
        while not(self.reached_side):
            pass

    def set_unsolved(self):
        [srf.set_unsolved() for srf in self.srfs]

x_count = 6
y_count = 5

rec_list = []

for i in range(x_count):
    # regular rectangles
    print "i : ", i
    for j in range(y_count):
        rec_list.append(rectangle(point(i*1.0, j*1.0), [i, j]))
        print "   j : ", j
    # loop back rectangles
    print "extra_rec"
    local_loop_rec = rectangle(point(0, 0), [i, y_count])
    pt_0 = point(i * 1.0, y_count * 1.0)
    pt_1 = point(i * 1.0 + 1.0, y_count * 1.0)
    pt_2 = point(i * 1.0 + 1.0, 0.0)
    pt_3 = point(i * 1.0, 0.0)
    local_loop_rec.pt_list = [pt_0, pt_1, pt_2, pt_3]
    rec_list.append(local_loop_rec)

print len(rec_list)
print "source:"

for i in range(len(rec_list)):
    print "rec", rec_list[i].index_value, ": ",
    for j in range(4):
        print rec_list[i].pt_list[j].x, rec_list[i].pt_list[j].y, ", ",
    print "\n"

# print "points shuffled:"

for i in range(len(rec_list)):
    # print "rec", rec_list[i].index_value, ": ",
    rec_list[i].random_pt_shuffle()
    # for j in range(4):
        # print rec_list[i].pt_list[j].x, rec_list[i].pt_list[j].y, ", ",
    # print "\n"

print "rectangles shuffled:"

r.shuffle(rec_list)

for i in range(x_count * y_count):
    print "rec", i, " - ", rec_list[i].index_value, ": ",
    for j in range(4):
        print rec_list[i].pt_list[j].x, rec_list[i].pt_list[j].y, ", ",
    print "\n"

surface_group = surface_ordering(rec_list)
