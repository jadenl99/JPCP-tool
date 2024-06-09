"""
Author: Girish Hari
Contributor: Hoang Ho, Jordan Fung
Lab: tsai-research
Repo: https://github.gatech.edu/tsai-research/CrackVectorModel
"""

import copy
import logging

import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
from skimage import measure, morphology

from cvm.bwmorph import get_branches_mask, get_endpoints_mask
from cvm.types import Np2dArray

logger = logging.getLogger(__name__)


def get_crack_skeleton(seg_img: np.ndarray) -> np.ndarray:
    """Return the binary skeleton of the provided binary segmentation image."""

    crack_skeleton = morphology.thin(seg_img).astype(np.uint8)
    return crack_skeleton


def get_intersections(crack_skeleton: np.ndarray, image_size):
    """Return intersections using `get_branches_mask` operation"""

    branch_points = get_branches_mask(crack_skeleton)

    blurred_kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], np.uint8)

    # isolate cells that have no neighbors
    centered_kernel = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]], np.uint8)
    hitormiss1 = cv.morphologyEx(
        branch_points.astype(np.uint8),
        cv.MORPH_ERODE,
        centered_kernel,
        borderValue=0,
    )
    hitormiss2 = cv.morphologyEx(
        cv.bitwise_not(branch_points.astype(np.uint8)),
        cv.MORPH_ERODE,
        blurred_kernel,
        borderValue=0,
    )
    no_neighbor_cells = cv.bitwise_and(hitormiss1, hitormiss2)

    # multi neighbor cells
    laplacian_kernel = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], np.uint8)
    # Apply convolution
    result = cv.filter2D(
        branch_points.astype(np.uint8),
        -1,
        laplacian_kernel,
        borderType=cv.BORDER_CONSTANT,
    )
    multi_neighbor_cells = np.where((crack_skeleton == 1) & (result >= 2), 1, 0)

    left_over_multineighbor_intersections = np.logical_and(
        branch_points,
        np.logical_not(np.where((crack_skeleton == 1) & (result >= 1), 1, 0)),
    )

    # multi neighbor intersection
    kernel4 = np.array([[1, 0, 1], [0, 0, 0], [1, 0, 1]], np.uint8)
    # Apply convolution
    result = cv.filter2D(
        branch_points.astype(np.uint8),
        -1,
        laplacian_kernel,
        borderType=cv.BORDER_CONSTANT,
    )
    multi_neighbor_cells = np.where((crack_skeleton == 1) & (result >= 2), 1, 0)

    # can maybe turn this into a convolution in the future with 4 kernals and a bunch of XORs
    # consolidate intersections that have 2 neighbor intersections
    one_neighbor_kernel = np.array([[-1, 1, -1], [1, 1, 1], [-1, 1, -1]], np.uint8)
    result = cv.filter2D(
        branch_points.astype(np.uint8),
        -1,
        one_neighbor_kernel,
        borderType=cv.BORDER_CONSTANT,
    )
    one_neighbor_intersection = np.where((crack_skeleton == 1) & (result == 2), 1, 0)
    one_neighbor_kernel_final = np.array([[0, 1, 0], [1, 1, 0], [0, 0, 0]], np.uint8)
    result = cv.filter2D(
        branch_points.astype(np.uint8),
        -1,
        one_neighbor_kernel_final,
        borderType=cv.BORDER_CONSTANT,
    )
    one_neighbor_intersection = np.where((crack_skeleton == 1) & (result == 2), 1, 0)

    # TODO: Convert this loops into numpy
    for j in range(image_size[1]):
        for i in range(image_size[0]):
            if (
                one_neighbor_intersection[j][i] == 1
                and i - 1 >= 0
                and i + 1 < image_size[0]
                and j - 1 >= 0
                and j + 1 < image_size[1]
            ):
                if (
                    multi_neighbor_cells[j + 1][i] == 1
                    or multi_neighbor_cells[j][i + 1] == 1
                    or multi_neighbor_cells[j - 1][i] == 1
                    or multi_neighbor_cells[j][i - 1] == 1
                ):
                    one_neighbor_intersection[j][i] = 0

    # combine single and multi neighbor intersections
    final_intersections = crack_skeleton & (
        multi_neighbor_cells | left_over_multineighbor_intersections | no_neighbor_cells | one_neighbor_intersection
    )

    # Get x, y indices of branch points
    branch_points_idx = np.where(final_intersections)

    # Transpose indices to (x, y) format
    branch_points_xy = np.column_stack((branch_points_idx[1], branch_points_idx[0]))

    return branch_points_idx, branch_points_xy


