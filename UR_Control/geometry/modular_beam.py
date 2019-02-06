import Rhino.Geometry as rg
import ghpythonlib.components as gh
import Grasshopper.Kernel.Data.GH_Path as ghpath
import Grasshopper.DataTree as datatree
import System
import math
from beam import Beam
import hole
import module

"""
Beam class for the modular unit
"""
class ModularBeam(Beam):

    def __init__(self, base_plane, dx, dy, dz, shift_ratio, depth):
        
        super(ModularBeam, self).__init__(base_plane, dx, dy, dz)
        
        self.depth = depth
        self.shift_ratio = shift_ratio
        self.module_list = []
        self.alive = True
        self.extended = False
        self.twist_angle = 0
        self.wing_angle  = 0
        self.rot_angle   = 0
    
    def belongs_to(self, module):
        
        self.module_list.append(module)

    def get_depth_of_module(self):
        
        modules = sorted(self.module_list, key=lambda m: m.depth) 
        return modules[-1].depth

    def get_middle_beam_in_module(self):
        
        for module in self.module_list:
            if module.middle_beam != self:
                return module.middle_beam

    def rotate_or_terminate(self, twist_angle, wing_angle, rot_angle):

        # simulate
        plane = rg.Plane(self.base_plane)
        
        self.simulate_rotation(plane, twist_angle, wing_angle, rot_angle)
 
        # get a distance to the bounding box
        line = rg.Line(plane.Origin - (plane.XAxis * self.dx * 0.5), \
                        plane.Origin + (plane.XAxis * self.dx * 1.5)).ToNurbsCurve()
           
        _, vals = rg.Intersect.Intersection.CurveBrep(line, bounding_brep, 1.0, 0.1)
        
        too_close = True if len(vals) > 0 else False 

        if not too_close:
    
            self.rotate(twist_angle, wing_angle, rot_angle)
            
            self.twist_angle = twist_angle
            self.wing_angle  = wing_angle
            self.wing_angle  = wing_angle
            
        else:
            
            self.alive = False

    
    def extend_to_ground_if_needed(self):

        if extension_ratio == 0:
            return

        plane = self.base_plane
        line  = rg.Line(plane.Origin + (plane.XAxis * self.dx * 0.5), \
                        plane.Origin + (plane.XAxis * self.dx * (0.5 + extension_ratio)))
        
        succeeded, v = rg.Intersect.Intersection.LinePlane(line, rg.Plane.WorldXY)
        
        if succeeded and line and v >= 0 and v <= 1:

            p = line.PointAt(v)
            dist = p.DistanceTo(plane.Origin)
            diff = dist - (self.dx * 0.5)
            vec = plane.XAxis * diff * 0.5
            plane.Translate(vec)
            self.dx += diff * 0.5
            self.extended = True

    def rotate(self, twist_angle, wing_angle, rot_angle):
        
        # twist
        radian, center, axis, _ = self.__get_rotation_values(self.base_plane, twist_angle, 'twist')
        self.base_plane.Rotate(radian, axis, center)
        
        # wing
        radian, center, axis, _ = self.__get_rotation_values(self.base_plane, wing_angle, 'wing')
        self.base_plane.Rotate(radian, axis, center)

        # rot
        radian, center, axis, orientation_sign = self.__get_rotation_values(self.base_plane, rot_angle, 'rot')
        self.base_plane.Rotate(radian, axis, center)

        # move
        middle_beam = self.get_middle_beam_in_module()
        move_vec = orientation_sign * middle_beam.base_plane.ZAxis * self.dy * 0.5 * math.sin(radian)
        self.base_plane.Translate(move_vec)

    def simulate_rotation(self, plane, twist_angle, wing_angle, rot_angle):
        
        # twist
        radian, center, axis, _ = self.__get_rotation_values(plane, twist_angle, 'twist')
        plane.Rotate(radian, axis, center)
        
        # wing
        radian, center, axis, _ = self.__get_rotation_values(plane, wing_angle, 'wing')
        plane.Rotate(radian, axis, center)

        # rot
        radian, center, axis, orientation_sign = self.__get_rotation_values(plane, rot_angle, 'rot')
        plane.Rotate(radian, axis, center)

        # move
        middle_beam = self.get_middle_beam_in_module()
        move_vec = orientation_sign * middle_beam.base_plane.ZAxis * self.dy * 0.5 * math.sin(radian)
        plane.Translate(move_vec)

            
    def __rotate(self, plane, angle, rotation_center, axis):
        
        if not bounding_brep:
            
            plane.Rotate(angle, axis, rotation_center)

        else:
            
            # check to see if the new beam is inside of the bounding brep or not
            candidate_angles = [angle, angle * 0.75, angle * 0.50, angle * 0.25, 0]
            
            for angle in candidate_angles:
                
                plane.Rotate(angle, axis, rotation_center)

                evaluation_point = rg.Point3d.Add(plane.Origin, plane.XAxis * self.dx * 0.5)
            
                if not bounding_brep.IsPointInside(evaluation_point, 1.0, True):
                    self.alive = False
            
                    # if outside, make it flush and try again
                    plane.Rotate(-angle, axis, rotation_center)
                
                else:
                    
                    self.alive = True
                    break
                    
    def __get_rotation_values(self, plane, angle, rotation):
        
        if rotation == 'twist':

            shift_vec = plane.XAxis * ((self.dx * 0.5) - 90) 
            
            # this is the center of the overlapping area between beams
            rotation_center = rg.Point3d(plane.Origin - shift_vec)
            
            radian = math.radians(angle)

            return radian, rotation_center, plane.ZAxis, 1.0

        elif rotation == 'wing':

            # whether the normal of this beam goes toward the same direction of its middle beam or not
            middle_beam = self.get_middle_beam_in_module()
            vec = rg.Vector3d(plane.Origin) - rg.Vector3d(middle_beam.base_plane.Origin)
            vec_angle = rg.Vector3d.VectorAngle(vec, middle_beam.base_plane.ZAxis)

            # in case that it goes in the opposite direction
            if vec_angle < math.pi * 0.5:
                angle *= -1

            # the end point along its length direction
            shift_vec = plane.XAxis * self.dx * 0.5
            rotation_center = rg.Point3d(plane.Origin - shift_vec)
            
            radian = math.radians(angle)
            
            return radian, rotation_center, plane.YAxis, 1.0

        elif rotation == 'rot':

            # whether the normal of this beam goes toward the same direction of its middle beam or not
            middle_beam = self.get_middle_beam_in_module()
            vec = rg.Vector3d(plane.Origin) - rg.Vector3d(middle_beam.base_plane.Origin)
            vec_angle = rg.Vector3d.VectorAngle(vec, middle_beam.base_plane.ZAxis)
        
            # rotation center
            rotation_center = rg.Point3d(plane.Origin)
        
            radian = math.radians(angle)

            # to avoid the collision with its middle beam, move the beam

            # in case that it goes in the opposite direction
            orientation_sign = 1.0 if vec_angle < math.pi * 0.5 else -1.0

            # in case that the angle is negative 
            orientation_sign *= 1.0 if angle > 0 else -1.0

            return radian, rotation_center, self.base_plane.XAxis, orientation_sign
