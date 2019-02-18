# class that generates connections between beams

import sys
sys.path.append("/Users/jonas/Dropbox/0.dfab/Trimester 2/Project I - Gradual Assemblies/Gradual-Assemblies/UR_Control")
import geometry.beam as beam

reload(beam)

import Rhino.Geometry as rg

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

    def __double_joint_start(self):
        """ Joint generation for element that is in an u-direction end state """
        # uses self.B1 & self.B2

    def __end_joint(self):
        """ Tension joint at the top, perhaps bottom, of the system """
