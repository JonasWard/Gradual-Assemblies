# this is an attempt at dividing a surface in bite-size possibility

import Rhino.Geometry as rg

# grasshopper parameters

surface
min_length
max_length
div_aim

# resetting the domain of the surface

domain_goal = rg.Interval(0.0, 1.0)
surface.SetDomain(0, domain_goal)
surface.SetDomain(1, domain_goal)
print surface.Domain[0], surface.Domain[1]
