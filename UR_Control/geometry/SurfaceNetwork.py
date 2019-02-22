"""Provides a scripting component.
    Inputs:
        x: The x script variable
        y: The y script variable
    Output:
        a: The a output variable"""

__author__ = "ytakzk"
__version__ = "2019.02.18"

import sys
import random
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import copy

path_to_append = single_parent
sys.path.append(path_to_append)

print path_to_append

# import geometry.beam as Beam
from geometry.joint_holes import JointHoles
from geometry.beam import Beam

tmp = []

# definition of U and V
class Direction(object):

    def __init__(self, direction):

        self.direction = direction

U = Direction('u')
V = Direction('v')

# definition of U0, U1, V0, V1 as the edges of surfaces
class Edge(object):

    def __init__(self, direction, value):

        self.direction = direction
        self.value = value

U0 = Edge(U, 0)
U1 = Edge(U, 1)
V0 = Edge(V, 0)
V1 = Edge(V, 1)

# definition of the edge between two surfaces to store how they are linked each other
class SharedEdge(object):

    def __init__(self, surface_1, surface_2, edge_1, edge_2):

        self.surface_1 = surface_1
        self.surface_2 = surface_2
        self.edge_1 = edge_1
        self.edge_2 = edge_2

    def get_beams(self):

        return self.__get_beams(self.surface_1, self.edge_1), \
               self.__get_beams(self.surface_2, self.edge_2)

    def __get_beams(self, surface, edge):


        if edge == V0:
            return surface.beams[0]
        elif edge == V1:
            return surface.beams[-1]
        elif edge == U0:
            return [b[0] for b in surface.beams]
        elif edge == U1:
            return [b[-1] for b in surface.beams]
        else:
            ValueError('edge direction is not a correct value')

# definition of division
class Division(object):

    def __init__(self):

        self.id = id(self)
        self.num = 0
        self.shared_edges = []

    def add_shared_edge(self, shared_edge):

        self.shared_edges.append(shared_edge)
        self.shared_edges = list(set(self.shared_edges))

    def determine_num(self):

        u_num, v_num = 0, 0

        for e in self.shared_edges:

            if e.edge_1.direction == U:

                u_num += 1

            else:

                v_num += 1

        # must be an odd number?
        self.num = 3 if u_num < v_num else 7

class Network(object):

    @staticmethod
    def get_relation(s1, s2):

        # get how two surfaces are linked

        domain = rg.Interval(0, 1)
        s1.SetDomain(0, domain)
        s1.SetDomain(1, domain)
        s2.SetDomain(0, domain)
        s2.SetDomain(1, domain)

        p1_1 = s1.IsoCurve(0, 0).PointAt(0.5) # bottom
        p1_2 = s1.IsoCurve(0, 1).PointAt(0.5) # top
        p1_3 = s1.IsoCurve(1, 0).PointAt(0.5) # left
        p1_4 = s1.IsoCurve(1, 1).PointAt(0.5) # right

        p2_1 = s2.IsoCurve(0, 0).PointAt(0.5) # bottom
        p2_2 = s2.IsoCurve(0, 1).PointAt(0.5) # top
        p2_3 = s2.IsoCurve(1, 0).PointAt(0.5) # left
        p2_4 = s2.IsoCurve(1, 1).PointAt(0.5) # top

        THRESHOLD_DIST = 1

        for loc_1, p1 in zip([V0, V1, U0, U1], [p1_1, p1_2, p1_3, p1_4]):

            for loc_2, p2 in zip([V0, V1, U0, U1], [p2_1, p2_2, p2_3, p2_4]):

                if p1.DistanceTo(p2) < THRESHOLD_DIST:

                    return loc_1, loc_2

        return None

    def __init__(self, surfaces):

        self.surfaces = [Surface(s) for s in surfaces]

        # find the shared edges
        shared_edges = []
        for i, s1 in enumerate(self.surfaces):

            for j, s2 in enumerate(self.surfaces):

                if s1 == s2:
                    continue

                rel = Network.get_relation(s1.surface, s2.surface)
                if rel:

                    edge1 = rel[0]
                    edge2 = rel[1]

                    shared_edge = SharedEdge(s1, s2, edge1, edge2)
                    s1.shared_edges.append(shared_edge)
                    s2.shared_edges.append(shared_edge)
                    shared_edges.append(shared_edge)

        self.shared_edges = shared_edges

        # find a set of surfaces to have the same division class
        self.divisions = []

        for _ in range(3): # we don't need this outmost for-loop if the surfaces are well-ordered

            # TODO: the better solution can be found but anyway it works

            for e in self.shared_edges:

                div_1 = e.surface_1.u_div if e.edge_1.direction == U else e.surface_1.v_div

                if e.edge_2.direction == U:

                    e.surface_2.u_div = div_1
                    e.surface_2.u_div.add_shared_edge(e)
                    self.divisions.append(e.surface_2.u_div)

                else:

                    e.surface_2.v_div = div_1
                    e.surface_2.v_div.add_shared_edge(e)
                    self.divisions.append(e.surface_2.v_div)

        self.divisions = list(set(self.divisions))

        # determine the division number
        for d in self.divisions:
            d.determine_num()

    def sew(self):

        for edge in self.shared_edges:

            beams_1, beams_2 = edge.get_beams()

            # connect edges between surfaces by dowels
            # Use Jonas's Joint class?

            tmp.extend([b.brep_representation() for b in beams_1])

