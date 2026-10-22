import cartopy.crs as crs
import xarray as xr

from arctichoke.dataset import  bound_lat, bound_lon, get_latlon_names, get_min_max
import arctichoke.params as sps
from arctichoke.plot.cartopy_plots import make_cartopy_map
from arctichoke.plot.hvplots import make_quadmesh_map
from arctichoke.plot.labels_and_titles import make_title, make_label
from arctichoke.plot.limit_extent import get_limited_extent

def plot_map(
    xr_data: xr.Dataset,
    var: str, 
    use_hvplot: bool = True,
    map_projection: str = 'Orthographic',
    map_bbox: [float, float, float, float] = sps.CAA_BBOX,
    clims: [(int, float), (int, float)] = None,
    map_title: str = None,
    map_label: str = None,
    diverging_cbar: bool = False, 
    return_plot_map_kwargs: bool = False,
    verbose: bool = False,
    **kwargs,
):
    """ Plot a map of the given dataset for the specified variable.

        Plot a map of the given data using either the `hvplot.quadmesh()` function or `xarray.plot()`, which uses `cartopy` underneath. 

        Parameters
        ----------
        xr_data : `xarray.Dataset`
            The dataset to plot.
        var : `str`
            The variable in `xr_data` to plot.
        use_hvplot : `bool`, optional
            Whether to use `hvplot` or `cartopy` to make the map.
            Default is `True` which uses `hvplot` and, if `False`, uses `cartopy` instead.
        map_projection : `str`, optional
            A string naming the map projection to use in the plot.
            Must be one of the following: 'NorthPolarStereo', 'Orthographic'.
            Default is 'Orthographic'.
        map_bbox : Array of `float`, optional
            An array of coordinates defining the bounding box of the map in the following format:
                - [LAT_MAX, LAT_MIN, LON_MAX, LON_MIN]
                
            Default is `arctichoke.params.latlon_params.CAA_BBOX`.
        clims : List or tuple of `int`, `float`, optional
            The limits to use in the colorbar.
            Note: This overrides the default method of limiting the colorbar range when `diverging_cbar=True`.
            Default is `None`, which uses the minimum / maximum values present in the data.
        map_title : `str`, optional
            Specify the title of the map or, if `None` is given, use the `make_title()` function to create the title.
            Default is `None`.
        map_label : `str`, optional
            Specify the label of the map's colorbar or, if `None` is given, use the `make_label()` function to create the label.
            Default is `None`.
        diverging_cbar : `bool`, optional
            Whether to use a diverging colormap on the colorbar.
            Default is `False`.
        return_plot_map_kwargs : `bool`, optional
            Whether to return `plot_map_kwargs` or not.
            Default is `False`.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `bound_lat()`, `bound_lon`, `hvplot.quadmesh()`, `arctichoke.plot.limit_extent.get_limited_extent()`, and `make_title()`

        Returns
        -------
        map_plot : `cartopy.mpl.geocollection.GeoQuadMesh` or `holoviews.core.overlay.Overlay`
            The plot object with the map.
        
        Examples
        --------
        >>> import xarray as xr
        >>> from arctichoke.plotting import plot_map
        >>> this_plot = plot_map(xr.open_dataset("data/areacello_Ofx_EC-Earth3P-HR_highres-future_r2i1p2f1_gn.nc", 'areacello')
        >>> print(type(this_plot))
        <class 'holoviews.core.overlay.Overlay'>
    """
    # Verify input arguments
    if not isinstance(xr_data, xr.Dataset):
        raise TypeError(f"(plot_map) `xr_data` must be `xr.Dataset`. Got type: {type(xr_data)}")
    if not isinstance(var, str):
        raise TypeError(f"(plot_map) `var` must be a string. Got type: {type(var)}")
    if var not in xr_data.data_vars:
        raise ValueError(f"(plot_map) Variable '{var}' not found in `xr_data`. Available variables are: {list(xr_data.data_vars)}")
    if not isinstance(use_hvplot, bool):
        raise TypeError(f"(plot_map) `use_hvplot` must be a `bool`. Got type: {type(use_hvplot)}")
    if not isinstance(map_projection, (str, type(None))):
        raise TypeError(f"(plot_map) `map_projection` must be a string. Got type: {type(map_projection)}")
    elif map_projection not in ['NorthPolarStereo', 'Orthographic']:
        raise ValueError(f"(plot_map) `map_projection` must be one of the following: 'NorthPolarStereo', 'Orthographic'. Got: {map_projection}")
    if isinstance(map_bbox, type([])):
        if not len(map_bbox) == 4:
            raise ValueError(f"(plot_map) `map_bbox` must have a length of 4. Got length: {len(map_bbox)}")
        else: 
            for i in range(len(map_bbox)):
                if not isinstance(map_bbox[i], (int, float)):
                    raise TypeError(f"(plot_map) `map_bbox[{i}]` must be a number. Got type: {type(map_bbox[i])}")
    elif not isinstance(map_bbox, (type([]), type(None))):
        raise TypeError(f"(plot_map) `map_bbox` must be a list or `None`. Got type: {type(map_bbox)}")
    if isinstance(clims, type([])):
        clims = tuple(clims)
    if not isinstance(clims, (tuple, type(None))):
        raise TypeError(f"(plot_map) `clims` must be a list, tuple, or `None`. Got type: {type(clims)}")
    elif not isinstance(clims, type(None)) and len(clims) != 2:
        raise TypeError(f"(plot_map) `clims` must be a list or tuple of length 2. Got length: {len(clims)}")
    if not isinstance(map_title, (str, type(None))):
        raise TypeError(f"(plot_map) `map_title` must be a string or `None`. Got type: {type(map_title)}")
    if not isinstance(map_label, (str, type(None))):
        raise TypeError(f"(plot_map) `map_label` must be a string or `None`. Got type: {type(map_label)}")
    if not isinstance(diverging_cbar, bool):
        raise TypeError(f"(plot_map) `diverging_cbar` must be a `bool`. Got type: {type(diverging_cbar)}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(plot_map) `verbose` must be a `bool`. Got type: {type(verbose)}")

    # Unpack the bounding box values
    if not isinstance(map_bbox, type(None)):
        box_lat_max = map_bbox[0]
        box_lat_min = map_bbox[1]
        box_lon_max = map_bbox[2]
        box_lon_min = map_bbox[3]
    else:
        box_lat_min, box_lat_max = get_min_max(xr_data, 'latitude')
        box_lon_min, box_lon_max = get_min_max(xr_data, 'longitude')
        map_bbox = [box_lat_max, box_lat_min, box_lon_max, box_lon_min]
    # Make sure the the coordinates aren't outside valid ranges
    box_lat_max = bound_lat(box_lat_max, **kwargs)
    box_lat_min = bound_lat(box_lat_min, **kwargs)
    box_lon_max = bound_lon(box_lon_max, **kwargs)
    box_lon_min = bound_lon(box_lon_min, **kwargs)
    # Get the central latitude and longitude
    box_lat_cent = (box_lat_max-box_lat_min)/2 + box_lat_min
    box_lon_cent = (box_lon_max-box_lon_min)/2 + box_lon_min
    if verbose:
        print(f"(plot_map) Central latitude: {box_lat_cent}, central longitude: {box_lon_cent}")
    if map_projection == 'Orthographic':
        # Define the projection for the plot
        # box_lon_cent = -90
        # box_lat_cent = 77
        map_projection = crs.Orthographic(central_longitude = box_lon_cent, central_latitude = box_lat_cent)
    elif map_projection == 'NorthPolarStereo':
        # Define the projection for the plot
        map_projection = crs.NorthPolarStereo(central_longitude = box_lon_cent)
    # Get the extent to which to limit the map plot
    map_extent = get_limited_extent(
        map_projection, 
        map_bbox,
        verbose=verbose,
        **kwargs,
    )
    if verbose:
        print(f"(plot_map) Map bounding box: {map_bbox}")
        print(f"(plot_map) Map extent: {map_extent}")

    # Set colormap
    if diverging_cbar == True:
        this_cmap = 'bwr'
        symmetric_cbar = True
    else:
        this_cmap = 'viridis'
        symmetric_cbar = False

    # Make title, if necessary
    if isinstance(map_title, type(None)):
        map_title = make_title(xr_data, **kwargs)
    # Make label, if necessary
    if isinstance(map_label, type(None)):
        map_label = make_label(xr_data, var, verbose=verbose)
    
    # Set colorbar parameters
    if isinstance(clims, type(None)):
        cmin, cmax = get_min_max(xr_data, var)
    else:
        cmin = min(clims)
        cmax = max(clims)
    if verbose:
        print(f"(plot_map) `diverging_cbar`: {diverging_cbar}")
        print(f"(plot_map) `cmin`: {cmin}, `cmax`: {cmax}")

    # Make the plot
    if use_hvplot:
        map_plot = make_quadmesh_map(
            xr_data = xr_data,
            var = var,
            cmin = cmin,
            cmax = cmax,
            map_projection = map_projection,
            map_extent = map_extent,
            map_bbox = map_bbox,
            map_title = map_title,
            map_label = map_label,
            this_cmap = this_cmap,
            symmetric_cbar = symmetric_cbar,
            verbose = verbose,
            **kwargs,
        )
    else:
        map_plot = make_cartopy_map(
            xr_data = xr_data,
            var = var,
            cmin = cmin,
            cmax = cmax,
            map_projection = map_projection,
            map_extent = map_extent,
            map_bbox = map_bbox,
            map_title = map_title,
            map_label = map_label,
            this_cmap = this_cmap,
            symmetric_cbar = symmetric_cbar,
            verbose = verbose,
            **kwargs,
        )
    
    if return_plot_map_kwargs:
        # Assemble the keyword arguments to return
        plot_map_kwargs = {
            'map_projection': map_projection,
            'map_extent': map_extent,
            'map_title': map_title,
        }

        return map_plot, plot_map_kwargs
    else:
        return map_plot