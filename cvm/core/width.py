"""
Author: Girish Hari
Contributor: Jordan Fung, Hoang Ho
Lab: tsai-research
Repo: https://github.gatech.edu/tsai-research/CrackVectorModel
"""

import math

import numpy as np

from cvm.config import settings


def compute_crack_width(branches_xy, thresh, image):
    branches_width = []
    branches_width_xy = []

    for branch_xy in branches_xy:
        branch_width_measurement = []
        branch_width_xy = []

        for j in range(1, len(branch_xy) - 1):
            center_x, center_y = branch_xy[j]
            previous_x, previous_y = branch_xy[j - 1]
            next_x, next_y = branch_xy[j + 1]

            vector_positive = np.array([next_x - previous_x, next_y - previous_y])
            orthogonal_positive = np.array([-vector_positive[1], vector_positive[0]])
            normalized_orthogonal_positive = orthogonal_positive / np.linalg.norm(orthogonal_positive)

            # Positive orthogonal direction
            pos_weight = 0.25
            neighb = np.array([center_x, center_y]) + pos_weight * normalized_orthogonal_positive
            neighb_value = 0

            # TODO: Use numpy
            while 0 <= neighb[0] and neighb[0] < image.shape[0] and 0 <= neighb[1] and neighb[1] < image.shape[1]:
                neighb_value = image[int(math.floor(neighb[0])), int(math.floor(neighb[1]))]
                if neighb_value > thresh:
                    pos_weight += 0.5
                    if pos_weight > settings.MAX_WIDTH_EXPAND:
                        break
                else:
                    break

                neighb = np.array([center_x, center_y]) + pos_weight * normalized_orthogonal_positive

            positive_side_xy = neighb

            # Negative orthogonal direction
            neg_weight = 0.25
            normalized_orthogonal_negative = -normalized_orthogonal_positive
            neighb = np.array([center_x, center_y]) + neg_weight * normalized_orthogonal_negative
            neighb_value = 0

            # TODO: Use numpy
            while 0 <= neighb[0] and neighb[0] < image.shape[0] and 0 <= neighb[1] and neighb[1] < image.shape[1]:
                neighb_value = image[int(math.floor(neighb[0])), int(math.floor(neighb[1]))]

                if neighb_value > thresh:
                    neg_weight += 0.5

                    if neg_weight > settings.MAX_WIDTH_EXPAND:
                        break

                else:
                    break

                neighb = np.array([center_x, center_y]) + neg_weight * normalized_orthogonal_negative

            negative_side_xy = neighb
            w = pos_weight + neg_weight
            branch_width_measurement.append(w)

            branch_width_xy.append([positive_side_xy, negative_side_xy])

        branches_width.append(np.asarray(branch_width_measurement, dtype=np.float32))
        if len(branch_width_xy) > 0:
            branches_width_xy.append(np.asarray(branch_width_xy, dtype=np.int32))
        else:
            branches_width_xy.append(np.empty(shape=(0, 0, 0), dtype=np.int32))

    return branches_width_xy, branches_width
