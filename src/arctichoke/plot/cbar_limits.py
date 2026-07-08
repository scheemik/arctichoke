from bokeh.models import LinearColorMapper, ColorBar
from bokeh.plotting import show
import holoviews as hv
import numpy as np

def set_cbar_lims(
    hv_overlay: (hv.core.overlay.Overlay, hv.element.raster.QuadMesh),
    cmin: (int, float),
    cmax: (int, float),
    verbose: bool = False,
    **kwargs,
):
    """ Limit the colorbar range without changing the colors.

        Set the limits of the colorbar in the given overlay object such that the displayed range of the colorbar is within those limits but the colors to which every value corresponds remains the same as the original.
        This is done by completely replacing the original colorbar with a new one where the range has been limited.

        Parameters
        ----------
        hv_overlay : `holoviews.core.overlay.Overlay`, `holoviews.element.raster.QuadMesh`
            The overlay object for which to construct the limited colorbar.
        cmin : `int`, `float`
            The minimum display value for the colormap. 
        cmax : `int`, `float`
            The maximum display value for the colormap.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `bokeh.models.LinearColorMapper()` and `bokeh.models.ColorBar()`.

        Returns
        -------
        fig : `bokeh.plotting._figure.figure`
            The figure containing the original plot and the new, limited colorbar.
        
        Examples
        --------
        >>> from arctichoke.plot.cbar_limits import set_cbar_lims
    """
    # Verify input arguments
    if not isinstance(hv_overlay, (hv.core.overlay.Overlay, hv.element.raster.QuadMesh)):
        raise TypeError(f"(set_cbar_lims) `hv_overlay` must be `hv.core.overlay.Overlay` or `hv.element.raster.QuadMesh`. Got type: {type(hv_overlay)}")
    if not isinstance(cmin, (int, float)):
        raise TypeError(f"(set_cbar_lims) `cmin` must be `int` or `float`. Got type: {type(cmin)}")
    if not isinstance(cmax, (int, float)):
        raise TypeError(f"(set_cbar_lims) `cmax` must be `int` or `float`. Got type: {type(cmax)}")
    if cmin > cmax:
        raise ValueError(f"(set_cbar_lims) `cmin` ({cmin}) must be less than `cmax` ({cmax})")
    if not isinstance(verbose, bool):
        raise TypeError(f"(set_cbar_lims) `verbose` must be a `bool`. Got type: {type(verbose)}")
    
    # Convert the overlay to a Bokeh figure
    renderer = hv.renderer("bokeh")
    plot = renderer.get_plot(hv_overlay)
    fig = plot.state

    # Check for existing colorbar
    old_cb = None
    for item in fig.right:
        if isinstance(item, ColorBar):
            old_cb = item
            break

    # Remove the existing colorbar
    if not isinstance(old_cb, type(None)):
        fig.right.remove(old_cb)
    else:
        print("Warning: Given `hv_overlay` does not contain a colorbar.")
        return fig

    # Extract title, mapper, and color palette from original colorbar
    cbar_title = old_cb.title
    orig_mapper = old_cb.color_mapper
    palette = orig_mapper.palette
    # Get max and min of original mapper
    full_low = orig_mapper.low
    full_high = orig_mapper.high

    if verbose:
        print(f"(set_cbar_lims) Original colorbar range: {full_low} to {full_high}")
        print(f"(set_cbar_lims) Limited colorbar range: {cmin} to {cmax}")

    # Get the fraction of the full range occupied by data
    f0 = (cmin - full_low) / (full_high - full_low)
    f1 = (cmax - full_low) / (full_high - full_low)
    # Convert the fractions to indices of the palette
    ncolors = len(palette)
    i0 = max(0, int(np.floor(f0 * (ncolors - 1))))
    i1 = min(ncolors - 1, int(np.ceil(f1 * (ncolors - 1))))
    # Take just the indices of the original color palette for the limited range
    cropped_palette = palette[i0:i1 + 1]

    # Create custom colorbar mapper
    cb_mapper = LinearColorMapper(
        palette = cropped_palette,
        low = cmin,
        high = cmax,
    )
    # Create the custom colorbar
    custom_cb = ColorBar(
        color_mapper = cb_mapper,
        label_standoff = 12,
        bar_line_color = 'black',
        major_tick_line_color = 'black',
        title = cbar_title,
    )
    # Add the custom colorbar in the old colorbar's place
    fig.add_layout(custom_cb, "right")
    
    show(fig)
    return fig