__author__ = "Wenqian"
__version__ = "2019.02.03"

# grasshopper variabels

seam_crvs
edge_crvs
u_count
v_count
rebuild_srf
beam_shift
curvature_factor_u
curvature_factor_v
offset_x
offset_y

import Rhino.Geometry as rg
# import scriptcontext as sc
# import math as m
# import rhinoscriptsyntax as rs
import copy

u_count
v_count

class BeamNet(object):
    """
    generate beam crvs from a srf
    """
    def __init__(self,srf,rebuild_srf,beam_shift,curvature_factor_u,curvature_factor_v,offset_x,offset_y,seam_crv,seam_side,edge_side):
        """
        Attributes:
        srf
        """
        self.srf = srf
        self.c_factor_u = curvature_factor_u*1000
        self.c_factor_v = curvature_factor_v*10000
        self.u_shift = beam_shift
        self.offset_x = offset_x
        self.offset_y = offset_y

        # get beams
        self.u_crvs = []
        self.v_crvs = []
        self.beam_crvs = []#nested
        self.beam_planes = []#nested
        self.get_uv()
        self.u_crvs = self.redraw_u_crvs_based_on_curvature()#apply if want to adjust beam length due to curvature
        self.get_beam()

        # get dowels
        # specially deal with seam situation and edge situation
        self.seam_crv_temp = seam_crv #it's a list
        self.seam_side = seam_side #it's a list
        self.seam_flag = False
        self.seam_row_index = []
        self.seam_crv = []
        if len(self.seam_side) != 0:
            self.seam_flag = True
            for crv, side in zip(self.seam_crv_temp,self.seam_side):
                if side == 0:
                    self.seam_row_index.append(0)
                    self.seam_crv.append(crv)
                if side == 1:
                    self.seam_row_index.append(len(self.beam_crvs)-1)
                    self.seam_crv.append(crv)

        self.edge_side = edge_side #it's a list
        self.edge_flag = False
        self.edge_row_index = []
        if len(self.edge_side) != 0:
            self.edge_flag = True
            for side in self.edge_side:
                if side == 0:
                    self.edge_row_index.append(0)
                if side == 1:
                    self.edge_row_index.append(len(self.beam_crvs)-1)
        self.end_dowel_crvs = []#flattened
        self.get_triple_connections()
        if self.seam_flag:
            self.get_seam_connections()

    def get_uv(self):

        # get u_count
        total_length= 0
        for i in range(6):
            total_length += self.srf.IsoCurve(1, 0.2 * i).GetLength()
        self.u_count = u_count
        self.beam_length = total_length/6/u_count

        # get v_count
        total_length= 0
        for i in range(6):
            total_length += self.srf.IsoCurve(0, 0.2 * i).GetLength()
        self.v_count = v_count
        self.dowel_length = total_length/6/v_count

        # get v_crvs
        for v in range(self.v_count+1):
            v_crv = self.srf.IsoCurve(1,v/self.v_count)
            if rebuild_srf:
                v_crv = v_crv.Rebuild(50,3,True)
            self.v_crvs.append(v_crv)

        # get u_crvs
        for u in range(self.u_count+1):
            u_crv = self.srf.IsoCurve(0,u/self.u_count)
            if rebuild_srf:
                u_crv = u_crv.Rebuild(50,3,True)
            self.u_crvs.append(u_crv)

    def regrading(self, crvs, count,factor):
        #regrading crvs based on curvature
        crvs_new_params = []#nested
        current_points_nested = []#nested
        for curves in crvs:
            curve_domain = curves.Domain
            curve_domain_length = curve_domain[1] - curve_domain[0]

            range_value = curve_domain_length /count
            domain_list = []
            temp_vector_length_list = []
            for i in range (count + 1):
                local_t = i * range_value
                domain_list.append(local_t)
                local_curvature_vec = rg.Vector3d(curves.CurvatureAt(local_t))
                vector_length = local_curvature_vec.Length
                temp_vector_length_list.append(vector_length)


            temp_vector_length_partial_sums = []
            temp_point_list = []
            c = 0
            previous_value = 0
            for local_vec_l in (temp_vector_length_list):
                x_value = domain_list[c]
                y_value = previous_value * factor
                local_pt = rg.Point3d(x_value, y_value, 0)
                temp_point_list.append(local_pt)
                temp_vector_length_partial_sums.append(previous_value)
                previous_value += local_vec_l
                c += 1

            curvature_crv = rg.Curve.CreateControlPointCurve(temp_point_list, 10)
            temp_points_curvature_crv = curvature_crv.DivideByCount(count, True)
            t_vals = [curvature_crv.PointAt(pt).X for pt in temp_points_curvature_crv]
            current_points = [curves.PointAt(t_val) for t_val in t_vals]
            current_points_nested.append(current_points)
            crvs_new_params.append(t_vals)
        return crvs_new_params, current_points_nested

    def flip_matrix(self, nested_list):
        #flip data in a nested list
        flipped_nested_list = []
        for i in range(len(nested_list[0])):
            new_list = []
            for j in range(len(nested_list)):
                new_list.append(nested_list[j][i])
            flipped_nested_list.append(new_list)
        return flipped_nested_list

    def redraw_u_crvs_based_on_curvature(self):
        pts_on_v_crvs = self.regrading(self.v_crvs,self.u_count,self.c_factor_v)[1] #regrading beam length based on curvatur
        pts_on_u_crvs = self.flip_matrix(pts_on_v_crvs)
        u_crvs_redraw = []
        for pts in pts_on_u_crvs:
            new_u_crv = rg.Curve.CreateControlPointCurve(pts,10)
            u_crvs_redraw.append(new_u_crv.Rebuild(100,3,True))
        return u_crvs_redraw

    def get_plane(self,crv):
        #get planes for beam crvs
        center_pt = crv.PointAt(0.5)
        norm = self.srf.NormalAt(self.srf.ClosestPoint(center_pt)[1],self.srf.ClosestPoint(center_pt)[2])
        xDirection = crv.PointAt(1) - crv.PointAt(0)
        return rg.Plane(center_pt, xDirection,norm)

    def get_beam(self):
        #get beam crvs and planes on v crvs
        u_crvs_new_params = self.regrading(self.u_crvs,self.v_count,self.c_factor_u)[0] #regrading beam position based on curvature

        for c in range(self.u_count):
            line_start_params = u_crvs_new_params[c]
            line_end_params = u_crvs_new_params[c+1]
            beam_crvs = []
            beam_planes = []
            for i,p in enumerate(line_start_params[:-1]):
                line_start_pts=[]
                line_end_pts = []
                line_start_pt=self.u_crvs[c].PointAt(p+(line_start_params[i+1]-p)*self.u_shift*(c%2+1))
                line_end_pt=self.u_crvs[c+1].PointAt(p+(line_end_params[i+1]-p)*self.u_shift*(c%2+1))
                beam_crv = rg.Line(line_start_pt,line_end_pt)
                beam_crvs.append(beam_crv)
                beam_planes.append(self.get_plane(beam_crv))

            self.beam_crvs.append(beam_crvs)
            self.beam_planes.append(beam_planes)

    def get_rotate_connection_points(self,pt,plane):
        # generate 4 cross points around an anchor point on beam
        plane.XAxis.Unitize()
        plane.YAxis.Unitize()
        p0 = rg.Point3d.Add(pt,plane.YAxis*self.offset_y)
        p1 = rg.Point3d.Add(pt,plane.XAxis*self.offset_x)
        p2 = rg.Point3d.Add(pt,plane.YAxis*-self.offset_y)
        p3 = rg.Point3d.Add(pt,plane.XAxis*-self.offset_x)
        return p0,p1,p2,p3

    def get_a_single_dowel_end_connection(self, crv_top, plane_top, flag_top, crv_bottom, plane_bottom, flag_bottom):
        pts_top = self.get_rotate_connection_points(crv_top.PointAt(flag_top),plane_top)
        pts_down = self.get_rotate_connection_points(crv_bottom.PointAt(flag_bottom),plane_bottom)
        if flag_top == 1:
            return rg.Line(pts_top[3],pts_down[2])
        else:
            return rg.Line(pts_top[1],pts_down[0])

    def add_edge_dowel(self, top_crv, top_pln, top_flag, bottom_crv, bottom_pln, bottom_flag):
        # add an extra dowel if the beam is on a naked edge
        beam_top_flip = copy.deepcopy(top_crv)
        beam_top_flip.Flip()
        beam_top_flip = rg.Line(beam_top_flip.PointAtLength(30),beam_top_flip.PointAtLength(beam_top_flip.Length-30))
        beam_bottom_flip = copy.deepcopy(bottom_crv)
        beam_bottom_flip.Flip()
        beam_bottom_flip = rg.Line(beam_bottom_flip.PointAtLength(30),beam_bottom_flip.PointAtLength(beam_bottom_flip.Length-30))
        return self.get_a_single_dowel_end_connection(beam_top_flip,top_pln,top_flag,beam_bottom_flip,bottom_pln,bottom_flag)

    def get_triple_connections(self):
        j = 0
        for crvs,planes in zip(self.beam_crvs,self.beam_planes):
            # generate connections in each u rows
            beams_top = crvs[:-1]
            planes_top = planes[:-1]
            beams_bottom = crvs[1:]
            planes_bottom = planes[1:]

            # for the seam row, get dowels on only inner side end of the beam
            if j in self.seam_row_index:
                for index in self.seam_row_index:
                    if j == index:
                        if j == 0:
                            for i in range(len(beams_top)):
                                self.end_dowel_crvs.append(self.get_a_single_dowel_end_connection(beams_top[i],planes_top[i],1,beams_bottom[i],planes_top[i],1))
                        elif j == len(self.beam_crvs)-1:
                            for i in range(len(beams_top)):
                                self.end_dowel_crvs.append(self.get_a_single_dowel_end_connection(beams_top[i],planes_top[i],0,beams_bottom[i],planes_top[i],0))
            # for other rows, get dowels on both ends of the beam
            else:
                for i in range(len(beams_top)):
                    self.end_dowel_crvs.append(self.get_a_single_dowel_end_connection(beams_top[i],planes_top[i],0,beams_bottom[i],planes_top[i],0))
                    self.end_dowel_crvs.append(self.get_a_single_dowel_end_connection(beams_top[i],planes_top[i],1,beams_bottom[i],planes_top[i],1))

            # for edge row if there is any
            if j in self.edge_row_index:
                for index in self.edge_row_index:
                    if j == index:
                        if j == 0:
                            for i in range(len(beams_top)):
                                self.end_dowel_crvs.append(self.add_edge_dowel(beams_top[i],planes_top[i],1,beams_bottom[i],planes_top[i],1))
                        elif j ==len(self.beam_crvs)-1:
                            for i in range(len(beams_top)):
                                self.end_dowel_crvs.append(self.add_edge_dowel(beams_top[i],planes_top[i],0,beams_bottom[i],planes_top[i],0))
            j += 1

    def get_seam_connections(self):
        # get the edge to be seam connected
        for i in range(len(self.seam_side)):
            crvs = copy.deepcopy(self.beam_crvs[self.seam_row_index[i]])
            plns = copy.deepcopy(self.beam_planes[self.seam_row_index[i]])
            # detect if reverse dowel direction
            if self.seam_crv[i].ClosestPoint(crvs[0].PointAt(0),20000)[1]>self.seam_crv[i].ClosestPoint(crvs[-1].PointAt(0),20000)[1]:
                crvs.reverse()
                plns.reverse()
                plns_flip = [rg.Plane(pln.Origin,pln.XAxis,pln.YAxis*-1) for pln in plns]
                plns = plns_flip
            # generate connections
            beams_top = crvs[:-1]
            planes_top = plns[:-1]
            beams_bottom = crvs[1:]
            planes_bottom = plns[1:]
            for j in range(len(beams_top)):
                self.end_dowel_crvs.append(self.get_a_single_dowel_end_connection(beams_top[j],planes_top[j],self.seam_side[i],beams_bottom[j],planes_top[j],self.seam_side[i]))


