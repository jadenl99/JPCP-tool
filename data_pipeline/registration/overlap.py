from enum import Enum  

class OverlapType(Enum):
    """Enum to specify the type of overlap between two slabs"""
    NO_OVERLAP = 0
    FULL_OVERLAP = 1
    BASE_MAJORITY_OVERLAP = 2
    CURRENT_MAJORITY_OVERLAP = 3
    MINOR_OVERLAP = 4

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
               s2_offset: float, s2_length: float):
    """Determines if the first slab/object belongs to the second slab/object.
    This is a calculation in 1D space.

    Args:
        s1_offset (float): The offset of the first slab/object (BY)
        s1_length (float): The length of the first slab/object (BY)
        s2_offset (float): The offset of the second slab/object (CY)
        s2_length (float): The length of the second slab/object (CY)
    Returns:
        OverlapType: The type of overlap between the two slabs/objects
    """
    overlap = overlap_offset_length(s1_offset, s1_length, s2_offset, s2_length)
    if overlap == 0:
        return OverlapType.NO_OVERLAP
    elif (abs(s1_offset - s2_offset) < 610 and 
          abs((s1_offset + s1_length) - (s2_offset + s2_length)) < 610):
    # overlap >= s1_length - 1220 and abs(s1_length - s2_length) < 610:
        return OverlapType.FULL_OVERLAP
    elif overlap >= float(s1_length) / 2:
        return OverlapType.BASE_MAJORITY_OVERLAP
    elif overlap >= float(s2_length) / 2:
        return OverlapType.CURRENT_MAJORITY_OVERLAP
    else:
        return OverlapType.MINOR_OVERLAP
        



