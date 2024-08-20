from enum import Enum  

class OverlapType(Enum):
    """Enum to specify the type of overlap between two slabs"""
    NO_OVERLAP = 0
    FULL_OVERLAP = 1
    # Overlap / BY length >= r
    BASE_MAJORITY_OVERLAP = 2
    # Overlap / CY length >= r
    CURRENT_MAJORITY_OVERLAP = 3
    MINOR_OVERLAP = 4   

class AlignmentType(Enum):
    """Enum to specify the type of replacement done based on the alignment of 
    CY and BY joints"""
    PARTIAL_ALIGN = 0
    JOINT_REPLACEMENT = 1  
    PARTIAL_INTERIOR = 2
    PARTIAL_EXTERIOR = 3
    FULL_TWO_EXTERIOR = 4
    FULL_ONE_EXTERIOR = 5
    FULL_TWO_ALIGN = 6
    PARTIAL_EXTERIOR_MINOR = 7



def overlap_offset_length(s1_offset: float, s1_length: float,
                          s2_offset: float, s2_length: float):
    """Calculates the overlap given the offset and length of two slabs. This is
    a calculation in 1D space.

    Args:
        s1_offset (float): The offset of the first slab/object
        s1_length (float): The length of the first slab/object
        s2_offset (float): The offset of the second slab/object
        s2_length (float): The length of the second slab/object
    Returns: 
        float: length of the overlap between the two slabs/objects
    """
    return max(0, min(s1_offset + s1_length, 
                      s2_offset + s2_length) - max(s1_offset, s2_offset))


def belongs_to(s1_offset: float, s1_length: float,
               s2_offset: float, s2_length: float,
               threshold: float = 0.5):
    """Determines if the first slab/object belongs to the second slab/object.
    This is a calculation in 1D space.

    Args:
        s1_offset (float): The offset of the first slab/object (BY)
        s1_length (float): The length of the first slab/object (BY)
        s2_offset (float): The offset of the second slab/object (CY)
        s2_length (float): The length of the second slab/object (CY)
        threshold (float): Percent of overlap to consider as majority overlap.
        default is 0.5
    Returns:
        OverlapType: The type of overlap between the two slabs/objects
    """
    overlap = overlap_offset_length(s1_offset, s1_length, s2_offset, s2_length)
    if overlap == 0:
        return OverlapType.NO_OVERLAP
    elif (abs(s1_offset - s2_offset) < 610 and 
          abs((s1_offset + s1_length) - (s2_offset + s2_length)) < 610):
        return OverlapType.FULL_OVERLAP
    elif overlap >= float(s1_length) * threshold:
        return OverlapType.BASE_MAJORITY_OVERLAP
    elif overlap >= float(s2_length) * threshold:
        return OverlapType.CURRENT_MAJORITY_OVERLAP
    else:
        return OverlapType.MINOR_OVERLAP
        


def replacement_type(interior: int, 
                     exterior: int, 
                     aligned: int, 
                     replacement_slab_length: float,
                     replacement_ratio: float,
                     replacement_threshold: float = 0.25):
    """Determines the type of replacement done based on the alignemnt of CY and
    BY joints

    Args:
        interior (int): number of CY interior joints
        exterior (int): number of CY exterior joints
        replacement_ratio (float): ratio of replaced CY slab length to BY slab length
        aligned (int): number of CY aligned joints
        replacement_slab_length (float): length of the replacing CY slab
        replacement_threshold (float): threshold to determine if the CY slab
        replaces the BY slab in the partial exeterior case. Default is 0.25 
    
    Returns:
        AlignmentType: The type of replacement done based on the alignment of CY
        and BY joints
    """
    if aligned == 2 and exterior == 0 and interior == 0:
        return AlignmentType.FULL_TWO_ALIGN
    
    if aligned == 1 and exterior == 1 and interior == 0:
        return AlignmentType.FULL_ONE_EXTERIOR
    
    if aligned == 0 and exterior == 2 and interior == 0:
        return AlignmentType.FULL_TWO_EXTERIOR
    
    if interior >= 2:
        return AlignmentType.PARTIAL_INTERIOR
    
    if aligned == 2 and interior == 1 and exterior == 0:
        return AlignmentType.PARTIAL_ALIGN
    
   
    if replacement_ratio >= replacement_threshold:  
        #print(replacement_ratio, replacement_threshold)  
        return AlignmentType.PARTIAL_EXTERIOR

    if replacement_slab_length <= 2400:
        return AlignmentType.JOINT_REPLACEMENT

    return AlignmentType.PARTIAL_EXTERIOR_MINOR  

    

def percent_BY_overlap(s1_offset: float, s1_length: float,
                       s2_offset: float, s2_length: float):
    """Calculates the percentage of the first slab/object that overlaps with the
    second slab/object. This is a calculation in 1D space.

    Args:
        s1_offset (float): The offset of the first slab/object (BY)
        s1_length (float): The length of the first slab/object (BY)
        s2_offset (float): The offset of the second slab/object (CY)
        s2_length (float): The length of the second slab/object (CY)
    Returns:
        float: The percentage of the first slab/object that overlaps with the
        second slab/object
    """
    overlap = overlap_offset_length(s1_offset, s1_length, s2_offset, s2_length)
    return float(overlap) / s1_length
