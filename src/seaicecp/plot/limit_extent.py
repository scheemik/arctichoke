import numpy as np 
import cartopy.crs as crs

import seaicecp.params as sps

def get_limited_extent(
    map_projection : crs.CRS,
    map_bbox : [float, float, float, float] = sps.NWP_BBOX,
    n_samples : int = 100,
):
    """ Get the extent to which to limit a plot.

        Using the given coordinates to define the corners of a bounding box, sample the edges, and project those points into the given projection.

        Parameters
        ----------
        map_projection : `cartopy.crs.CRS`
            The coordinate reference system from `cartopy` onto which the bounding box will be projected.
        map_bbox : Array of `float`, optional
            An array of coordinates defining the bounding box of the map in the following format:
                - [LAT_MAX, LAT_MIN, LON_MAX, LON_MIN]
                
            Default is `seaicecp.params.latlon_params.NWP_BBOX`.
        n_sample : `int`, optional
            The number of samples to take along the edges of the bounding box.
            Use a larger number for larger bounding boxes to reduce clipping.
            Default is `100`.

        Returns
        -------
        map_extent
        
        Examples
        --------
        >>> 
    """
    # Verify input arguments
    if not isinstance(map_projection, crs.CRS):
        raise TypeError(f"(get_limited_extent) `map_projection` must be a `cartopy.crs.CRS` object. Got type: {type(map_projection)}")
    if not isinstance(map_bbox, type([])):
        raise TypeError(f"(get_limited_extent) `map_bbox` must be a list. Got type: {type(map_bbox)}")
    elif not len(map_bbox) == 4:
        raise ValueError(f"(get_limited_extent) `map_bbox` must have a length of 4. Got length: {len(map_bbox)}")
    else: 
        for i in range(len(map_bbox)):
            if not isinstance(map_bbox[i], (int, float)):
                raise TypeError(f"(get_limited_extent) `map_bbox[{i}]` must be a number. Got type: {type(map_bbox[i])}")
    if not isinstance(n_samples, int):
        raise TypeError(f"(get_limited_extent) `n_samples` must be an integer. Got type: {type(n_samples)}")

    # Unpack the bounding box values
    box_lat_max = map_bbox[0]
    box_lat_min = map_bbox[1]
    box_lon_max = map_bbox[2]
    box_lon_min = map_bbox[3]
    # Sample the edges of the bounding box
    edge_S_lons = np.linspace(box_lon_min, box_lon_max, n_samples)
    edge_S_lats = np.full(n_samples, box_lat_min)
    edge_N_lons = np.linspace(box_lon_min, box_lon_max, n_samples)
    edge_N_lats = np.full(n_samples, box_lat_max)
    edge_W_lats = np.linspace(box_lat_min, box_lat_max, n_samples)
    edge_W_lons = np.full(n_samples, box_lon_min)
    edge_E_lats = np.linspace(box_lat_min, box_lat_max, n_samples)
    edge_E_lons = np.full(n_samples, box_lon_max)
    # Concatenate the edge samples
    edge_lons = np.concatenate([edge_S_lons, edge_N_lons, edge_W_lons, edge_E_lons])
    edge_lats = np.concatenate([edge_S_lats, edge_N_lats, edge_W_lats, edge_E_lats])
    # Transform the edge samples
    edge_pts = map_projection.transform_points(crs.PlateCarree(), edge_lons, edge_lats)
    edge_xs = edge_pts[:, 0]
    edge_ys = edge_pts[:, 1]
    # Get the extent in projected coordinates
    map_extent = (edge_xs.min(), edge_xs.max(), edge_ys.min(), edge_ys.max())

    return map_extent