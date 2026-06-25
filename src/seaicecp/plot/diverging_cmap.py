import bokeh.palettes
import holoviews as hv
# Set the backend for `holoviews`
hv.extension("bokeh")

def make_diverging_cmap(
    cmin: (int, float),
    cmax: (int, float),
    cmid: (int, float) = 0,
    ncolors: int = 256, 
    verbose: bool = False,
    **kwargs,
):
    """ Create a diverging colormap where the selected middle value is always white.

        Make a custom diverging blue-white-red colormap with the given maximum and mininmum values, adjusted such that the selected middle value is white and the shorter end is cut off in color if the two ranges on either side of the middle value are uneven to preserve visual value perception.

        Parameters
        ----------
        cmin : `int`, `float`
            The minimum value for the colormap. 
        cmax : `int`, `float`
            The maximum value for the colormap.
        cmid : `int`, `float`, optional
            The middle value at which the colormap should be white.
            Default is `0`.
        ncolors : `int`, optional
            The number of colors to use in the colormap.
            Default is `256`.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `bokeh.palettes.diverging_palette()`.

        Returns
        -------
        diverging_cmap : `tuple`
            The colors of the diverging colormap with a length of `ncolors`.
        
        Examples
        --------
        >>> from seaicecp.plot.diverging_cmap import make_diverging_cmap
    """
    # Verify input arguments
    if not isinstance(cmin, (int, float)):
        raise TypeError(f"(make_diverging_cmap) `cmin` must be `int` or `float`. Got type: {type(cmin)}")
    if not isinstance(cmax, (int, float)):
        raise TypeError(f"(make_diverging_cmap) `cmax` must be `int` or `float`. Got type: {type(cmax)}")
    if cmin > cmax:
        raise ValueError(f"(make_diverging_cmap) `cmin` ({cmin}) must be less than `cmax` ({cmax})")
    if not isinstance(cmid, (int, float)):
        raise TypeError(f"(make_diverging_cmap) `cmid` must be `int` or `float`. Got type: {type(cmid)}")
    if cmid < cmin or cmid > cmax:
        raise ValueError(f"(make_diverging_cmap) `cmid` ({cmid}) must be greater than `cmin` ({cmin}) and must be less than `cmax` ({cmax})")
    if not isinstance(ncolors, (int, float)):
        raise TypeError(f"(make_diverging_cmap) `ncolors` must be `int`. Got type: {type(ncolors)}")
    if ncolors < 2:
        raise ValueError(f"(make_diverging_cmap) `ncolors` must be greater than or equal to 2. Got: {ncolors}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(make_diverging_cmap) `verbose` must be a `bool`. Got type: {type(verbose)}")
    
    # Find the total range
    total_range = cmax - cmin
    # Find which end of the range is farther from the middle
    range_below_mid = cmid - cmin 
    range_above_mid = cmax - cmid
    # Set the normalized point
    c_diverge_point_normalized = (range_below_mid) / (total_range)
    palette_cutoff = round(c_diverge_point_normalized * ncolors)-1
    if range_below_mid > range_above_mid:
        if verbose:
            print(f"(make_diverging_cmap) Shortening the Reds")
            print(f"(make_diverging_cmap) `palette_cutoff`: {palette_cutoff}")
        diverging_cmap = bokeh.palettes.diverging_palette(
            bokeh.palettes.Blues[ncolors],
            bokeh.palettes.Reds[ncolors][palette_cutoff:],
            n=ncolors,
            midpoint=c_diverge_point_normalized,
            **kwargs,
        )
    elif range_below_mid == range_above_mid:
        if verbose:
            print(f"(make_diverging_cmap) Reds and Blues are even")
            print(f"(make_diverging_cmap) `palette_cutoff`: {palette_cutoff}")
        diverging_cmap = bokeh.palettes.diverging_palette(
            bokeh.palettes.Blues[ncolors],
            bokeh.palettes.Reds[ncolors],
            n=ncolors,
            midpoint=c_diverge_point_normalized,
            **kwargs,
        )
    else:
        if verbose:
            print(f"(make_diverging_cmap) Shortening the Blues")
            print(f"(make_diverging_cmap) `palette_cutoff`: {palette_cutoff}")
        diverging_cmap = bokeh.palettes.diverging_palette(
            bokeh.palettes.Blues[ncolors][palette_cutoff:],
            bokeh.palettes.Reds[ncolors],
            n=ncolors,
            midpoint=c_diverge_point_normalized,
            **kwargs,
        )
    # Insert white (#ffffff) into the middle of the colormap
    if verbose:
        print(f"(make_diverging_cmap) Adding white (#ffffff) to the middle of the colormap")
    diverging_cmap = diverging_cmap[:palette_cutoff] + ('#ffffff',) + diverging_cmap[palette_cutoff:]
    return diverging_cmap
