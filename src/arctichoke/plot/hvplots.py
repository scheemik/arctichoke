import cartopy.crs as crs
import hvplot.pandas
import hvplot.xarray
import numpy as np
import pandas as pd
import xarray as xr

from arctichoke.dataset import  get_latlon_names
from arctichoke.plot.cbar_limits import set_cbar_lims
from arctichoke.plot.labels_and_titles import make_title, make_label
from arctichoke.plot.save_hvplots import save_hvplot

def make_quadmesh_map(
    xr_data: xr.Dataset,
    var: str, 
    cmin: (int, float),
    cmax: (int, float),
    map_projection: crs.CRS,
    map_extent: (float, float, float, float),
    map_bbox: (bool, [float, float, float, float]),
    mark_bbox: (bool, [float, float, float, float]) = False,
    map_title: str = None,
    map_label: str = None,
    this_cmap: str = 'viridis',
    symmetric_cbar: bool = False, 
    save_as: str = None,
    verbose: bool = False,
    **kwargs,
):
    """ Create an `hvplot` quadmesh map.

        Plot a map of the given data using the `hvplot.quadmesh()` function.
        This function is meant to be called by the wrapper function `arctichoke.plot.plot_map()` using `use_hvplot=True`. 

        Parameters
        ----------
        xr_data : `xarray.Dataset`
            The dataset to plot.
        var : `str`
            The variable in `xr_data` to plot.
        cmin : `int`, `float`
            The minimum value for the colorbar.
        cmax : `int`, `float`
            The maximum value for the colorbar.
        map_projection : `cartopy.crs.CRS`
            The map projection object to use for the plot.
        map_extent : tuple of (int, float)
            The extent to which the plot should be limited in the following format: 
            `(x_min, x_max, y_min, y_max)`
        map_bbox : Array of `float`, optional
            An array of coordinates defining the bounding box of the map in the following format:
                - [LAT_MAX, LAT_MIN, LON_MAX, LON_MIN]
                
        mark_bbox : `None`, Array of `float`, optional
            An array of coordinates defining a bounding box to mark on the map in the following format:
                - [LAT_MAX, LAT_MIN, LON_MAX, LON_MIN]
                
            Default is `False` which adds no bounding box.
        map_title : `str`, optional
            Specify the title of the map or, if `None` is given, use the `make_title()` function to create the title.
            Default is `None`.
        map_label : `str`, optional
            Specify the label of the map's colorbar or, if `None` is given, use the `make_label()` function to create the label.
            Default is `None`.
        this_cmap : `str`, optional
            The colormap to use for this plot.
            Default is `viridis`.
        symmetric_cbar : `bool`, optional
            Whether to use a symmetric, diverging colormap on the colorbar.
            Default is `False`.
        save_as : `str`, `None`, optional
            The file name to pass to `arctichoke.plot.save_hvplots.save_hvplot()`.
            Default is `None`, which doesn't save the plot to a file.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `make_title()`.

        Returns
        -------
        qm_map_plot : `holoviews.core.overlay.Overlay`
            An overlay object which can be used to construct the plot.
        
        Examples
        --------
        >>> import xarray as xr
        >>> from arctichoke.plot.plot_map import plot_map
        >>> this_plot = plot_map(xr.open_dataset("data/areacello_Ofx_EC-Earth3P-HR_highres-future_r2i1p2f1_gn.nc", 'areacello', use_hvplot=True)
        >>> print(type(this_plot))
        <class 'holoviews.core.overlay.Overlay'>
    """
    # Verify input arguments
    if not isinstance(xr_data, xr.Dataset):
        raise TypeError(f"(make_quadmesh_map) `xr_data` must be `xr.Dataset`. Got type: {type(xr_data)}")
    if not isinstance(var, str):
        raise TypeError(f"(make_quadmesh_map) `var` must be a string. Got type: {type(var)}")
    if var not in xr_data.data_vars:
        raise ValueError(f"(make_quadmesh_map) Variable '{var}' not found in `xr_data`. Available variables are: {list(xr_data.data_vars)}")
    if not isinstance(cmin, (int, float)):
        raise TypeError(f"(make_quadmesh_map) `cmin` must be `int` or `float`. Got type: {type(cmin)}")
    if not isinstance(cmax, (int, float)):
        raise TypeError(f"(make_quadmesh_map) `cmax` must be `int` or `float`. Got type: {type(cmax)}")
    if not isinstance(map_projection, (crs.CRS, type(None))):
        raise TypeError(f"(make_quadmesh_map) `map_projection` must be `crs.CRS`. Got type: {type(map_projection)}")
    if isinstance(map_extent, tuple):
        if not len(map_extent) == 4:
            raise ValueError(f"(make_quadmesh_map) `map_extent` must have a length of 4. Got length: {len(map_extent)}")
        else: 
            for i in range(len(map_extent)):
                if not isinstance(map_extent[i], (int, float)):
                    raise TypeError(f"(make_quadmesh_map) `map_extent[{i}]` must be a number. Got type: {type(map_extent[i])}")
    elif not isinstance(map_extent, (type([]), type(None))):
        raise TypeError(f"(make_quadmesh_map) `map_extent` must be a list or `None`. Got type: {type(map_extent)}")
    if isinstance(map_bbox, type([])):
        if not len(map_bbox) == 4:
            raise ValueError(f"(make_quadmesh_map) `map_bbox` must have a length of 4. Got length: {len(map_bbox)}")
        else: 
            for i in range(len(map_bbox)):
                if not isinstance(map_bbox[i], (int, float)):
                    raise TypeError(f"(make_quadmesh_map) `map_bbox[{i}]` must be a number. Got type: {type(map_bbox[i])}")
    elif not isinstance(map_bbox, type(None)):
        raise TypeError(f"(make_quadmesh_map) `map_bbox` must be a list or `bool`. Got type: {type(map_bbox)}")
    if isinstance(mark_bbox, type([])):
        if not len(mark_bbox) == 4:
            raise ValueError(f"(make_quadmesh_map) `mark_bbox` must have a length of 4. Got length: {len(mark_bbox)}")
        else: 
            for i in range(len(mark_bbox)):
                if not isinstance(mark_bbox[i], (int, float)):
                    raise TypeError(f"(make_quadmesh_map) `mark_bbox[{i}]` must be a number. Got type: {type(mark_bbox[i])}")
    elif isinstance(mark_bbox, bool):
        if mark_bbox:
            mark_bbox = map_bbox
    else:
        raise TypeError(f"(make_quadmesh_map) `mark_bbox` must be a list or `bool`. Got type: {type(mark_bbox)}")
    if not isinstance(map_title, (str, type(None))):
        raise TypeError(f"(make_quadmesh_map) `map_title` must be a string or `None`. Got type: {type(map_title)}")
    if not isinstance(map_label, (str, type(None))):
        raise TypeError(f"(make_quadmesh_map) `map_label` must be a string or `None`. Got type: {type(map_label)}")
    if not isinstance(this_cmap, str):
        raise TypeError(f"(make_quadmesh_map) `this_cmap` must be a string. Got type: {type(this_cmap)}")
    if not isinstance(symmetric_cbar, bool):
        raise TypeError(f"(make_quadmesh_map) `symmetric_cbar` must be a `bool`. Got type: {type(symmetric_cbar)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(make_quadmesh_map) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(make_quadmesh_map) `verbose` must be a `bool`. Got type: {type(verbose)}")
    
    # Information to output
    if verbose:
        print(f"(make_quadmesh_map) `save_as`: {save_as}")

    # Get the latitude and longitude coordinate names
    lat_var, lon_var = get_latlon_names(xr_data)
    if verbose:
        print(f"(make_quadmesh_map) `lat_var`: {lat_var}")
        print(f"(make_quadmesh_map) `lon_var`: {lon_var}")

    # Make title, if necessary
    if isinstance(map_title, type(None)):
        map_title = make_title(xr_data, **kwargs)
    # Make label, if necessary
    if isinstance(map_label, type(None)):
        map_label = make_label(xr_data, var, verbose=verbose)

    # Make the plot
    qm_map_plot = xr_data[var].hvplot.quadmesh(
        lon_var, 
        lat_var, 
        projection=map_projection, 
        project=True,
        global_extent=False, 
        title=map_title,
        clabel=map_label,
        cmap=this_cmap, 
        clim=(cmin,cmax),
        bgcolor='lightgray',
        symmetric=symmetric_cbar,
        coastline=True,
        geo=True,
    )

    # Set plot extent
    if not isinstance(map_extent, type(None)):
        qm_map_plot = qm_map_plot.opts(
            xlim=(map_extent[0], map_extent[1]),
            ylim=(map_extent[2], map_extent[3]),
        )

    # Add bounding box to the map
    if mark_bbox:
        if verbose:
            print(f"(make_quadmesh_map) Adding bounding box from `mark_bbox` to the map")
        # Set the corners of the bounding box
        bbox_df = pd.DataFrame({
            'lon': [mark_bbox[3], mark_bbox[2], mark_bbox[2], mark_bbox[3], mark_bbox[3]],
            'lat': [mark_bbox[1], mark_bbox[1], mark_bbox[0], mark_bbox[0], mark_bbox[1]]
        })
        # Set the number of points per side of the frame of the bounding box
        n = 10
        frame_df = pd.DataFrame({
            'lon': np.concatenate([
                np.linspace(mark_bbox[3], mark_bbox[2], n),
                [mark_bbox[2]]*(n-1), 
                np.linspace(mark_bbox[2], mark_bbox[3], n),
                [mark_bbox[3]]*(n-1), 
            ]),
            'lat': np.concatenate([
                [mark_bbox[1]]*(n-1), 
                np.linspace(mark_bbox[1], mark_bbox[0], n),
                [mark_bbox[0]]*(n-1), 
                np.linspace(mark_bbox[0], mark_bbox[1], n),
            ]),
        })
        # Create paths, points, and labels
        shortest_path = bbox_df.hvplot.paths(
            color='blue', 
            crs=map_projection,
            features=['coastline'],
        )
        straight_path = frame_df.hvplot.paths(
            color='grey', 
            crs=crs.PlateCarree(), 
            line_dash='dashed',
            line_width=2,
        )
        points = bbox_df.hvplot.points(color='red', size=10, geo=True)
        # Compose the map with the bounding box
        qm_map_plot = qm_map_plot * shortest_path * straight_path * points

    # Set colorbar parameters
    if cmin != -cmax:
        qm_map_plot = set_cbar_lims(
            qm_map_plot,
            cmin,
            cmax,
            verbose = verbose,
            # **kwargs,
        )

    # Save the plot, if applicable
    if not isinstance(save_as, type(None)):
        # Save the plot to file
        save_hvplot(
            qm_map_plot,
            save_as,
            verbose = verbose,
        )

    return qm_map_plot