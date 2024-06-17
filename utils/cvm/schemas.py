from pathlib import Path

import cv2 as cv
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import orjson
import pydantic_numpy.typing as pnd
from geojson import Feature, FeatureCollection, LineString
from pydantic import BaseModel, ConfigDict

from cvm import utils
from cvm.core.base import plot_result_of_crack_length_and_width


class CrackVectorModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    intersections_xy: pnd.Np2DArrayInt32
    branches_length_xy: list[pnd.Np2DArrayInt32]
    branches_width_xy: list[pnd.Np3DArrayInt32]
    branches_length: pnd.Np1DArrayFp32
    branches_width: list[pnd.Np1DArrayFp32]

    def to_geojson(self) -> FeatureCollection:
        """
        Generates a GeoJSON representation of the CrackVectorModel.

        Returns:
            FeatureCollection: A collection of GeoJSON features representing the crack vector model
            using the branch-based representation (refer to `README.md` to learn more).
        """
        n_branches = len(self.branches_length_xy)
        branch_features = []
        for idx in range(n_branches):
            cur_branch_point_xy = self.branches_length_xy[idx]
            cur_branch_width = self.branches_width[idx]

            branch_feature = Feature(
                geometry=LineString(cur_branch_point_xy.tolist()),
                properties={"name": "branch", "width": cur_branch_width.tolist()},
            )
            branch_features.append(branch_feature)

        geojson_cvm = FeatureCollection(branch_features)

        return geojson_cvm

    def dump_geojson(self, file: str | Path) -> None:
        """
        Writes the CrackVectorModel's geojson representation to a file.

        Parameters:
            file (str | Path): The path to the file to write the geojson representation to.

        Returns:
            None
        """
        with open(str(file), "w") as f:
            geo_cvm_str = orjson.dumps(
                self.to_geojson(), option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_INDENT_2
            ).decode("utf-8")
            f.write(geo_cvm_str)

    def to_geodataframe(self) -> gpd.GeoDataFrame:
        """
        Converts the CrackVectorModel object to a GeoDataFrame.

        Returns:
            gpd.GeoDataFrame: A GeoDataFrame containing length and width features.
        """

        geojson_cvm = self.to_geojson()
        return utils.geojson_to_geodataframe(geojson_cvm)

    def plot_on(self, image: np.ndarray | str | Path, *, save_to_file: str | Path | None = None, **kwargs) -> None:
        """
        Plots the crack vectors on the provided image with associated lengths and widths.

        Parameters:
            image (np.ndarray | str | Path): The image on which to plot the crack vectors.
            save_to_file (str | Path | None, optional): File path to save the plot. If None, the plot is shown but not saved. Defaults to None.

        Returns:
            None
        """
        if not isinstance(image, np.ndarray):
            if not Path(image).exists():
                raise FileNotFoundError(f"Not found image at the given path {image}")

            image = cv.imread(str(image))

        lon1 = np.concatenate(
            [branch_width_xy[:, 0, 0] for branch_width_xy in self.branches_width_xy if branch_width_xy.any()]
        )
        lat1 = np.concatenate(
            [branch_width_xy[:, 0, 1] for branch_width_xy in self.branches_width_xy if branch_width_xy.any()]
        )
        lon2 = np.concatenate(
            [branch_width_xy[:, 1, 0] for branch_width_xy in self.branches_width_xy if branch_width_xy.any()]
        )
        lat2 = np.concatenate(
            [branch_width_xy[:, 1, 1] for branch_width_xy in self.branches_width_xy if branch_width_xy.any()]
        )
        plot_result_of_crack_length_and_width(
            rng_image=image,
            branches_xy=self.branches_length_xy,
            intersections_xy=self.intersections_xy,
            lon1=lon1,
            lon2=lon2,
            lat1=lat1,
            lat2=lat2,
            branches_length=self.branches_length,
            branches_width=self.branches_width,
            **kwargs,
        )

        # Show the plot
        if save_to_file is not None:
            plt.savefig(str(save_to_file), bbox_inches="tight", pad_inches=0)
        else:
            plt.show()
