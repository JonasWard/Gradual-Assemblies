# grasshopper inputs
import Rhino.Geometry as rg
import copy as c

srfs
count = int(len(srfs) / 2)
#
srfs_set_count = [[srf_index * 2, srf_index * 2 + 1] for srf_index in range(count)]
srfs_sets = [[srfs[srf_index * 2], srfs[srf_index * 2 + 1]] for srf_index in range(count)]
# srf_list = list(srfs.Branches)
print srfs_set_count

a = []

for srfs_set in srfs_sets:
    print "len srfs_set", len(srfs_sets)
    isocrvs = []
    for switch, srf in enumerate(srfs_set):
        print switch
        srf.SetDomain(0, rg.Interval(0, 9))
        srf.SetDomain(1, rg.Interval(0, 9))

        point_list = []
        for v in range(10):
            point_v_list = []
            for u in range(10):
                point_v_list.append(c.deepcopy(srf.PointAt (u, v)))
            if (switch == 0):
                point_v_list.reverse()
            point_list.append(c.deepcopy(point_v_list))
        if (switch == 0):
            point_list.reverse()

        for i in range(switch, 10):
            print i
            isocrvs.append(rg.NurbsCurve.Create(False, 3, point_list[i]))


    loft_type = rg.LoftType.Tight
    local_new_srf = rg.Brep.CreateFromLoftRebuild(isocrvs, rg.Point3d.Unset, rg.Point3d.Unset, loft_type, False, 50)[0]
    local_new_srf = c.deepcopy(local_new_srf.Faces.Item[0].ToNurbsSurface())
    print local_new_srf
    a.append(local_new_srf)
