import unittest

from crop_slab.joint import HorizontalJoint
from crop_slab.subjoint import SubJoint

class TestJoints(unittest.TestCase):
    def test_initilization_subjoint(self):
        subjoint = SubJoint(10, 5, 20, 10)
        self.assertEqual(subjoint.x1, 10)
        self.assertEqual(subjoint.y1, 5)
        self.assertEqual(subjoint.x2, 20)
        self.assertEqual(subjoint.y2, 10)

        subjoint = SubJoint(20, 10, 10, 5)
        self.assertEqual(subjoint.x1, 10)
        self.assertEqual(subjoint.y1, 5)
        self.assertEqual(subjoint.x2, 20)
        self.assertEqual(subjoint.y2, 10)
        self.assertEqual(subjoint.dist, 11.18)


    def test_initilization_subjoint_zero_length(self):
        with self.assertRaises(ValueError):
            subJoint = SubJoint(10, 5, 10, 5)

    
    def test_construct_joint_simple(self):
        subjoint_left = SubJoint(0, 0, 3000, 3000)
        subjoint_right = SubJoint(3000, 3000, 6000, 6000)
        joint = HorizontalJoint()

        if (joint.subjoint_belongs_to_joint(subjoint_left)):
            joint.add_subjoint(subjoint_left)
        
        if (joint.subjoint_belongs_to_joint(subjoint_right)):
            joint.add_subjoint(subjoint_right)
        
        self.assertEqual(subjoint_left, joint.subjoints[0])
        self.assertEqual(subjoint_right, joint.subjoints[1])

    
    def test_construct_joint_simple_reverse(self):
        subjoint_right = SubJoint(3000, 3000, 6000, 6000)
        subjoint_left = SubJoint(0, 0, 3000, 3000)
        joint = HorizontalJoint()

        if (joint.subjoint_belongs_to_joint(subjoint_right)):
            joint.add_subjoint(subjoint_right)
        
        if (joint.subjoint_belongs_to_joint(subjoint_left)):
            joint.add_subjoint(subjoint_left)
        
        self.assertEqual(subjoint_left, joint.subjoints[0])
        self.assertEqual(subjoint_right, joint.subjoints[1])


    def test_construct_joint_near(self):
        subjoint_left = SubJoint(0, 0, 3000, 3000)
        subjoint_right = SubJoint(3099, 3099, 5000, 3500)
        joint = HorizontalJoint()

        if (joint.subjoint_belongs_to_joint(subjoint_left)):
            joint.add_subjoint(subjoint_left)
        
        if (joint.subjoint_belongs_to_joint(subjoint_right)):
            joint.add_subjoint(subjoint_right)
        
        self.assertEqual(subjoint_left, joint.subjoints[0])
        self.assertEqual(subjoint_right, joint.subjoints[1])
    

    def test_construct_joint_near2(self):  
        subjoint_left = SubJoint(0, 0, 3000, 3000)
        subjoint_right = SubJoint(3099, 3099, 5000, 3500)
        joint = HorizontalJoint()

        if (joint.subjoint_belongs_to_joint(subjoint_right)):
            joint.add_subjoint(subjoint_right)
        
        if (joint.subjoint_belongs_to_joint(subjoint_left)):
            joint.add_subjoint(subjoint_left)
        
        self.assertEqual(subjoint_left, joint.subjoints[0])
        self.assertEqual(subjoint_right, joint.subjoints[1])

    def test_construct_joint_far(self):
        subjoint_left = SubJoint(0, 0, 3000, 3000)
        subjoint_right = SubJoint(3101, 3101, 5000, 5000)
        joint = HorizontalJoint()

        if (joint.subjoint_belongs_to_joint(subjoint_left)):
            joint.add_subjoint(subjoint_left)
        
        if (joint.subjoint_belongs_to_joint(subjoint_right)):
            joint.add_subjoint(subjoint_right)
        
        self.assertEqual(subjoint_left, joint.subjoints[0])
        self.assertRaises(IndexError, lambda: joint.subjoints[1])

    
    def test_construct_joint_three_pieces(self):
        subjoint_end = SubJoint(3000, 3000, 5000, 3500)
        subjoint_middle = SubJoint(1000, 1000, 2950, 2975)
        subjoint_begin = SubJoint(950, 950, 0, 0)

        joint = HorizontalJoint()

        if (joint.subjoint_belongs_to_joint(subjoint_end)):
            joint.add_subjoint(subjoint_end)
        
        if (joint.subjoint_belongs_to_joint(subjoint_middle)):
            joint.add_subjoint(subjoint_middle)
        
        if (joint.subjoint_belongs_to_joint(subjoint_begin)):
            joint.add_subjoint(subjoint_begin)

        self.assertEqual(subjoint_begin, joint.subjoints[0])
        self.assertEqual(subjoint_middle, joint.subjoints[1])
        self.assertEqual(subjoint_end, joint.subjoints[2])
        


    