def remove_intersections(crack_skeleton: np.ndarray, intersections_idx):
    # Copy the input skeleton to avoid modifying the original
    updated_crack_skeleton = np.copy(crack_skeleton)

    # Remove intersections using provided indices
    updated_crack_skeleton[intersections_idx] = 0

    # Get linear indices of the updated crack skeleton
    crack_skeleton_idx = np.argwhere(updated_crack_skeleton)

    return updated_crack_skeleton, crack_skeleton_idx


def find_neighbors(
    intersections_idx: np.ndarray, image_size, crack_skeleton_idx: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    # Initialize list for collecting all intersection neighbors
    crack_skeleton_idx = (crack_skeleton_idx.T[0], crack_skeleton_idx.T[1])
    intersections_idx = np.ravel_multi_index((intersections_idx[1], intersections_idx[0]), image_size)
    crack_skeleton_idx = np.ravel_multi_index((crack_skeleton_idx[1], crack_skeleton_idx[0]), image_size)
    neighbors_idx = []

    offsets = [-1, 1, -image_size[1], image_size[1]]

    # Loop through each intersection index to find its neighbors
    for intersection_idx in intersections_idx:
        # Find neighbors for the current intersection
        intersection_neighbors = [intersection_idx + offset for offset in offsets]

        # Append intersection neighbors to the list
        neighbors_idx.extend(intersection_neighbors)

    # Filter unique neighbors
    neighbors_idx = list(set(neighbors_idx))

    # Remove intersections from neighbors
    neighbors_idx = [idx for idx in neighbors_idx if idx not in intersections_idx]

    # Retain only those neighbors that are part of the crack skeleton
    neighbors_idx = np.array([idx for idx in neighbors_idx if idx in crack_skeleton_idx], dtype=np.int32)

    # Convert linear indices to x, y coordinates
    x, y = np.unravel_index(neighbors_idx, image_size)
    neighbors_idx = (y, x)

    # Combine x and y coordinates
    neighbors_xy = np.column_stack((x, y))

    return neighbors_idx, neighbors_xy


def split_to_branches(crack_skeleton: np.ndarray) -> list[Np2dArray]:
    # Label connected components (branches) in the binary skeleton
    labeled_branches = measure.label(crack_skeleton, connectivity=2)

    # Use regionprops to get the list of pixel indices for each branch
    branches_idx = [region.coords for region in measure.regionprops(labeled_branches)]

    return branches_idx


def add_neighbors_back_to_branches(neighbors_idx, branches_idx, image):
    modified_neighbors_idx = np.array([neighbors_idx[0], neighbors_idx[1]]).T
    special_pixels_idx = []

    for i, branch in enumerate(branches_idx):
        if len(branch) >= 2:
            temp_image = np.zeros_like(image)
            temp_image[branch.T[0], branch.T[1]] = 1

            ends = get_endpoints_mask(temp_image)

            ends_idx = np.where(ends)

            if len(ends_idx[0]) > 2:
                logger.debug("Hard warning (this branch is skipped): more than 2 end points " "found in a branch")
                continue
            # elif len(ends_idx[0]) < 2:
            #     logger.warning('Hard warning (this branch is skipped): less than 2 end points found in a branch')
            #     continue

            for j in range(len(ends_idx[0])):
                end_idx = (ends_idx[0][j], ends_idx[1][j])
                end_surroundings_idx = [
                    [end_idx[0] - 1, end_idx[1]],
                    [end_idx[0] + 1, end_idx[1]],
                    [end_idx[0], end_idx[1] - 1],
                    [end_idx[0], end_idx[1] + 1],
                    [end_idx[0] - 1, end_idx[1] - 1],
                    [end_idx[0] + 1, end_idx[1] + 1],
                    [end_idx[0] - 1, end_idx[1] + 1],
                    [end_idx[0] + 1, end_idx[1] - 1],
                ]

                selected_neighbors_idx = np.array(
                    [np.array(idx) for idx in end_surroundings_idx if idx in modified_neighbors_idx.tolist()]
                )

                if len(selected_neighbors_idx) > 1:
                    logger.debug(
                        "Soft warning (additional neighbors are added to branch): "
                        "more than 1 neighbor found for a normal branch end"
                    )
                if len(selected_neighbors_idx) == 0:
                    continue

                branches_idx[i] = np.vstack([branches_idx[i], selected_neighbors_idx])
                modified_neighbors_idx = np.array(
                    [idx for idx in modified_neighbors_idx.tolist() if idx not in selected_neighbors_idx.tolist()]
                )
        elif len(branch) == 1:
            center_idx = branch[0]
            end_surroundings_idx = [
                [center_idx[0] - 1, center_idx[1]],
                [center_idx[0] + 1, center_idx[1]],
                [center_idx[0], center_idx[1] - 1],
                [center_idx[0], center_idx[1] + 1],
                [center_idx[0] - 1, center_idx[1] - 1],
                [center_idx[0] + 1, center_idx[1] + 1],
                [center_idx[0] - 1, center_idx[1] + 1],
                [center_idx[0] + 1, center_idx[1] - 1],
            ]

            selected_neighbors_idx = np.array(
                [idx for idx in end_surroundings_idx if idx in modified_neighbors_idx.tolist()]
            )

            if len(selected_neighbors_idx) > 2:
                logger.debug(
                    "Soft warning (saved as special pixels and additional neighbors "
                    "are added to this single pixel branch): more than 2 neighbors found for a single pixel branch"
                )
                special_pixels_idx.extend(selected_neighbors_idx)
            elif len(selected_neighbors_idx) == 0:
                continue

            branches_idx[i] = np.vstack([branches_idx[i], selected_neighbors_idx])
            modified_neighbors_idx = np.array(
                [idx for idx in modified_neighbors_idx.tolist() if idx not in selected_neighbors_idx.tolist()]
            )

    return modified_neighbors_idx, special_pixels_idx, branches_idx


def convert_remaining_neighbors_as_single_pixel_branches(
    modified_neighbors_idx: np.ndarray, branches_idx: list[np.ndarray]
):
    branches_idx = copy.deepcopy(branches_idx)

    for i in modified_neighbors_idx:
        branches_idx.append(np.array([i]))
    # return np.array(branches_idx)
    return branches_idx


def connect_branches_with_intersections(branches_idx: list[np.ndarray], image: np.ndarray, intersections_idx):
    special_pixels_1_idx = []
    special_pixels_2_idx = []
    use_of_intersections = []

    for i, branch in enumerate(branches_idx):
        if len(branch) >= 2:
            temp_image = np.zeros_like(image)
            temp_image[branch.T[0], branch.T[1]] = 1

            ends = get_endpoints_mask(temp_image)
            ends_idx = np.where(ends)

            if len(ends_idx[0]) > 2:
                logger.debug("Hard warning (this branch is skipped): more than 2 end points found in a branch")
                continue
            # elif len(ends_idx[0]) < 2:
            #     logger.warning('Hard warning (this branch is skipped): less than 2 end points found in a branch')
            #     continue

            for j in range(len(ends_idx[0])):
                end_idx = (ends_idx[0][j], ends_idx[1][j])
                end_surroundings_idx = [
                    [end_idx[1] - 1, end_idx[0]],
                    [end_idx[1] + 1, end_idx[0]],
                    [end_idx[1], end_idx[0] - 1],
                    [end_idx[1], end_idx[0] + 1],
                    [end_idx[1] - 1, end_idx[0] - 1],
                    [end_idx[1] + 1, end_idx[0] + 1],
                    [end_idx[1] - 1, end_idx[0] + 1],
                    [end_idx[1] + 1, end_idx[0] - 1],
                ]

                selected_neighbors_idx = [idx for idx in end_surroundings_idx if idx in intersections_idx.tolist()]

                if len(selected_neighbors_idx) > 1:
                    logger.debug(
                        "Soft warning (saved as special pixels): "
                        "an end point connects to more than one intersection "
                        "(only one intersection point will be connected with the branch)"
                    )
                    special_pixels_1_idx.extend(selected_neighbors_idx)
                    selected_neighbors_idx = [selected_neighbors_idx[0]]
                elif len(selected_neighbors_idx) == 0:
                    continue

                branches_idx[i] = np.vstack([branches_idx[i], list(reversed(selected_neighbors_idx[0]))])
                use_of_intersections.extend(selected_neighbors_idx)
        elif len(branch) == 1:
            end_idx = (branch[0][0], branch[0][1])
            end_surroundings_idx = [
                [end_idx[1] - 1, end_idx[0]],
                [end_idx[1] + 1, end_idx[0]],
                [end_idx[1], end_idx[0] - 1],
                [end_idx[1], end_idx[0] + 1],
                [end_idx[1] - 1, end_idx[0] - 1],
                [end_idx[1] + 1, end_idx[0] + 1],
                [end_idx[1] - 1, end_idx[0] + 1],
                [end_idx[1] + 1, end_idx[0] - 1],
            ]
            selected_neighbors_idx = [idx for idx in end_surroundings_idx if idx in intersections_idx.tolist()]

            if len(selected_neighbors_idx) > 2:
                logger.debug(
                    "Soft warning (saved as special pixels and additional neighbors "
                    "are added to this single pixel branch): more than 2 neighbors found "
                    "for a single pixel branch"
                )
                special_pixels_2_idx.extend(selected_neighbors_idx)
            if len(selected_neighbors_idx) == 0:
                continue

            branches_idx[i] = np.vstack([branches_idx[i], np.array(np.flip(selected_neighbors_idx))])
            use_of_intersections.extend(selected_neighbors_idx)

    # return np.array(branches_idx)
    return branches_idx


def linearize_branches(branches_idx, image):
    linearized_branches_idx = []
    special_pixels_1_idx = []  # a crack branch has less than 2 end points.
    special_pixels_2_idx = []  # a crack branch has more than 2 end points.

    for branch in branches_idx:
        # Branches after being connected with intersections should contain more than 2 pixels
        if len(branch) < 2:
            logger.debug("Step 5: Hard warning (this branch is skipped): " "this branch contains only one pixel.")
            continue

        # Branches containing more than 2 pixels
        temp_image = np.zeros(image.shape, dtype=bool)
        temp_image[branch.T[0], branch.T[1]] = 1
        ends = get_endpoints_mask(temp_image)
        ends_idx = np.where(ends)

        # Check the number of end points
        if len(ends_idx[0]) < 2:
            logger.debug(
                "Step 5: Hard warning (this branch is skipped): "
                "this multi-pixel branch contains less than 2 end points"
            )
            special_pixels_1_idx.extend(branch)
            continue
        elif len(ends_idx[0]) > 2:
            # End points can be greater than 2 if connected with more than 3 ends
            logger.debug(
                "Step 5: Hard warning (this branch is skipped): "
                "this multi-pixel branch contains more than 2 end points"
            )
            special_pixels_2_idx.extend(branch)
            continue

        # Analyze connectivity for normal branches that have two end points
        start_idx = ends_idx[0][0], ends_idx[1][0]
        # end_idx = ends_idx[0][1], ends_idx[1][1]
        cur_idx = start_idx
        sorted_branch_idx = [cur_idx]
        branch_set = set(map(tuple, branch))
        branch_set.remove(start_idx)

        while len(branch_set) > 0:
            surroundings = [
                (cur_idx[0] - 1, cur_idx[1]),
                (cur_idx[0] + 1, cur_idx[1]),
                (cur_idx[0], cur_idx[1] - 1),
                (cur_idx[0], cur_idx[1] + 1),
                (cur_idx[0] - 1, cur_idx[1] - 1),
                (cur_idx[0] + 1, cur_idx[1] + 1),
                (cur_idx[0] - 1, cur_idx[1] + 1),
                (cur_idx[0] + 1, cur_idx[1] - 1),
            ]

            selected_neighbors = [neighbor for neighbor in surroundings if neighbor in branch_set]

            if len(selected_neighbors) == 2 or len(selected_neighbors) == 1:
                selected_neighbors = selected_neighbors[0]
            elif not selected_neighbors or len(selected_neighbors) > 2:
                logger.debug(
                    "Step 5: Hard warning (this branch is skipped): "
                    "this branch is not linearizable because a pixel is connected to "
                    "more than 2 pixels when routing to the next step."
                )
                break

            sorted_branch_idx.append(selected_neighbors)
            branch_set.remove(selected_neighbors)
            cur_idx = selected_neighbors

        # sorted_branch_idx.append(end_idx)
        linearized_branches_idx.append(sorted_branch_idx)

    return linearized_branches_idx, special_pixels_1_idx, special_pixels_2_idx


def plot_result_of_crack_length_and_width(
    rng_image, branches_xy, intersections_xy, lon1, lon2, lat1, lat2, branches_length, branches_width, **kwargs
):
    is_plain = "plain" in kwargs and kwargs["plain"]

    # Prepare the figure and axis
    dpi = 64
    width, height = rng_image.shape[:2]
    figsize = width / dpi, height / dpi
    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(rng_image, cmap="gray")

    # Set plot size
    if not is_plain:
        fig.set_figheight(16)
        fig.set_figwidth(16)

    # Plot branches

    np.random.seed(42)
    for branch_xy in branches_xy:
        if len(branch_xy) > 0:
            branch_xy = np.array(branch_xy)
            ax.plot(branch_xy[:, 1], branch_xy[:, 0], linewidth=3, color=np.random.rand(3))

    # Plot intersections
    if len(intersections_xy) > 0:
        ax.plot(
            intersections_xy[:, 1],
            intersections_xy[:, 0],
            "or",
            markersize=5,
            markerfacecolor="r",
            label="Intersections",
        )

    if is_plain:
        # Plot width measurement (the green bars)
        lons = np.array([np.array(lon1).T, np.array(lon2).T, [np.nan] * len(lon2)])
        lats = np.array([np.array(lat1).T, np.array(lat2).T, [np.nan] * len(lat2)])
        ax.plot(lats.T.flatten(), lons.T.flatten(), linewidth=0.5, color="green")

    # Plot length and width results for each crack
    lons = []
    lats = []
    labels = []

    for i in range(len(branches_length)):
        branch_xy = np.array(branches_xy[i])
        indtxt = branch_xy.shape[0] // 2
        lons.append(branch_xy[indtxt, 0])
        lats.append(branch_xy[indtxt, 1])
        labels.append(f"L{branches_length[i]:.1f}-W{np.mean(branches_width[i]):.1f}")

    # Faster plotting technology: limit the labels only to the visible axes area
    # ax_limits = ax.get_xlim(), ax.get_ylim()
    # valid_idx = np.where((np.array(lons) >= ax_limits[0][0]) & (np.array(lons) <= ax_limits[0][1]) &
    #                      (np.array(lats) >= ax_limits[1][0]) & (np.array(lats) <= ax_limits[1][1]))[0]

    if is_plain:
        ax.set_axis_off()

    if is_plain:
        for i in range(len(lons)):
            ax.text(lats[i], lons[i], labels[i], color="yellow")

    if not is_plain:
        # Plot summarized results
        total_crack_length = sum(branches_length)
        num_branches = len(branches_xy)
        num_intersections = len(intersections_xy)

        summary_text = f"total crack length: {total_crack_length:.2f} mm\n"
        summary_text += f"number of branches: {num_branches}\n"
        summary_text += f"number of intersections: {num_intersections}\n"

        props = {"boxstyle": "round", "facecolor": "grey", "alpha": 0.15}  # bbox features
        ax.text(
            0.1,
            0.85,
            summary_text,
            color="black",
            backgroundcolor="white",
            transform=plt.gcf().transFigure,
            bbox=props,
        )
        plt.subplots_adjust(left=0.25)
        ax.legend()

    # Plot legend
    # if len(ax.get_legend().get_lines()) > 0:
