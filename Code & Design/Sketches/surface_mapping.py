# simple surface divisions

import sys

# import the beam_class
path_to_append = ''.join([double_parent, "/UR_Control"])
sys.path.append(path_to_append)

print path_to_append

import geometry.beam as beam

# new hole class
path_to_append = single_parent

print path_to_append
sys.path.append(path_to_append)

print path_to_append

import Joints.hole_class as hc

import Rhino.Geometry as rg

# surface class based on surface_sets

class Divisions(object):
    """ Class that contains the amount of divisions for the organised surfaces """
    def __init__(self, value, direction = 0):
        self.val = value
        self.dir = direction

class StartValue(object):
    """ Class that indicates the start value of an organised surface based on, has to be 0 or 1"""
    def __init__(self, value = 0):
        self.value = 0

class OrganisedSurface(object):
    def __init__(self, srf, v_div = None, u_div = None, start_val = 0, create_set = False):
        """ initialization
        :param srf:         The surface geometry to consider
        :param u_div:       The amount of u_divisions the surface has to consider or another surface
        :param v_div:       The amount of v_divisions the surface has to consider or another surface
        :parap start_val:   Defines the starting condition of the surface (0 or 1 - default = 0)
        :param create_set:  Whether to create or not create or add set depending on in the case u_div or v_div was a surface (default False)
        """
        self.__srf_check(srf)
        self.start_val_set = False
        self.div_vals = [0, 0]
        self.__division_check(v_div, 0)
        self.__division_check(u_div, 0)
        if not(self.start_val_set):
            self.start_val = start_val


    def __srf_check(self, srf):
        """ internal method that checks whether the input value is a nurbs surface, if it's a surface, transforms it into nurbssurface
        :param srf:     Surface to consider adding to the class (has to be of type rg.Surface or rg.NurbsSurface)
        """
        if (type(srf) == rg.NurbsSurface()):
            self.srf = srf
        elif (type(srf) == rg.Surface()):
            self.srf = srf.ToNurbsSurface()
        else:
            self.error = True
            self.error_text = "Invalid Surface Input"

        self.__error_display()

    def __division_check(self, div_val, dir):

        if(div_val == None):
            #inherented dif vals
            self.error = False

        # elif((type(div_val) == OrganisedSurface()) and self.start_val_set):
        #     self.error = True
        #     self.error_text = "For now, this shouldn't happen (: )"
        elif((type(div_val) == OrganisedSurface()) and not(self.start_val_set)):
            self.div_vals[dir] = div_val.div_vals[dir]
            self.start_val = (div_val.start_val + div_val.div_vals[dir]) % 2
            self.start_val_set = True
        elif((type(div_val) == int) or (type(div_val) == int)):
            self.div_vals[dir] = div_val
        else:
            self.error = True
            self.error_text = ''.join(["Invalid Direction Input for direction ", dir])

        self.__error_display()

    def __create_set(self):
        pass

    def __error_display(self):
        if(self.error):
            print self.error_text

class SurfaceSet(object):
    def __init__(self, o_srf_list = None, v_or_u_continious = 0, loop = False):
        """ initialization
        :param srf_class_list:      Empty, Organised Surface or Inemurable list Org. Srfs. Which Define it's geometry
        :param v_or_u_continious:   Whether the surface set is continious in the v or u direction
        :parap loop:                Whether the SurfaceSet runs into itself at the end locations
        """

        self.srf_list = []
        self.__surface_add_check(o_srf_list)

    def AddSurface(self, o_srf, v_or_u_continious = 0, loop = False):
        self.__surface_add_check(o_srf)

    def __surface_add_check(self, srf_set):
        if (srf_set == None):
            self.empty_srf = True
            self.srf_list = []
        elif (type(srf_set) == OrganisedSurface()):
            self.empty_srf = False
            self.srf_list = [srf_set]
        elif (type(srf_set[0]) == OrganisedSurface()):
            self.empty_srf = False
            self.srf_list = srf_set
        else:
            self.error = True
            self.error_text = "Invalid Surface Input"

        self.__error_display()

    def __error_display(self):
        if(self.error):
            print self.error_text

    def Generate_BeamNetwork(self):
        """ generating the beam relations """
        # should generate a beam network class
        pass

    def __surface_loop_check(self):
        """ internal method to fix uneven amount of divisions in the loop direction """
        pass

    def Split(self, splits = 2):
        """ method that splits the surface set in a given amount of surfaces along the u direction
        :param splits:       """
        pass

