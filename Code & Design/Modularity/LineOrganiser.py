# line organiser

import Rhino.Geometry as rg

# grasshopper inputs

lines

# interpreting
count = len(lines)
pt_0_add, pt_1_add = False, False

# setting up a little class

class Line(object):


    """docstring for Line."""
    def __init__(self, line):
        self.end_solved = False
        self.start_solved = False
        self.end = line.PointAt(0.0)
        self.start = line.PointAt(1.0)

    def set_solved_start(self):
        self.start_solved = True

    def set_solved_end(self):
        self.end_solved = True

class Joint(object):

    def __init__(self, point, line_0, line_1, line_2):
        self.end_solved = False
        self.start_solver = False
        self.end = line.PointAt(0.0)
        self.start = line.PointAt(1.0)

pt_list = []
ClassedLines = []
for line in lines:
    line_class = Line(line)
    ClassedLines.append(line_class)

    pt_0 = rg.Point3d(line_class.end)
    pt_1 = rg.Point3d(line_class.start)

    if not (len(pt_list) == 0):
        for pt in pt_list:
            if (pt_0 == pt):
                pt_0_add = False
                break
            else:
                pt_0_add = True

            if (pt_1 == pt):
                pt_1_add = False
                break
            else:
                pt_1_add = True
    else:
        pt_0_add = True
        pt_1_add = True

    if pt_0_add:
        pt_list.append(pt_0)
    if pt_1_add:
        pt_list.append(pt_1)

print len (ClassedLines)
Joints = []
for pt in pt_list:
    lines = []

    for Line in ClassedLines:
        if not(Line.start_solved):
            if ( pt == Line.start):
                print "goal"
                lines.append(Line)
                Line.set_solved_start

        if not(Line.end_solved):

            if ( pt == Line.end):
                print "zicher"
                lines.append(Line)
                Line.set_solved_end

    local_Joint = Joint(pt, lines[0], lines[1], lines[2])
    Joints.append(local_Joint)
