# getting srf outside of Domain

import Rhino.Geometry as rg
import copy as c

# grasshopper

srfs
new_srf_list = []

for srf in srfs:
    srf.SetDomain(0, rg.Interval(5, 14))
    srf.SetDomain(1, rg.Interval(5, 14))

    isocrv_list = []
    for u in range(5, 15):
        point_v_list = []
        for v in range(13, 17, 1):
            point_v_list.append(c.deepcopy(srf.PointAt (u, v)))
        isocrv_list.append(rg.NurbsCurve.Create(False, 3, point_v_list))
    loft_type = rg.LoftType.Tight
    local_new_srf = rg.Brep.CreateFromLoftRebuild(isocrv_list, rg.Point3d.Unset, rg.Point3d.Unset, loft_type, False, 50)[0]
    local_new_srf = c.deepcopy(local_new_srf.Faces.Item[0].ToNurbsSurface())
    new_srf_list.append(c.deepcopy(local_new_srf))