class BeamNetwork(object):
    """ Class that defines the relations between the different beams and as such defines wheren which type of joint should be generated """
    def __init__(self, beams, relations = None):
        """ initialization
        :param beams:       Beam Class Objects as a list sorted as: [u_direction][v_direction]
        :param relations:   Optional list we might need to define extra relations (to other surfaces or when the surface touches upon itself again)
        """

class Joint(object):
    """ Joint class that links three (or two) beams togehter with manipulated dowels """
    def __init__(self, first_beam = None, middle_beam = None, third_beam = None):
        """ Base initialization of the connections
        :param beam_0: initializes the first beam to be considered in the joint
        :param beam_1: initializes the second (middle) beam to be considered in the joint
        :parap beam_2: initializes the third beam to be considered in the joint
        """

        self.B0 = first_beam
        self.B1 = middle_beam
        self.B2 = third_beam

        self.__beam_check()

        if not(self.error_flag_input):

        else:
            print self.error_text

    def __beam_check(self):
        """ Error generation function to check the beam being entered
            Setting and checking joint type
            jointtype == 0 = triple, 1 = double_start, 2 = double_end
            """
        # initialization
        listed_numbers = ["first ", "second", "third", "fourth", "fifth", "sixth"]
        self.error_flag_input = False

        # # checking whether the inputed beams are members of the beam class
        # Beam_list = [self.B0, self.B1, self.B2]
        # error_values = [not(type(bm) == beam.Beam or bm == None) for bm in beam_list]
        # problematic_beams = [if(error_val): listed_numbers[i] for i, error_val in enumerate(error_values)]
        # beam_text = []
        # self.error_text =


        if not(self.error_flag_input):
            # checking whether the beam input is reasonable

            self.joint_type = 0

            if self.B1 == None:
                # checking whether the middle beam is given or not
                self.error_flag_middle = True

            if self.B0 == None:
                # checking whether the first beam is being considered or not
                # in case this one is not given, check whether the rest are given
                self.joint_type = 2
                if self.B2 == None:
                    self.error_flag_ends = True
            elif self.B2 == None:
                self.joint_type = 1

            if (self.error_flag_ends or self.error_flag_middle):
                self.error_flag_input = True
                if (self.error_flag_ends and self.error_flag_middle):
                    self.error_text = "You need to give me something to work with mate!"
                elif (self.error_flag_ends):
                    self.error_text = "Can't do shit without either an end or a start beam!"
                elif (self.error_flag_middle):
                    self.error_text = "No Triple Penetration without a middle beam!"

    def __triple_joint(self):
        """ Joint generation if you have to generate a dowel through 3 beams """
        # so uses both self.B0, self.B1 & self.B2

    def __double_joint_start(self):
        """ Joint generation for element that is in an u-direction start state """
        # uses self.B0 & self.B1

    def __double_joint_end(self):
        """ Joint generation for element that is in an u-direction end state """
        # uses self.B1 & self.B2

    def __end_joint(self):
        """ Tension joint at the top, perhaps bottom, of the system """

