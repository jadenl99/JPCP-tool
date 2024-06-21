import logging
from itertools import chain
from pathlib import Path

import cv2 as cv
import geojson
import numpy as np

from cvm.config import settings
from cvm.exceptions import (
    ExistedGeojsonObjectError,
    GeojsonFormatError,
    MissingImageError,
    MissingImageOrGeojsonError,
    RedundantImageError,
)
from cvm.schemas import CrackVectorModel
from cvm.utils import geojson_to_geodataframe

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
from .length import compute_crack_length
from .width import compute_crack_width

logger = logging.getLogger(__name__)


class CvmBuilder:
    """
    A builder class for constructing a CrackVectorModel (CVM) using either segmentation or range images.

    Attributes:
        _seg_img (np.ndarray | None): The segmentation image used for constructing the CVM.
        _range_img (np.ndarray | None): The range image used for constructing the CVM.

    Methods:
        use_seg_img_path(seg_img_path): Sets the segmentation image using a file path.
        use_range_img_path(range_img_path): Sets the range image using a file path.
        use_seg_img_obj(seg_img_obj): Sets the segmentation image using an image object.
        use_range_img_obj(range_img_obj): Sets the range image using an image object.
        build(): Constructs and returns the CrackVectorModel.
        _get_binarized_range_img(range_img): A static method to binarize the range image.
    """

    def __init__(self):
        self._seg_img: np.ndarray | None = None
        self._range_img: np.ndarray | None = None
        self._geojson_obj: geojson.FeatureCollection | None = None

        self._use_rng_img_for_width_cal: bool = False

    def use_seg_img_path(self, path: str | Path, /) -> "CvmBuilder":
        """
        Sets the segmentation image for the CVM using a file path.

        Parameters:
            seg_img_path (str | Path): The file path to the segmentation image.

        Returns:
            CvmBuilder: The instance of this builder for chaining.
        """
        if self._seg_img is not None:
            raise RedundantImageError("Please use either use_seg_img_path OR use_seg_img_obj for segmentation image!")

        if not Path(path).exists():
            raise FileNotFoundError(f"Not found segmentation image at the given path {path}")

        self._seg_img = cv.imread(str(path), cv.IMREAD_GRAYSCALE)
        return self

    def use_range_img_path(self, path: str | Path, /) -> "CvmBuilder":
        """
        Sets the range image for the CVM using a file path.

        Parameters:
            range_img_path (str | Path): The file path to the range image.

        Returns:
            CvmBuilder: The instance of this builder for chaining.
        """
        if self._range_img is not None:
            raise RedundantImageError("Please use either use_range_img_path OR use_range_img_obj for range image!")

        if not Path(path).exists():
            raise FileNotFoundError(f"Not found range image at the given path {path}")

        _range_img = cv.imread(str(path), cv.COLOR_BGR2GRAY)[:, :, 0]
        self._range_img = 255 - _range_img
        return self

    def use_seg_img_obj(self, obj: np.ndarray, /) -> "CvmBuilder":
        """
        Sets the segmentation image for the CVM using an image object.

        Parameters:
            seg_img_obj (np.ndarray): The segmentation image object.

        Returns:
            CvmBuilder: The instance of this builder for chaining.
        """
        if self._seg_img is not None:
            raise RedundantImageError("Please use either use_seg_img_path OR use_seg_img_obj for segmentation image!")

        self._seg_img = obj
        return self

    def use_range_img_obj(self, obj: np.ndarray, /) -> "CvmBuilder":
        """
        Sets the range image for the CVM using an image object.

        Parameters:
            range_img_obj (np.ndarray): The range image object.

        Returns:
            CvmBuilder: The instance of this builder for chaining.
        """
        if self._range_img is not None:
            raise RedundantImageError("Please use either use_range_img_path OR use_range_img_obj for range image!")

        _range_img = cv.cvtColor(obj, cv.COLOR_BGR2GRAY)[:, :, 0]
        self._range_img = 255 - _range_img
        return self

    def use_geojson_obj(self, obj: geojson.FeatureCollection, /):
        """
        Sets the GeoJSON object for the CVM using a FeatureCollection object.

        Parameters:
            obj (geojson.FeatureCollection): The GeoJSON FeatureCollection object.

        Returns:
            CvmBuilder: The instance of this builder for chaining.
        """
        if self._geojson_obj is not None:
            raise ExistedGeojsonObjectError(
                "Please use either use_geojson_obj OR use_geojson_file for CVM's geojson format!"
            )
        self._geojson_obj = obj
        return self

    def use_geojson_file(self, file: str | Path, /):
        """
        A function to load a GeoJSON file, validate its format, and set it as the GeoJSON object.

        Parameters:
            file (str | Path): The path to the GeoJSON file.

        Raises:
            ExistedGeojsonObjectError: If a GeoJSON object already exists.
            FileNotFoundError: If the specified GeoJSON file path does not exist.
            GeojsonFormatError: If the GeoJSON file is not valid.

        Returns:
            CvmBuilder: The instance of this builder for chaining.
        """
        if self._geojson_obj is not None:
            raise ExistedGeojsonObjectError(
                "Please use either use_geojson_obj OR use_geojson_file for CVM's geojson format!"
            )

        if not Path(file).exists():
            raise FileNotFoundError(f"Not found geojson file at the given path {file}")

        with open(str(file)) as f:
            self._geojson_obj = geojson.load(f)
            if not self._geojson_obj.is_valid:
                raise GeojsonFormatError(f"Geojson file at {file} is not valid!")

        return self

    def use_range_image_for_width_calculation(self):
        """
        This method sets a flag to use a range image for width calculation. It raises a MissingImageError
        if the range image is not provided. It returns the current object.
        """
        if self._range_img is None:
            raise MissingImageError(
                "Must input a range image before using this method! Use use_range_* methods before this one!"
            )
        self._use_rng_img_for_width_cal = True

        return self

    def remove_lane_mark(self) -> "CvmBuilder":
        if self._seg_img is not None:
            return self

        if self._range_img is not None:
            return self

        raise NotImplementedError("remove_lane_mark is not yet implemented!")
        raise MissingImageError("No image to clean lane mark! Please use one method use_* before using this function.")

    def build(self) -> CrackVectorModel:
        """
        Constructs and returns the CrackVectorModel based on the provided images.

        Returns:
            CrackVectorModel: The constructed CrackVectorModel.

        Raises:
            MissingImageError: If neither a segmentation nor a range image has been set.
        """
        self._check_current_state()

        # Use geojson to construct the CVM ...
        if self._geojson_obj is not None:
            return self._build_from_geojson(self._geojson_obj)

        # ... or use image to construct the CVM
        img_size = (self._seg_img.shape[1], self._seg_img.shape[0])

        # Step 1: Extract Crack Skeleton
        crack_skeleton = get_crack_skeleton(self._seg_img)

        ### Step 2: Split Continuous Crack Skeleton to Disconnected Crack Branches
        # Step 2.1: find intersections
        intersections_idx, intersections_xy = get_intersections(crack_skeleton, img_size)

        # step 2.2: remove intersections
        (
            crack_skeleton_no_intersection,
            crack_skeleton_no_intersection_idx,
        ) = remove_intersections(crack_skeleton, intersections_idx)

        ## Step 2.3: find neighbors
        neighbors_idx, neighbors_xy = find_neighbors(intersections_idx, img_size, crack_skeleton_no_intersection_idx)

        ## Step 2.4: remove neighbors
        crack_skeleton_no_intersection[neighbors_idx] = 0

        ## Step 2.5: split to branches
        branches = split_to_branches(crack_skeleton_no_intersection)

        # Step 3: Branch connectivity refinement
        ## Step 3.1: adding neighbors back to branches
        (
            modified_neighbors_idx,
            _,
            branches_idx,
        ) = add_neighbors_back_to_branches(neighbors_idx, branches, crack_skeleton)

        ## Step 3.2: converting remaining neighbors back as single pixel branches and add back to branches
        branches_idx = convert_remaining_neighbors_as_single_pixel_branches(modified_neighbors_idx, branches_idx)

        ## Step 3.3: connecting branches with intersections
        branches_idx = connect_branches_with_intersections(branches_idx, crack_skeleton, intersections_xy)
        linearized_branches_xy = linearize_branches(branches_idx, crack_skeleton)[0]

        # Set the unit length of the pavement image (length that each pixel represents)
        pixel_length = 4  # unit in mm
        branches_length = compute_crack_length(linearized_branches_xy, pixel_length)

        image_for_width = self._range_img if self._use_rng_img_for_width_cal else self._seg_img
        thresh = (
            settings.WIDTH_INTENSITY_THRESHOLD.range
            if self._use_rng_img_for_width_cal
            else settings.WIDTH_INTENSITY_THRESHOLD.segmentation
        )
        branches_width_xy, branches_width = compute_crack_width(
            linearized_branches_xy, thresh=thresh, image=image_for_width
        )

        # TODO: The intersections reprenstation is reversed compared to the correct one.
        # TODO: It should be fixed but it might mess up the connect_branches_with_intersections function.
        # TODO: Therefore, we temporarily flip it back here.
        intersections_xy = np.flip(intersections_xy, axis=1)

        return CrackVectorModel(
            intersections_xy=intersections_xy,
            branches_length_xy=linearized_branches_xy,
            branches_width_xy=branches_width_xy,
            branches_length=branches_length,
            branches_width=branches_width,
        )

    def _check_current_state(self) -> None:
        """
        A function to check the current state of the object before building CVM.

        Raises:
            RedundantImageError: If both Segmentation image and GeoJSON object are found.
            MissingImageError: If there is no image to build CVM from.
            MissingImageOrGeojsonError: If Range image is required for width calculation and not found.
        """
        if self._seg_img is not None and self._geojson_obj is not None:
            raise RedundantImageError(
                "Found both Segmentation image and Geojson object! Please use either use_seg_* OR use_geojson_*!"
            )

        if self._seg_img is None and self._geojson_obj is None:
            raise MissingImageError(
                "No image to build CVM from! Please use one method use_seg_* OR use_geojson_* before using this function."
            )

        if self._use_rng_img_for_width_cal and self._range_img is None:
            raise MissingImageOrGeojsonError(
                "Range image is required for width calculation! Please use use_range_* before using this function."
            )

    def _build_from_geojson(self, geojson_obj: geojson.FeatureCollection) -> CrackVectorModel:
        """
        Builds a CrackVectorModel from a GeoJSON FeatureCollection object.

        Args:
            geojson_obj (geojson.FeatureCollection): The GeoJSON object to build from.

        Returns:
            CrackVectorModel: The constructed CrackVectorModel containing information about intersections, branches length, branches width.
        """

        def get_perpendicular_ends(linestring, widths):
            coords = np.array(linestring.coords)
            num_coords = len(coords)

            perpendicular_ends = []

            for i in range(1, num_coords - 1):
                prev_coord = coords[i - 1]
                curr_coord = coords[i]
                next_coord = coords[i + 1]

                # Calculate the direction vector
                direction = next_coord - prev_coord

                # Rotate the direction vector by 90 degrees
                perpendicular = np.array([-direction[1], direction[0]])

                # Normalize the perpendicular vector
                length = np.linalg.norm(perpendicular)
                if length != 0:
                    perpendicular = perpendicular / length

                # Calculate the offset vector
                half_width = widths[i - 1] / 2
                offset = perpendicular * half_width

                # Calculate the two end coordinates
                end1 = curr_coord + offset
                end2 = curr_coord - offset

                perpendicular_ends.append((end1, end2))

            return perpendicular_ends

        gdf = geojson_to_geodataframe(geojson_obj)
        branches_length_xy = [np.array(length.coords, dtype=np.int32) for length in gdf.geometry]
        branches_length = gdf.geometry.length.to_numpy(dtype=np.float32)

        gdf["coords"] = gdf.geometry.apply(lambda geom: list(geom.coords))
        branches_width_xy = [
            np.array(
                get_perpendicular_ends(branch.geometry, branch.width),
                dtype=np.int32,
            )
            for branch in gdf.itertuples(index=False)
        ]
        branches_width_xy = [
            branch_width_xy if branch_width_xy.any() else np.empty((0, 0, 0)) for branch_width_xy in branches_width_xy
        ]
        branches_width = [np.asarray(branch.width, dtype=np.float32) for branch in gdf.itertuples(index=False)]

        # Get intersections by finding duplicate ends of branches
        intersections_xy, count = np.unique(
            list(chain(*[(branch_length_xy[0], branch_length_xy[-1]) for branch_length_xy in branches_length_xy])),
            axis=0,
            return_counts=True,
        )
        intersections_xy = intersections_xy[count > 1]

        return CrackVectorModel(
            intersections_xy=intersections_xy,
            branches_length_xy=branches_length_xy,
            branches_width_xy=branches_width_xy,
            branches_length=branches_length,
            branches_width=branches_width,
        )