class Surface(object):

    def __init__(self, surface):

        self.surface = surface
        self.u_div = Division()
        self.v_div = Division()
        self.shared_edges = []

        self.beams = [] # nested array according to u-v mapping

    def instantiate_beams(self):

        self.beams = []

        surface = self.__offset_sides_surface(50)

        for u in range(self.u_div.num):

            inner_arr = []

            for v in range(self.v_div.num + 1):

                if (u % 2 == 0 and v % 2 == 1) or (u % 2 == 1 and v % 2 == 0):
                    continue

                p1 = surface.PointAt(u/self.u_div.num, v/self.v_div.num)
                p2 = surface.PointAt(u/self.u_div.num, (v+1)/self.v_div.num)

                length = p1.DistanceTo(p2)

                center = rg.Point3d((p1 + p2) / 2)

                _, uu, vv = surface.ClosestPoint(center)

                normal = surface.NormalAt(uu, vv)
                x_axis = rg.Vector3d(p1) - rg.Vector3d(p2)
                y_axis = rg.Vector3d.CrossProduct(normal, x_axis)

                plane = rg.Plane(center, x_axis, normal)

                beam = Beam(plane, length, 25, 5)

                inner_arr.append(beam)

            self.beams.append(inner_arr)

    def joint_generation(self, beam_set, location_set, type = 0):
        pass

    def joint_type(self, type = 0):
        if type == 0:
            pass


    def add_dowels(self):

        """
            * extend the edges of beams
            * add dowels that go through three beams in the same surface
            * use Jonas's joint class?
        """

        self.beams

        pass

    def get_flatten_beams(self):

        return list(chain.from_iterable(self.beams))

    def __offset_sides_surface(self, offset_dis=20):
        """ method that returns a slightly shrunk version of the surface along the v direction
            :param offset_dis:       Offset Distance (default 20)
            :return temp_srf:   The trimmed surface
        """
        sampling_count = 25

        temp_surface = copy.deepcopy(self.surface)

        temp_surface.SetDomain(1, rg.Interval(0, sampling_count - 1))
        temp_isocurves = [temp_surface.IsoCurve(0, v_val) for v_val in range(sampling_count)]

        temp_isocurves_shortened = []

        for isocurve in temp_isocurves:
            # getting the length and the domain of every isocurve
            length = isocurve.GetLength()
            start_t, end_t = isocurve.Domain[0], isocurve.Domain[1]
            t_delta = end_t - start_t
            t_differential = t_delta / length
            # calculating how much the offset_dis result in t_val change
            t_shift = t_differential * offset_dis
            start_t_new = start_t + t_shift
            end_t_new = end_t - t_shift
            # splitting the curve at those two new start & end points with and taking the middle piece
            new_isocurve = isocurve.Split([start_t_new, end_t_new])[1]
            temp_isocurves_shortened.append(new_isocurve)

        # switching the uv direction back to where it should be! -> rebuilding the surface
        point_list = [[] for i in range(sampling_count)]
        for temp_curve in temp_isocurves_shortened:
            length = temp_curve.GetLength()
            start_t, end_t = temp_curve.Domain[0], temp_curve.Domain[1]
            t_delta = end_t - start_t
            t_differential = t_delta / (sampling_count - 1)
            # calculating how much the offset_dis result in t_val change
            point_set = [temp_curve.PointAt(t_val * t_differential + start_t) for t_val in range(0, sampling_count, 1)]
            for i, point in enumerate(point_set):
                point_list[i].append(rg.Point3d(point))

        uv_switched_curves = []
        for point_set in point_list:
            local_isocurve = rg.NurbsCurve.Create(False, 3, point_set)
            uv_switched_curves.append(local_isocurve)

        # lofting those isocurves
        loft_type = rg.LoftType.Tight
        s = rg.Brep.CreateFromLoftRebuild(uv_switched_curves, rg.Point3d.Unset, rg.Point3d.Unset, loft_type, False, 50)[0]
        # getting the loft as a nurbssurface out of the resulting brep
        s = s.Faces.Item[0].ToNurbsSurface()

        domain = rg.Interval(0, 1)
        s.SetDomain(0, domain)
        s.SetDomain(1, domain)

        return s


# debug
random.shuffle(surfaces)

# create a network from surfaces
network = Network(surfaces)

# labels of divisions
label = []
label_pos = []
for s in network.surfaces:
    string = 'u%d\nv:%d' % (s.u_div.id, s.v_div.id)
    label.append(string)
    label_pos.append(s.surface.PointAt(0.5, 0.5))

beams = []

# entire workflow
for s in network.surfaces:

    # instantiate beams
    s.instantiate_beams()

    # add dowels to the beams in the surface (not for sewing)
    s.add_dowels() # joint class must be applied inside

    # visualization
    beams.extend([b.brep_representation(make_holes=False) for b in s.get_flatten_beams()])

# add dowels to connect contact surfaces
network.sew() # joint class must be applied inside

# consider keystones
