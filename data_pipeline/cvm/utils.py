import geopandas as gpd
import numpy as np
from geojson import FeatureCollection


def _idx_to_xy(indices: tuple[np.ndarray, np.ndarray]) -> np.ndarray:
    """Convert a tuple of index arrays to an array of (x, y) coordinates.

    Args:
        indices (tuple[np.ndarray, np.ndarray]): A tuple containing two NumPy arrays
            representing the row and column indices.
    Returns:
        np.ndarray: A 2D NumPy array of shape (N, 2), where N is the number of indices,
            containing the (x, y) coordinates corresponding to the input indices.
    """
    xy = np.column_stack((indices[1], indices[0]))
    return xy


def geojson_to_geodataframe(geojson_cvm: FeatureCollection, /):
    """
    Converts a GeoJSON FeatureCollection to a GeoDataFrame containing length and width features.

    Args:
        geojson_cvm (FeatureCollection): The input GeoJSON FeatureCollection.

    Returns:
        GeoDataFrame: A GeoDataFrame with length and width features.
    """
    branch_gdf = gpd.GeoDataFrame.from_features(geojson_cvm).drop(columns=["name"])
    return branch_gdf
