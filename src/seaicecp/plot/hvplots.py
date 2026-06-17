import hvplot.xarray
import xarray as xr
import cartopy.crs as crs

from seaicecp.plot.save_hvplots import save_hvplot
from seaicecp.plot.limit_extent import get_limited_extent
from seaicecp.dataset.latlon_type import get_latlon_names
import seaicecp.params as sps

def quadmesh_map(
    xr_data: xr.Dataset,
    var: str, 
    save_as: str = None,
    map_projection: str = 'NorthPolarStereo',
    map_bbox: [float, float, float, float] = sps.NWP_BBOX,
    verbose: bool = False,
    **kwargs,
):
    """ Create an `hvplot` quadmesh map.

        Plot a map of the given data using the `hvplot.quadmesh()` function. 

        Parameters
        ----------
        xr_data : `xarray.Dataset`
            The dataset to plot.
        var : `str`
            The variable in `xr_data` to plot.
        save_as : `str`, `None`, optional
            The file name to pass to `seaicecp.plot.save_hvplots.save_hvplot()`.
            Default is `None`, which doesn't save the plot to a file.
        map_projection : `str`, optional
            A string naming the map projection to use in the plot.
            Must be one of the following: 'NorthPolarStereo', 'Orthograpic'.
            Default is 'NorthPolarStereo'.
        map_bbox : Array of `float`, optional
            An array of coordinates defining the bounding box of the map in the following format:
                - [LAT_MAX, LAT_MIN, LON_MAX, LON_MIN]
                
            Default is `seaicecp.params.latlon_params.NWP_BBOX`.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `hvplot.quadmesh()` and `seaicecp.plot.limit_extent.get_limited_extent()`

        Returns
        -------
        qm_map_plot : `holoviews.core.overlay.Overlay`
            An overlay object which can be used to construct the plot.
        
        Examples
        --------
        >>> import xarray as xr
        >>> this_plot = hvplots.quadmesh_map(xr.open_dataset("data/areacello_Ofx_EC-Earth3P-HR_highres-future_r2i1p2f1_gn.nc", 'areacello')
        >>> print(type(this_plot))
        <class 'holoviews.core.overlay.Overlay'>
    """
    # Verify input arguments
    if not isinstance(xr_data, xr.Dataset):
        raise TypeError(f"(quadmesh_map) `xr_data` must be `xr.Dataset`. Got type: {type(xr_data)}")
    if not isinstance(var, str):
        raise TypeError(f"(quadmesh_map) `var` must be a string. Got type: {type(var)}")
    if var not in xr_data.data_vars:
        raise ValueError(f"(quadmesh_map) Variable '{var}' not found in `xr_data`. Available variables are: {list(xr_data.data_vars)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(quadmesh_map) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    if not isinstance(map_projection, (str, type(None))):
        raise TypeError(f"(quadmesh_map) `map_projection` must be a string. Got type: {type(map_projection)}")
    elif map_projection not in ['NorthPolarStereo', 'Orthographic']:
        raise ValueError(f"(quadmesh_map) `map_projection` must be one of the following: 'NorthPolarStereo', 'Orthographic'. Got: {map_projection}")
    if not isinstance(map_bbox, type([])):
        raise TypeError(f"(quadmesh_map) `map_bbox` must be a list. Got type: {type(map_bbox)}")
    elif not len(map_bbox) == 4:
        raise ValueError(f"(quadmesh_map) `map_bbox` must have a length of 4. Got length: {len(map_bbox)}")
    else: 
        for i in range(len(map_bbox)):
            if not isinstance(map_bbox[i], (int, float)):
                raise TypeError(f"(quadmesh_map) `map_bbox[{i}]` must be a number. Got type: {type(map_bbox[i])}")
    
    # Information to output
    if verbose:
        print(f"(quadmesh_map) `save_as`: {save_as}")

    map_extent = None
    if map_projection == 'Orthographic':
        # Define the projection for the plot
        map_projection = crs.Orthographic(-90, 77)
    elif map_projection == 'NorthPolarStereo':
        # Unpack the bounding box values
        box_lat_max = map_bbox[0]
        box_lat_min = map_bbox[1]
        box_lon_max = map_bbox[2]
        box_lon_min = map_bbox[3]

        # Get the central longitude
        box_lon_cent = (box_lon_max-box_lon_min)/2 + box_lon_min
        # Define the projection for the plot
        map_projection = crs.NorthPolarStereo(central_longitude = box_lon_cent)
        # Get the extent to which to limit the map plot
        map_extent = get_limited_extent(map_projection)
    
    # Get the latitude and longitude coordinate names
    lat_var, lon_var = get_latlon_names(xr_data)
    if verbose:
        print(f"(quadmesh_map) `lat_var`: {lat_var}")
        print(f"(quadmesh_map) `lon_var`: {lon_var}")

    # Make the plot
    qm_map_plot = xr_data[var].hvplot.quadmesh(
        lon_var, 
        lat_var, 
        projection=map_projection, 
        project=True,
        global_extent=False, 
        cmap='viridis', 
        coastline=True,
        geo=True,
    )

    # Set plot extent
    if not isinstance(map_extent, type(None)):
        qm_map_plot = qm_map_plot.opts(
            xlim=(map_extent[0], map_extent[1]),
            ylim=(map_extent[2], map_extent[3]),
        )

    # Save the plot, if applicable
    if not isinstance(save_as, type(None)):
        # Save the plot to file
        save_hvplot(qm_map_plot, save_as)

    return qm_map_plot

