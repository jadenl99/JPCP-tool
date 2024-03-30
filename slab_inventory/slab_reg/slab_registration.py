class SlabRegistration:
    def __init__(self):
        self.PERCENT_REQ = 0.5


    def membership(self, offsetBY, lengthBY, offsetCY, lengthCY):
        """Determines membership of current year slab

        Args:
            offsetBY (float): y_offset of base year slab
            lengthBY (float): length of base year slab
            offsetCY (float): y_offset of current year slab
            lengthCY (float): length of current year slab

        Returns:
            bool: membership of current year slab
        """
        percent_overlap_CY = self.calc_percent_overlap_CY(
            offsetBY, lengthBY, offsetCY, lengthCY
            )
        percent_overlap_BY = self.calc_percent_overlap_BY(
            offsetBY, lengthBY, offsetCY, lengthCY
            )
        return percent_overlap_CY >= self.PERCENT_REQ or \
            percent_overlap_BY >= self.PERCENT_REQ
    
    def classify(self, BY_info, CY_info):
        """Classifies what CY slabs correspond to BY slabs

        Args:
            BY_info (list): base year slab info
            CY_info (list): current year slab info

        Returns:
            list: list of base year slabs and their membership to current 
            year slabs
        """
        slab_membership = [{'base_id': i + 1, 'CY_id': []} for i in range(len(BY_info))]
        BY_index = 0
        CY_index = 0

        while BY_index < len(BY_info) and CY_index < len(CY_info):
            BY_offset = BY_info[BY_index]['offset']
            BY_length = BY_info[BY_index]['length']
            CY_offset = CY_info[CY_index]['offset']
            CY_length = CY_info[CY_index]['length']
            
            if self.membership(BY_offset, BY_length, CY_offset, CY_length):
                slab_membership[BY_index]['CY_id'].append(CY_index + 1)
            
            if BY_offset + BY_length <= CY_offset + CY_length:
                BY_index += 1
            else:
                CY_index += 1
        
        return slab_membership


    def calc_overlap(self, offsetBY, lengthBY, offsetCY, lengthCY):
        """Calculates overlap between two slabs

        Args:
            offsetBY (float): y_offset of base year slab
            lengthBY (float): length of base year slab
            offsetCY (float): y_offset of current year slab
            lengthCY (float): length of current year slab

        Returns:
            float: overlap between two slabs
        """
        startBY = offsetBY
        endBY = offsetBY + lengthBY
        startCY = offsetCY
        endCY = offsetCY + lengthCY

        overlap = max(0, min(endBY, endCY) - max(startBY, startCY))
        return overlap
    

    def calc_percent_overlap_BY(self, offsetBY, lengthBY, offsetCY, lengthCY):
        """Calculates percent overlap of base year slab

        Args:
            offsetBY (float): y_offset of base year slab
            lengthBY (float): length of base year slab
            offsetCY (float): y_offset of current year slab
            lengthCY (float): length of current year slab

        Returns:
            float: percent overlap of base year slab
        """
        overlap = self.calc_overlap(offsetBY, lengthBY, offsetCY, lengthCY)
        percent_overlap = overlap / lengthBY
        return percent_overlap
    

    def calc_percent_overlap_CY(self, offsetBY, lengthBY, offsetCY, lengthCY):
        """Calculates percent overlap of current year slab

        Args:
            offsetBY (float): y_offset of base year slab
            lengthBY (float): length of base year slab
            offsetCY (float): y_offset of current year slab
            lengthCY (float): length of current year slab

        Returns:
            float: percent overlap of current year slab
        """
        overlap = self.calc_overlap(offsetBY, lengthBY, offsetCY, lengthCY)
        percent_overlap = overlap / lengthCY
        return percent_overlap
    


        

if __name__ == '__main__':
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

    reg_info = SlabRegistration()

    print(reg_info.classify(BY_info, CY_info))