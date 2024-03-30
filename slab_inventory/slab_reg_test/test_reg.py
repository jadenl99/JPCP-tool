import unittest
from slab_reg.slab_registration import SlabRegistration

reg = SlabRegistration()
class TestRegistration(unittest.TestCase):
    def test_case1(self):
        """
        BY: |----20----||----20----||----20----|
        CY: |---18-----||-9--||-11-||----20----|
        
        Expected: the second BY 20 slab must align with the CY 9 and 11 slabs.
        """
        BY_info = [
            {   
                'id': 1,
                'offset': 0,
                'length': 20
            },
            {   
                'id': 2,
                'offset': 20,
                'length': 20
            },
            {
                'id': 3,
                'offset': 40,
                'length': 20
            }
        ]   
        CY_info = [
            {
                'id': 1,
                'offset': 0,
                'length': 20
            },
            {
                'id': 2,
                'offset': 20,
                'length': 9
            },
            {
                'id': 3,
                'offset': 29,
                'length': 11
            },
            {
                'id': 4,
                'offset': 40,
                'length': 20
            }
        ]
        
        reg_info = reg.classify(BY_info, CY_info)

        self.assertEqual(reg_info[0]['CY_id'], [1])
        self.assertEqual(reg_info[1]['CY_id'], [2, 3])
        self.assertEqual(reg_info[2]['CY_id'], [4])


    def test_case2(self):
        """
        BY: |----20----||----20----||----20----|
        CY: |---18---||--8--||--14-||----20----|
        
        Expected: the second BY 20 slab must align with the CY 8 and 14 slabs.
        """
        BY_info = [
            {   
                'id': 1,
                'offset': 0,
                'length': 20
            },
            {   
                'id': 2,
                'offset': 20,
                'length': 20
            },
            {
                'id': 3,
                'offset': 20,
                'length': 20
            }
        ]
        
        CY_info = [
            {
                'id': 1,
                'offset': 0,
                'length': 18
            },
            {
                'id': 2,
                'offset': 18,
                'length': 8
            },
            {
                'id': 3,
                'offset': 26,
                'length': 14
            },
            {
                'id': 4,
                'offset': 40,
                'length': 20
            }
        ]
        
        reg_info = reg.classify(BY_info, CY_info)

        self.assertEqual(reg_info[0]['CY_id'], [1])
        self.assertEqual(reg_info[1]['CY_id'], [2, 3])
        self.assertEqual(reg_info[2]['CY_id'], [3])


    def test_case3(self):
        """
        BY: |----20----||----20----||----20----|
        CY: |---18---||------26------||---18---|
        
        Expect one to one mapping between BY and CY slabs.
        """
        BY_info = [
            {   
                'id': 1,
                'offset': 0,
                'length': 20
            },
            {   
                'id': 2,
                'offset': 20,
                'length': 20
            },
            {
                'id': 3,
                'offset': 40,
                'length': 20
            }
        ]     
        CY_info = [
            {
                'id': 1,
                'offset': 0,
                'length': 18
            },
            {
                'id': 2,
                'offset': 18,
                'length': 24
            },
            {
                'id': 3,
                'offset': 44,
                'length': 18
            }
        ]
        
        reg_info = reg.classify(BY_info, CY_info)

        self.assertEqual(reg_info[0]['CY_id'], [1])
        self.assertEqual(reg_info[1]['CY_id'], [2])
        self.assertEqual(reg_info[2]['CY_id'], [3])

    
    def test_no_CY_slabs_left(self):
        """
        BY: |----20----||----20----||----20----|
        CY: |---18---||------26------|

        Expected: last BY slab mapped to nothing
        """

        BY_info = [
            {   
                'id': 1,
                'offset': 0,
                'length': 20
            },
            {   
                'id': 2,
                'offset': 20,
                'length': 20
            },
            {
                'id': 3,
                'offset': 40,
                'length': 20
            }
        ]
        
        CY_info = [
            {
                'id': 1,
                'offset': 0,
                'length': 18
            },
            {
                'id': 2,
                'offset': 18,
                'length': 26
            }
        ]
        
        reg_info = reg.classify(BY_info, CY_info)

        self.assertEqual(reg_info[0]['CY_id'], [1])
        self.assertEqual(reg_info[1]['CY_id'], [2])
        self.assertEqual(reg_info[2]['CY_id'], [])


    def test_no_BY_slabs_left(self):
        """
        BY: |----20----||----20----|
        CY: |---18---||------26------||---18---|

        Expected: last CY slab mapped to nothing
        """

        BY_info = [
            {   
                'id': 1,
                'offset': 0,
                'length': 20
            },
            {   
                'id': 2,
                'offset': 20,
                'length': 20
            }
        ]
        
        CY_info = [
            {
                'id': 1,
                'offset': 0,
                'length': 18
            },
            {
                'id': 2,
                'offset': 18,
                'length': 26
            },
            {
                'id': 3,
                'offset': 44,
                'length': 18
            }
        ]
        
        reg_info = reg.classify(BY_info, CY_info)

        self.assertEqual(reg_info[0]['CY_id'], [1])
        self.assertEqual(reg_info[1]['CY_id'], [2])
    

    def test_ambiguous_case_simple(self):
        """
        BY: |----20----||----18----||----22----|
        CY: |----------------60----------------|

        Expected: all BY slabs must align with the CY slab.
        """
            
        BY_info = [
            {   
                'id': 1,
                'offset': 0,
                'length': 20
            },
            {   
                'id': 2,
                'offset': 20,
                'length': 18
            },
            {
                'id': 3,
                'offset': 38,
                'length': 22
            }
        ]
        
        CY_info = [
            {
                'id': 1,
                'offset': 0,
                'length': 60
            }
        ]
        
        reg_info = reg.classify(BY_info, CY_info)

        # self.assertEqual(reg_info[0]['CY_id'], [])
        # self.assertEqual(reg_info[1]['CY_id'], [])
        # self.assertEqual(reg_info[2]['CY_id'], [])
        
        # # if using both conditions
        self.assertEqual(reg_info[0]['CY_id'], [1])
        self.assertEqual(reg_info[1]['CY_id'], [1])
        self.assertEqual(reg_info[2]['CY_id'], [1])


    def test_ambiguous_case(self):
        """
        BY: |----20----||--6--||---18---||----20----|
        CY: |----24---------||-------40-------------|

        Expected: the first BY 20 slab must align with the CY 24 slab. The 
        fourth BY 20 slab must align with the CY 40 slab. What about the 2nd 
        and 3rd BY 20 slabs? 
        """

        BY_info = [
            {   
                'id': 1,
                'offset': 0,
                'length': 20
            },
            {   
                'id': 2,
                'offset': 20,
                'length': 6
            },
            {
                'id': 3,
                'offset': 26,
                'length': 18
            },
            {
                'id': 4,
                'offset': 44,
                'length': 20
            }
        ]
        
        CY_info = [
            {
                'id': 1,
                'offset': 0,
                'length': 24
            },
            {
                'id': 2,
                'offset': 24,
                'length': 40
            }
        ]
        
        reg_info = reg.classify(BY_info, CY_info)

        # self.assertEqual(reg_info[0]['CY_id'], [1])
        # self.assertEqual(reg_info[1]['CY_id'], [])
        # self.assertEqual(reg_info[2]['CY_id'], [])
        # self.assertEqual(reg_info[3]['CY_id'], [2])
        
        # with overlapping conditions going both ways
        self.assertEqual(reg_info[0]['CY_id'], [1])
        self.assertEqual(reg_info[1]['CY_id'], [1])
        self.assertEqual(reg_info[2]['CY_id'], [2])
        self.assertEqual(reg_info[3]['CY_id'], [2])