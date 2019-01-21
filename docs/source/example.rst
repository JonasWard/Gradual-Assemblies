Examples
================

How to Use
--------------------

.. code-block :: python

    # import libraries
    import Rhino.Geometry as rg
    from geometry.beam import Beam
    from geometry.dowel import Dowel
    from geometry.hole import Hole

    # dimensions
    beam_dx = 145
    beam_dy = 10
    beam_dz = 4
    dowel_radius = 1.0

    # create beams from planes
    beam_plane_1 = rg.Plane(rg.Plane.WorldXY)
    beam_plane_1.Translate(rg.Vector3d(400, 30, 0))

    beam_plane_2 = rg.Plane(rg.Plane.WorldXY)
    beam_plane_2.Translate(rg.Vector3d(400, 30, 0))

    beam_planes = [beam_plane_1, beam_plane_2]

    # create dowels from planes
    dowel_plane_1 = rg.Plane(rg.Plane.WorldXY)
    dowel_plane_1.Translate(rg.Vector3d(440, 30, 0))
    dowel_plane_2 = rg.Plane(rg.Plane.WorldXY)
    dowel_plane_2.Translate(rg.Vector3d(-440, 30, 0))

    dowel_planes = [dowel_plane_1, dowel_plane_2]

    beams = []

    # feed beam planes 
    for beam_plane in beam_planes:
        
        # create an instance of beam class
        beam = Beam(base_plane=beam_plane, dx=beam_dx, dy=beam_dy, dz=beam_dz)
        
        for dowel_plane in dowel_planes:

            # create an instance of dowel class as the connected dowel connected
            dowel = Dowel(base_plane=dowel_plane, dowel_radius=dowel_radius)

            # add the dowel to the beam as its connection
            beam.add_dowel(dowel)
        
        beams.append(beam)

    # get planes and brep(s) 
    safe_planes, top_planes, bottom_planes, beam_breps = Hole.get_tool_planes_as_tree(beams, safe_plane_diff=100)

.. image:: https://raw.githubusercontent.com/ytakzk/Gradual_Assemblies/master/docs/source/_static/example_grasshopper.PNG


Beam Class
--------------------

A class for beams

.. code-block :: python

    beam_plane = rg.Plane.WorldXY # the plane to define a beam's position and orientation
    beam_dx    = 145 # the length of a beam
    beam_dy    = 10 # the width of a beam
    beam_dz    = 4 # the depth of a beam

    # instanciate
    beam = Beam(base_plane=beam_plane,
                dx=beam_dx,
                dy=beam_dy,
                dz=beam_dz)
    
    # get a brep of the beam (used for visualization or debug)
    brep = beam.brep_representation()


Dowel Class
--------------------

A class for dowels

.. code-block :: python

    dowel_plane  = rg.Plane.WorldXY # the plane to define a dowel's position and orientation
    dowel_radius = 1.0 # the radius of a dowel

    # instanciate from plane
    dowel_plane = rg.Plane.WorldXY
    dowel = Dowel(base_plane=dowel_plane, dowel_radius=1.0)

    # OR

    # instanciate from line
    dowel_line = rg.Line(rg.Point3d(0, 0, -30), rg.Point3d(0, 0, 30))
    dowel = Dowel(line=dowel_line, dowel_radius=1.0)

    # add a dowel to the beam (possible if the beam has been declared before)
    beam.add_dowel(dowel)


Hole Class
--------------------

A class for making planes to open holes in beams

.. code-block :: python

    # contain beams as array
    beams = [beam_1, beam_2]

    # returns four kinds of data trees
    #
    # 1st: safe planes to drill
    # 2nd: planes to start drilling
    # 3rd: planes to end drilling
    # 4th: breps of beams in each state of drilling

    safe_planes, top_planes, bottom_planes, beam_breps = Hole.get_tool_planes_as_tree(beams,
        safe_plane_diff=100)