class Hole(object):
    """ Hole class that defines the hole positions on which the dowels in the joint will be designed based on the type of joint and the beam """
    def __init__(self, ref_beam, location=0, type=0, type_args=[120, 20, 30, False, False]):
        """ initialization
            :param beam:        Beam that's being considered
            :param locations:   Iterable list or float indicating the t_vals on the beam baseline where you need the holes (default = 0)
            :param type:        Topological type of the joint (default = 0)
            :param type_args:   Iterable list containing parametrs defining the position of the joint holes in relationship to the joint type
        """

        self.beam = ref_beam
        self.beam_line = self.beam.get_baseline()
        self.type = type
        self.locs = location
        self.type_args = type_args

        self.__type_definitions()
        if(self.type_completed_flag):
            self.__joint_point_calculation()
        else:
            print self.error_message

    def __type_definitions(self):
        """ internal method that defines the different joint types
            type = 0 -> default type, takes the args:
                x0_ext          - first shift along the beams axis, resulting into a new middle point
                cover_h         - how much the second point should lay underneath the edge of the beam
                x1_ext          - second shfit along the beams axis, resulting into the new top (or bottom) point
                symmetry_flag   - whether the dowel hole connections are axis symmetrical (True) or point symmetrical (False)
                invert_flag     - whether the direction should be inverted or not
        """
        if (self.type == 0):
            type_input_count = 5

            type_args_count = len(self.type_args)
            if not(type_args_count == type_input_count):
                self.error_message = ''.join(["You should've given ", type_input_count, " values, but you only gave ", type_args_count])
                self.type_completed_flag = False

            else:
                self.type_completed_flag = True
                x0_ext, cover_h, x1_ext, symmetry_flag, invert_flag = self.type_args
                unit_x = self.beam.base_plane.XAxis
                unit_y = self.beam.base_plane.YAxis
                # setting directions according to flags
                if (symmetry_flag):
                    v1_switch = -1
                else:
                    v1_switch = 1

                if (invert_flag):
                    v2_switch = -1
                else:
                    v2_switch = 1

                self.vec_0 = rg.Vector3d(unit_x) * x0_ext
                self.vec_1 = rg.Vector3d(unit_y) * (self.beam.dy / 2 - cover_h) * v1_switch
                self.vec_2_a = rg.Vector3d(unit_x) * x1_ext
                self.vec_2_b = v1_switch * self.vec_2_a

                self.beam_extension_l = x0_ext + x1_ext

    def type_transform(self, point_val):
        """ method that returns the joint points at a certain point on the beam
            :param point:   The t_val of the point on the beam to consider.
            :return:        The beam hole locations & reference points.
        """
        if (self.type == 0):
            local_point = self.beam_line.PointAt(point_val)

            # translating to the mid_points
            mv_0 = rg.Transform.Translation(self.vec_0)
            mv_1 = rg.Transform.Translation(-self.vec_0)
            mid_0, mid_1 = rg.Point3d(local_point), rg.Point3d(local_point)
            mid_0.Transform(mv_0)
            mid_1.Transform(mv_1)

            # translating to the end_points set_0
            v_top = rg.Vector3d(self.vec_1 + self.vec_2_a)
            v_bottom = rg.Vector3d(- v_top)
            mv_0 = rg.Transform.Translation(v_top)
            mv_1 = rg.Transform.Translation(v_bottom)
            top_0, bot_0 = rg.Point3d(mid_0), rg.Point3d(mid_0)
            top_0.Transform(mv_0)
            bot_0.Transform(mv_1)

            # translating to the end_points set_1
            v_top = self.vec_1 + self.vec_2_b
            v_bottom = - v_top
            mv_0 = rg.Transform.Translation(v_top)
            mv_1 = rg.Transform.Translation(v_bottom)
            top_1, bot_1 = rg.Point3d(mid_1), rg.Point3d(mid_1)
            top_1.Transform(mv_0)
            bot_1.Transform(mv_1)

            hole_list = [[local_point], [top_0, mid_0, bot_0], [top_1, mid_1, bot_1]]
            return hole_list

    def __joint_point_calculation(self):
        """ Internal method that executes the joint_point_calculations """
        local_line = self.beam_line
        b_pts = []
        self.joint_pts = []
        if (type(self.locs) == float or type(self.locs) == int):
            b_pt = local_line.PointAt(self.locs)
            b_pts.append(b_pt)
            self.joint_pts = self.type_transform(self.locs)
        elif (type(self.locs) == list):
            for t_val in self.locs:
                b_pt = local_line.PointAt(t_val)
                b_pts.append(b_pt)
                self.joint_pts.append(self.type_transform(self.locs))
