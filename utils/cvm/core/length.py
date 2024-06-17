"""
Author: Girish Hari
Contributor: Hoang Ho, Jordan Fung
Lab: tsai-research
Repo: https://github.gatech.edu/tsai-research/CrackVectorModel
"""

import numpy as np

from .base import (
    add_neighbors_back_to_branches,
    connect_branches_with_intersections,
    convert_remaining_neighbors_as_single_pixel_branches,
    find_neighbors,
    get_crack_skeleton,
    get_intersections,
    linearize_branches,
    remove_intersections,
    split_to_branches,
)


def get_crack_length_vector(seg_img: np.ndarray):
    # Get the image_size: (width, height)
    image_size = (seg_img.shape[1], seg_img.shape[0])

    # Step 2: Extract Crack Skeleton
    crack_skeleton = get_crack_skeleton(seg_img)

    ### Step 3: Split Continuous Crack Skeleton to Disconnected Crack Branches
    # Step 3.1: find intersections
    intersections_idx, intersections_xy = get_intersections(crack_skeleton, image_size)

    # step 3.2: remove intersections
    (
        crack_skeleton_no_intersection,
        crack_skeleton_no_intersection_idx,
    ) = remove_intersections(crack_skeleton, intersections_idx)

    # Step 3.3: find neighbors
    neighbors_idx, _ = find_neighbors(intersections_idx, image_size, crack_skeleton_no_intersection_idx)

    # Step 3.4: remove neighbors
    crack_skeleton_no_intersection[neighbors_idx] = 0

    # # Step 3.5: split to branches
    branches = split_to_branches(crack_skeleton_no_intersection)

    # Step 4: Branch connectivity refinement
    ## Step 4.1: adding neighbors back to branches
    (
        modified_neighbors_idx,
        _,
        branches_idx,
    ) = add_neighbors_back_to_branches(neighbors_idx, branches, crack_skeleton)

    ### Step 4.2: converting remaining neighbors back as single pixel branches and add back to branches
    branches_idx = convert_remaining_neighbors_as_single_pixel_branches(modified_neighbors_idx, branches_idx)

    ### Step 4.3: connecting branches with intersections
    branches_idx = connect_branches_with_intersections(branches_idx, crack_skeleton, intersections_xy)
    linearized_branches_idx = linearize_branches(branches_idx, crack_skeleton)[0]

    # Set the unit length of the pavement image (length that each pixel represents)
    pixel_length = 4  # unit in mm
    crack_length = compute_crack_length(
        linearized_branches_idx,
        pixel_length,
    )

    return crack_length


def compute_crack_length(branches_xy, pixel_length) -> np.ndarray[np.float32]:
    branches_length = []

    for branch_xy in branches_xy:
        if len(branch_xy) > 0:
            branch_xy = np.array(branch_xy)
            diffs = np.diff(branch_xy, axis=0)
            curve_length = np.sum(np.linalg.norm(diffs, axis=1)) * pixel_length
            branches_length.append(curve_length)

    return np.asarray(branches_length, dtype=np.float32)
