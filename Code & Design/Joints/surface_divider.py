import rhinoscriptsyntax as rs
import Rhino.Geometry as rg

new_srf_set = []
u_div = 5

srf.SetDomain(0, rg.Interval(0, u_div - 1))
second_srf = srf
for u_val in range(1, u_div - 1, 1):
	local_srf_set = second_srf.Split(0, u_val)
	print local_srf_set
	new_srf_set.append(local_srf_set[0])
	second_srf = local_srf_set[1]
new_srf_set.append(second_srf)

final_srf_set = []
final_srf_set_viz = []

for surf in new_srf_set:
	local_new_srf_set = []
	v_div = 5

	surf.SetDomain(1, rg.Interval(0, v_div - 1))
	second_srf = surf
	for v_val in range(1, v_div - 1, 1):
		local_srf_set = second_srf.Split(1, v_val)
		print local_srf_set
		local_new_srf_set.append(local_srf_set[0])
		final_srf_set_viz.append(local_srf_set[0])
		second_srf = local_srf_set[1]
	local_new_srf_set.append(second_srf)
	final_srf_set_viz.append(local_srf_set[0])

	final_srf_set.append(local_new_srf_set)
