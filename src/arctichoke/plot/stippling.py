import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
import xarray as xr

from arctichoke.params import hatch_grn

def add_hatches(
    hatch_axis,
    dataset,
    var,
    hatch_label,
    hatch_levels = [0, 0.5, 1],
    mark_levels = [False, True, False],
    hatch_style = '.',
    hatch_density = 2,
    hatch_color = hatch_grn,
    contour_level = 0.5,
    verbose = False,
    **kwargs,
):
    """ Add hatching or stippling to an axis.

        Add hatching lines or stippling dots as an overlay to a map on an existing axis.

        Parameters
        ----------
        hatch_axis : `cartopy.mpl.geoaxes.GeoAxes`
            The pre-existing axis on which to add the hatching marks.
            Default is `None` which creates a new figure with a new axis.
        dataset : `xarray.Dataset`
            The dataset to use for the overlay. 
            This does not need to be the same dataset in the given axis plot, but expects to have the same dimensions.
        var : `str`
            The variable in `dataset` to use for the overlay.
        hatch_label : `str`
            The label for the overlay in the legend.
        hatch_levels : Array of `int` or `float`, optional
            An array of the levels to use for the overlay.
            If overlaying a region of multiple values, submit the maximum and minimum values.
            If overlaying a region of one value (such as a binary mask), submit three values. 
            Default is `[0, 0.5, 1]` as would be needed to overlay a binary mask.
        mark_levels : Array of `bool`, optional
            An array of the levels to mark in the overlay.
            Must be the same length as `hatch_levels`. 
            Default is `[False, True, False]` as would be needed to overlay a binary mask.
        hatch_style : `str`, optional
            The strings to indicate what style of hatching or stippling to use.
            Ex: `'.'`, `'/'`.
            Default is `'.'`.
        hatch_density : `int`, optional
            The density of the pattern of the overlay, with higher numbers giving more dense patterns.
            Default is `2`.
        hatch_color : `tuple`, optional
            The color to use for the hatches.
            Must be a tuple of RGBA.
            Default is `(0, .6, 0, 0.9)`.
        contour_level : `None`, `int`, `float`, optional
            A value to mark with a contour on the axis.
            This can be used to frame an area of hatching.
            Default is `0.5` to add a contour to show the edge of a binary mask.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `make_title()`.
            
        Returns
        -------
        handles : 
            The handles required to add the hatch label to the legend in the original plot.
        
        Examples
        --------
        >>> 
    """
    # Assemble hatches
    hatches = []
    for i in range(len(hatch_levels)):
        if mark_levels[i] == True:
            hatches.append(hatch_style * hatch_density)
            hatches_style = hatches[i]
        else:
            hatches.append('') 
    # Add hatches to the axis
    hatch_overlay = dataset[var].plot.contourf(
        ax=hatch_axis,
        transform=ccrs.PlateCarree(), # if not transformed, the data will become very distorted
        robust=True,
        colors='none',
        levels=hatch_levels,
        hatches=hatches,
        add_colorbar=False,
    )
    # Manually change the hatch color
    hatch_overlay._hatch_color = hatch_color
    # Add contour to frame the hatched area
    if not isinstance(contour_level, type(None)):
        if verbose:
            print(f"(add_hatches) Adding a contour at the `contour_level`:{contour_level}")
        # Add contour line to frame the hatches
        contour_line = dataset[var].plot.contour(
            ax=hatch_axis,
            transform=ccrs.PlateCarree(),  # if not transformed, the data will become very distorted
            robust=True,
            levels=[contour_level],
            colors=[hatch_color],
            linewidths=0.5,
        )
    # Add label for the legend
    hatch_legend = mpl.patches.Patch(label=hatch_label, facecolor='none', edgecolor=hatch_color, hatch=hatches_style)
    handles, labels = plt.gca().get_legend_handles_labels()
    handles.extend([hatch_legend])

    return handles
