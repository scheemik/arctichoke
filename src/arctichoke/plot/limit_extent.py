import numpy as np 
import cartopy.crs as crs

from arctichoke.dataset import bound_lat, bound_lon
import arctichoke.params as sps

def get_limited_extent(
    map_projection : crs.CRS,
    map_bbox : [float, float, float, float] = sps.CAA_BBOX,
    n_samples : int = 100,
    padding : (int, float) = 0.1,
    verbose: bool = False,
    **kwargs,
):
    """ Get the extent to which to limit a plot.

        Using the given coordinates to define the corners of a bounding box, sample the edges, and project those points into the given projection.
        If the value of `map_bbox` is the default value of `arctichoke.params.latlon_params.CAA_BBOX`, that bounding box will be replaced by `CAAM_BBOX` which has been manually tuned to provide a more reasonable extent definition for making plots of the CAA.

        Parameters
        ----------
        map_projection : `cartopy.crs.CRS`
            The coordinate reference system from `cartopy` onto which the bounding box will be projected.
        map_bbox : Array of `float`, optional
            An array of coordinates defining the bounding box of the map in the following format:
                - [LAT_MAX, LAT_MIN, LON_MAX, LON_MIN]
                
            Default is `arctichoke.params.latlon_params.CAA_BBOX`.
        n_sample : `int`, optional
            The number of samples to take along the edges of the bounding box.
            Use a larger number for larger bounding boxes to reduce clipping.
            Default is `100`.
        padding : `int`, `float`, optional
            The fractional value between 0 and 1 by which to multiply the latitude and longitude extents.
            Default is `0.1`, or 10%.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `bound_lat()` and `bound_lon()`.

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
    if not isinstance(padding, (int, float)):
        raise TypeError(f"(get_limited_extent) `padding` must be an integer or `float`. Got type: {type(padding)}")
    if padding < 0 or padding > 1:
        raise TypeError(f"(get_limited_extent) `padding` must be between 0 and 1. Got: {padding}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(get_limited_extent) `verbose` must be a `bool`. Got type: {type(verbose)}")

    # Information to output
    if verbose:
        print(f"(get_limited_extent) Caution: The full range of possibilities of longitude values have not been accounted for, if using longitude values near the limits of the valid range, `nan` values may occur in the returned `map_extent`.")

    # Get the map version of the bounding box, if applicable
    if map_bbox == sps.CAA_BBOX:
        map_bbox = sps.CAAM_BBOX
        if verbose:
            print(f"(get_limited_extent) Given `map_bbox` of `CAA_BBOX`, so replacing with `CAAM_BBOX`.")

    # Unpack the bounding box values
    box_lat_max = map_bbox[0]
    box_lat_min = map_bbox[1]
    box_lon_max = map_bbox[2]
    box_lon_min = map_bbox[3]
    # Pad the bounding box values, if applicable
    if padding != 0:
        if verbose:
            print(f"(get_limited_extent) Adding a padding of {padding*100}% to the bounding box.")
        lat_extent = abs(box_lat_max - box_lat_min)
        lon_extent = abs(box_lon_max - box_lon_min)
        lat_padding = lat_extent * padding 
        lon_padding = lon_extent * padding 
        box_lat_max += lat_padding / 2
        box_lat_min -= lat_padding / 2
        box_lon_max += lon_padding / 2
        box_lon_min -= lon_padding / 2
    # Make sure the the coordinates aren't outside valid ranges
    box_lat_max = bound_lat(box_lat_max, **kwargs)
    box_lat_min = bound_lat(box_lat_min, **kwargs)
    box_lon_max = bound_lon(box_lon_max, **kwargs)
    box_lon_min = bound_lon(box_lon_min, **kwargs)
    if verbose:
        print(f"(get_limited_extent) Bounding box: \n\tlat_max = {box_lat_max}, lat_min = {box_lat_min}, lon_max = {box_lon_max}, lon_min = {box_lon_min}")
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
    # if verbose:
    #     print(f"(get_limited_extent) Edge points: \n\tedge_lons = {edge_lons}\n\tedge_lats = {edge_lats}")
    # Transform the edge samples
    edge_pts = map_projection.transform_points(crs.PlateCarree(), edge_lons, edge_lats)
    edge_xs = edge_pts[:, 0]
    edge_ys = edge_pts[:, 1]
    # Get the extent in projected coordinates
    map_extent = (edge_xs.min(), edge_xs.max(), edge_ys.min(), edge_ys.max())

    return map_extent