# get surface edge to define special situations
srf.SetDomain(0, rg.Interval(0,1))
srf.SetDomain(1, rg.Interval(0,1))

u_0_crv = srf.IsoCurve(0,0)
u_0_crv.Domain = rg.Interval(0,1)
test_pt_0 = u_0_crv.PointAt(0.5)

u_1_crv = srf.IsoCurve(0,1)
u_1_crv.Domain = rg.Interval(0,1)
test_pt_1 = u_1_crv.PointAt(0.5)

# detect seam crv as guide line for seam dowel connection
seam_crv = []
seam_side = []
for c in seam_crvs:
    if c.ClosestPoint(test_pt_0,100)[0]:
        seam_crv.append(c)
        seam_side.append(0)
    if c.ClosestPoint(test_pt_1,100)[0]:
        seam_crv.append(c)
        seam_side.append(1)

# detect edge crv as guide line for edge dowel connection
edge_side = []
for c in edge_crvs:
    if c.ClosestPoint(test_pt_0,100)[0]:
        edge_side.append(0)
    if c.ClosestPoint(test_pt_1,100)[0]:
        edge_side.append(1)

# get beam net
test_beams = BeamNet(srf,rebuild_srf,beam_shift,curvature_factor_u,curvature_factor_v,offset_x,offset_y,seam_crv,seam_side,edge_side)

# output
beam_curves = []
for crvs in test_beams.beam_crvs:
    beam_curves.extend(crvs)

beam_planes = []
for planes in test_beams.beam_planes:
    beam_planes.extend(planes)

dowel_crvs = []
dowel_crvs.extend(test_beams.end_dowel_crvs)

assembly_beam_crvs=[]
assembly_beam_crvs.extend(test_beams.flip_matrix(test_beams.beam_crvs)[0])
assembly_beam_crvs.extend(test_beams.flip_matrix(test_beams.beam_crvs)[-1])

assembly_beam_plns=[]
assembly_beam_plns.extend(test_beams.flip_matrix(test_beams.beam_planes)[0])
assembly_beam_plns.extend(test_beams.flip_matrix(test_beams.beam_planes)[-1])

temp = ['beam average length:',test_beams.beam_length,'dowl average lengh:',test_beams.dowel_length]
