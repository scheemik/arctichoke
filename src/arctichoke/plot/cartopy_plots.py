import cartopy.crs as crs
from cartopy.mpl.geoaxes import GeoAxes
from matplotlib.axes._axes import Axes
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

from arctichoke.dataset import  get_latlon_names
from arctichoke.plot.cbar_limits import set_cbar_lims
from arctichoke.plot.labels_and_titles import make_title, make_label
from arctichoke.plot.save_hvplots import save_hvplot

def make_cartopy_map(
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
    fig: Figure = None,
    axis: (Axes, GeoAxes) = None,
    save_as: str = None,
    verbose: bool = False,
    **kwargs,
):
    """ Create a `cartopy` map.

        Plot a map of the given data using the `xarray.plot()` function, which uses `cartopy` underneath.
        This function is meant to be called by the wrapper function `arctichoke.plot.plot_map()` using `use_hvplot=False`. 

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
        map_label : `str`, `None`, optional
            Specify the label of the map's colorbar or, if `None` is given, use the `make_label()` function to create the label.
            Default is `None`.
        this_cmap : `str`, optional
            The colormap to use for this plot.
            Default is `viridis`.
        symmetric_cbar : `bool`, optional
            Whether to use a symmetric, diverging colormap on the colorbar.
            Default is `False`.
        fig : `None`, `matplotlib.figure.Figure`, optional
            If not `None`, this is the pre-existing figure on which to plot the map.
            Default is `None` which creates a new figure with a new axis.
        axis : `None`, `matplotlib.axes._axes.Axes`, `cartopy.mpl.geoaxes.GeoAxes`, optional
            If not `None`, this is the pre-existing axis in `fig` on which to plot the map.
            Default is `None` which creates a new figure with a new axis.
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
        cp_map_plot : `cartopy.mpl.geocollection.GeoQuadMesh`
            The plot object from cartopy.
        
        Examples
        --------
        >>> import xarray as xr
        >>> from arctichoke.plot.plot_map import plot_map
        >>> this_plot = plot_map(xr.open_dataset("data/areacello_Ofx_EC-Earth3P-HR_highres-future_r2i1p2f1_gn.nc", 'areacello', use_hvplot=False)
        >>> print(type(this_plot))
        <class 'cartopy.mpl.geocollection.GeoQuadMesh'>
    """
    # Verify input arguments
    if not isinstance(xr_data, xr.Dataset):
        raise TypeError(f"(make_cartopy_map) `xr_data` must be `xr.Dataset`. Got type: {type(xr_data)}")
    if not isinstance(var, str):
        raise TypeError(f"(make_cartopy_map) `var` must be a string. Got type: {type(var)}")
    if var not in xr_data.data_vars:
        raise ValueError(f"(make_cartopy_map) Variable '{var}' not found in `xr_data`. Available variables are: {list(xr_data.data_vars)}")
    if not isinstance(cmin, (int, float)):
        raise TypeError(f"(make_cartopy_map) `cmin` must be `int` or `float`. Got type: {type(cmin)}")
    if not isinstance(cmax, (int, float)):
        raise TypeError(f"(make_cartopy_map) `cmax` must be `int` or `float`. Got type: {type(cmax)}")
    if not isinstance(map_projection, (crs.CRS, type(None))):
        raise TypeError(f"(make_cartopy_map) `map_projection` must be `crs.CRS`. Got type: {type(map_projection)}")
    if isinstance(map_extent, tuple):
        if not len(map_extent) == 4:
            raise ValueError(f"(make_cartopy_map) `map_extent` must have a length of 4. Got length: {len(map_extent)}")
        else: 
            for i in range(len(map_extent)):
                if not isinstance(map_extent[i], (int, float)):
                    raise TypeError(f"(make_cartopy_map) `map_extent[{i}]` must be a number. Got type: {type(map_extent[i])}")
    elif not isinstance(map_extent, (type([]), type(None))):
        raise TypeError(f"(make_cartopy_map) `map_extent` must be a list or `None`. Got type: {type(map_extent)}")
    if isinstance(map_bbox, type([])):
        if not len(map_bbox) == 4:
            raise ValueError(f"(make_cartopy_map) `map_bbox` must have a length of 4. Got length: {len(map_bbox)}")
        else: 
            for i in range(len(map_bbox)):
                if not isinstance(map_bbox[i], (int, float)):
                    raise TypeError(f"(make_cartopy_map) `map_bbox[{i}]` must be a number. Got type: {type(map_bbox[i])}")
    elif not isinstance(map_bbox, type(None)):
        raise TypeError(f"(make_cartopy_map) `map_bbox` must be a list or `bool`. Got type: {type(map_bbox)}")
    if isinstance(mark_bbox, type([])):
        if not len(mark_bbox) == 4:
            raise ValueError(f"(make_cartopy_map) `mark_bbox` must have a length of 4. Got length: {len(mark_bbox)}")
        else: 
            for i in range(len(mark_bbox)):
                if not isinstance(mark_bbox[i], (int, float)):
                    raise TypeError(f"(make_cartopy_map) `mark_bbox[{i}]` must be a number. Got type: {type(mark_bbox[i])}")
    elif isinstance(mark_bbox, bool):
        if mark_bbox:
            mark_bbox = map_bbox
    else:
        raise TypeError(f"(make_cartopy_map) `mark_bbox` must be a list or `bool`. Got type: {type(mark_bbox)}")
    if not isinstance(map_title, (str, type(None))):
        raise TypeError(f"(make_cartopy_map) `map_title` must be a string or `None`. Got type: {type(map_title)}")
    if not isinstance(map_label, (str, type(None))):
        raise TypeError(f"(make_cartopy_map) `map_label` must be a string or `None`. Got type: {type(map_label)}")
    if not isinstance(this_cmap, str):
        raise TypeError(f"(make_cartopy_map) `this_cmap` must be a string. Got type: {type(this_cmap)}")
    if not isinstance(symmetric_cbar, bool):
        raise TypeError(f"(make_cartopy_map) `symmetric_cbar` must be a `bool`. Got type: {type(symmetric_cbar)}")
    if not isinstance(fig, (str, (type(None), Figure))):
        raise TypeError(f"(make_cartopy_map) `fig` must be `None` or `matplotlib.figure.Figure`. Got type: {type(fig)}")
    if not isinstance(axis, (str, (type(None), Axes, GeoAxes))):
        raise TypeError(f"(make_cartopy_map) `axis` must be `None`, `matplotlib.axes._axes.Axes`, or `cartopy.mpl.geoaxes.GeoAxes`. Got type: {type(axis)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(make_cartopy_map) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(make_cartopy_map) `verbose` must be a `bool`. Got type: {type(verbose)}")
    
    # Information to output
    if verbose:
        print(f"(make_cartopy_map) `save_as`: {save_as}")

    # Make title, if necessary
    if isinstance(map_title, type(None)):
        map_title = make_title(xr_data, **kwargs)
    # Make label, if necessary
    if isinstance(map_label, type(None)):
        map_label = make_label(xr_data, var, verbose=verbose)

    # Check whether an existing figure and axis have been given
    if not isinstance(fig, type(None)) and not isinstance(axis, type(None)):
        if verbose:
            print(f"(make_cartopy_map) Replacing existing axis with specified projection.")
        # Get the existing axis position
        ax_pos = axis.get_position()
        # Remove the existing axis
        axis.remove()
        # Replace this axis with the given projection
        axis = fig.add_axes(ax_pos, projection=map_projection)
    else:
        # Set up the figure and axis with the chosen projection
        fig, axis = plt.subplots(1, 1, subplot_kw=dict(projection=map_projection))

    # Plot the map
    cp_map_plot = xr_data[var].plot(
        ax=axis,
        transform=crs.PlateCarree(),  # if not transformed, the data will become very distorted
        cbar_kwargs={
            'label': map_label,
            'orientation': 'horizontal', 
            # 'shrink': 0.7,
            'extend': 'neither',
        },
        cmap = this_cmap,
        vmin = cmin,
        vmax = cmax,
        robust=True,
    )

    # Change axis background color to the default grey in `hvplot`
    axis.set_facecolor('#D3D3D3')
    # Add axis labels and title
    axis.set_title(map_title)
    # Add coastlines from cartopy
    axis.coastlines()

    # Add bounding box to the map
    if mark_bbox:
        # Set the corners of the bounding box
        bbox_df = pd.DataFrame({
            'lon': [mark_bbox[3], mark_bbox[2], mark_bbox[2], mark_bbox[3], mark_bbox[3]],
            'lat': [mark_bbox[1], mark_bbox[1], mark_bbox[0], mark_bbox[0], mark_bbox[1]]
        })
        # Set the number of points per side of the frame of the bounding box
        n = 25
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
        # Add bounding box corners
        axis.scatter(bbox_df['lon'], bbox_df['lat'], color='red', transform=crs.PlateCarree())
        # Add bounding box frame
        axis.plot(frame_df['lon'], frame_df['lat'], color='grey', linestyle='--', transform=crs.PlateCarree())

    # # Not implemented for cartopy plots yet
    # if cmin != -cmax:
    #     cp_map_plot = set_cbar_lims(
    #         cp_map_plot,
    #         cmin,
    #         cmax,
    #         verbose = verbose,
    #         # **kwargs,
    #     )
    if not isinstance(map_extent, type(None)):
        axis.set_extent(
            (map_extent[0], map_extent[1],
            map_extent[2], map_extent[3]),
            crs = map_projection,
        )

    # Save the plot, if applicable
    if not isinstance(save_as, type(None)):
        # Save the plot to file
        plt.savefig(save_as, dpi=200, bbox_inches='tight')

    return axis
