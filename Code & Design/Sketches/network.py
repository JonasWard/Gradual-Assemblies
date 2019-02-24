#
# Basic classes for MAS-DFAB 2018-19 T2 GKR Project
#

__author__ = "masdfab students"
__status__ = "development"
__version__ = "0.0.1"
__date__    = "15 January 2019"

import Rhino.Geometry as rg
import Grasshopper.Kernel.Data.GH_Path as ghpath
import Grasshopper.DataTree as datatree

import rhinoscriptsyntax as rs
import clr
clr.AddReference("Grasshopper")

import System
import math

temp_geom = []

normal_beams = datatree[System.Object]()
shifted_beams = datatree[System.Object]()

for path in normal_list.Paths:
    for plane in normal_list.Branch(path):

        plane.Rotate(beam_rotation * math.pi / 180, plane.YAxis, plane.Origin)

        beam = Beam(plane, dx, dy, dz)
        normal_beams.Add(beam, path)

for path in shifted_list.Paths:
    for plane in shifted_list.Branch(path):

        plane.Rotate(beam_rotation * math.pi / 180, plane.YAxis, plane.Origin)

        beam = Beam(plane, dx, dy, dz)
        shifted_beams.Add(beam, path)

def get_dowel(beam, line_1, line_2):

    succeeded, p1, p2 = line_1.ClosestPoints(line_2)

    if succeeded:

        normal = rg.Vector3d.Subtract(rg.Vector3d(p2), rg.Vector3d(p1))

        plane = rg.Plane(p1, normal)
        temp_geom.append(plane)
        temp_geom.append(p1)
        temp_geom.append(p2)
        return Dowel(plane, dowel_radius=radius)

    else:

        return None

n_list = shifted_beams

for branch_index, beams in enumerate(normal_beams.Branches):

    for list_index, beam in enumerate(beams):

        """
        normal beams
        """

        has_hole = False

        if list_index >= 1:

            other_beam = beams[list_index - 1]
            line_1 = beam.get_baseline().ToNurbsCurve()
            line_2 = other_beam.get_baseline().ToNurbsCurve()
            has_hole = True

        if list_index < len(beams) - 1:

            other_beam = beams[list_index + 1]
            line_1 = beam.get_baseline().ToNurbsCurve()
            line_2 = other_beam.get_baseline().ToNurbsCurve()
            has_hole = True

        if has_hole:

            dowel = get_dowel(beam, line_1, line_2)
            if dowel:
                beam.add_dowel(dowel)
                other_beam.add_dowel(dowel)
                temp_geom.append(dowel.base_plane)

        """
        shifted beams
        """

        tmp_shifted_beams = shifted_beams.Branches[branch_index]

        if list_index >= 1:

            shifted_beam = tmp_shifted_beams[list_index - 1]

            line_1 = beam.get_baseline().ToNurbsCurve()
            line_2 = shifted_beam.get_baseline().ToNurbsCurve()

            dowel = get_dowel(beam, line_1, line_2)
            if dowel:
                beam.add_dowel(dowel)
                shifted_beam.add_dowel(dowel)
                temp_geom.append(dowel.base_plane)

        if list_index < len(tmp_shifted_beams):

            shifted_beam = tmp_shifted_beams[list_index]

            line_1 = beam.get_baseline().ToNurbsCurve()
            line_2 = shifted_beam.get_baseline().ToNurbsCurve()

            dowel = get_dowel(beam, line_1, line_2)
            if dowel:
                beam.add_dowel(dowel)
                shifted_beam.add_dowel(dowel)
                temp_geom.append(dowel.base_plane)


for branch_index, beams in enumerate(shifted_beams.Branches):

    for list_index, beam in enumerate(beams):

        """
        shifted beams
        """

        if list_index > 1:

            other_beam = beams[list_index - 1]
            line_1 = beam.get_baseline().ToNurbsCurve()
            line_2 = other_beam.get_baseline().ToNurbsCurve()

        elif list_index < len(beams) - 1:

            other_beam = beams[list_index + 1]
            line_1 = beam.get_baseline().ToNurbsCurve()
            line_2 = other_beam.get_baseline().ToNurbsCurve()

        else:

            continue

        dowel = get_dowel(beam, line_1, line_2)
        if dowel:
            beam.add_dowel(dowel)
            other_beam.add_dowel(dowel)
            temp_geom.append(dowel.base_plane)

for path in normal_beams.Paths:
    for beam in normal_beams.Branch(path):
        beam.remove_duplicates_in_dowel_list()
        temp_geom.append(beam.brep_representation())

for path in shifted_beams.Paths:
    for beam in shifted_beams.Branch(path):
        beam.remove_duplicates_in_dowel_list()
        temp_geom.append(beam.brep_representation())
