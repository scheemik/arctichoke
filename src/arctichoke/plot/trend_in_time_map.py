import xarray as xr

from arctichoke.analysis import sum_by_year, trend_in_time, trend_in_time_scipy
from arctichoke.analysis.significance import find_significance 
from arctichoke.dataset import make_mask, select_months
from arctichoke.dataset.interp_dataset import interp_to_reg_grid
import arctichoke.params as sps
from arctichoke.path import list_variable_files
from arctichoke.plot.plot_map import plot_map
from arctichoke.plot.stippling import add_hatches

def make_trend_map(
    this_source_id: str,
    this_var: str,
    this_variant_label: str,
    this_modification: str,
    calc_pvals: bool = False,
    mask_where_zero_across_time: (bool, xr.DataArray) = True,
    select_summer: bool = True,
    call_sum_by_year: bool = True,
    find_mean: bool = False,
    map_projection: str = 'Orthographic',
    use_hvplot: bool = False,
    add_sig: bool = True,
    re_trim_extent: bool = True,
    return_map: bool = False,
    verbose: bool = False,
    **kwargs,
):
    """ Plot the trends of the given data on a map.

        For each grid cell in the dataset, calculate the yearly sum, then find the trend in time for the given variable and plot it on a map. 

        Parameters
        ----------
        this_source_id : `str`
            The source ID of the model to plot.
            Example: `'EC-Earth3P-HR'`.
        this_var : `str`
            The variable ID of the variable to plot.
            Example: `'silandfast'`.
        this_variant_label : `str`
            The variant label of the model to plot.
            Example: `'r1i1p2f1'`.
        this_modification : `str`
            The modification of the data to plot.
            Example: `'trim_CAA_'`.
        calc_pvals : `bool`, optional
            Whether to use the version of `trend_in_time()` which calculates p-values.
            Default is `False`.
        mask_where_zero_across_time : `bool`, `xarray.DataArray`, optional
            Whether to mask out grid cells which have zero as a value across the entire time dimension using `mask_where_all_zero()`, which only applies to "marker" variables.
            If a `xarray.DataArray` is given, it is used as a mask.
            Default is `False`. 
        select_summer : `bool`, optional
            Whether to use `select_months()` to only plot the summer months (June-October).
            Default is `True`.
        call_sum_by_year : `bool`, `None`, optional
            Whether to use `sum_by_year()` to sum the variable across each year before taking the trends across time.
            Default is `True`.
        find_mean : `bool`, optional
            Whether to find the mean instead of sum when calling `sum_by_year()`.
            This is only relevant when `call_sum_by_year` is `True` or when it is `None` and `this_var` is a marker variable.
            Default is `False`.
        map_projection : `str`, optional
            The map projection to use.
            Default is `'Orthographic'`.
        use_hvplot : `bool`, optional
            Whether to use `hvplot` or `cartopy` to make the map.
            Default is `True` which uses `hvplot` and, if `False`, uses `cartopy` instead.
        add_sig : `bool`, optional
            Whether or not to add an overlay for the statisitcal significance of the trends.
            Default is `True`.
        re_trim_extent : `bool`, optional
            Whether or not to reset the extent of the plot to avoid showing the full globe after adding a significance overlay.
            Default is `True`.
        return_map : `bool`, optional
            Whether to return the map object or not.
            Default is `False`.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `list_variable_files()` and `plot_map()`.

        Returns
        -------
        trend_map_axis : `holoviews.core.overlay.Overlay`
            The map of the trends in time for the given variable.
        
        Examples
        --------
        >>> from arctichoke.plot import make_trend_map
        >>> make_trend_map(
        >>>     this_source_id = 'EC-Earth3P-HR',
        >>>     this_var = 'silandfast',
        >>>     this_variant_label = 'r1i1p2f1',
        >>>     this_modification = 'trim_CAA_',
        >>>     verbose = True,
        >>> )
    """
    # Verify input arguments
    if not isinstance(calc_pvals, bool):
        raise TypeError(f"(make_trend_map) `calc_pvals` must be a `bool`. Got type: {type(calc_pvals)}")
    if not isinstance(select_summer, bool):
        raise TypeError(f"(make_trend_map) `select_summer` must be a `bool`. Got type: {type(select_summer)}")
    if not isinstance(call_sum_by_year, (bool, type(None))):
        raise TypeError(f"(make_trend_map) `call_sum_by_year` must be a `bool` or `None`. Got type: {type(call_sum_by_year)}")
    if not isinstance(find_mean, (bool, type(None))):
        raise TypeError(f"(make_trend_map) `find_mean` must be a `bool` or `None`. Got type: {type(find_mean)}")
    if not isinstance(use_hvplot, bool):
        raise TypeError(f"(make_trend_map) `use_hvplot` must be a `bool`. Got type: {type(use_hvplot)}")
    if not isinstance(add_sig, bool):
        raise TypeError(f"(make_trend_map) `add_sig` must be a `bool`. Got type: {type(add_sig)}")
    if not isinstance(re_trim_extent, bool):
        raise TypeError(f"(make_trend_map) `re_trim_extent` must be a `bool`. Got type: {type(re_trim_extent)}")
    if not isinstance(return_map, bool):
        raise TypeError(f"(make_trend_map) `return_map` must be a `bool`. Got type: {type(return_map)}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(make_trend_map) `verbose` must be a `bool`. Got type: {type(verbose)}")
    # Get the list of `this_var` files
    filelist = list_variable_files(
        source_id = this_source_id,
        variable_id = this_var,
        variant_label = this_variant_label,
        with_modification = this_modification,
        verbose = verbose,
        **kwargs,
    )
    # Open those files into a multi-file dataset
    if select_summer:
        dataset = select_months(
            filelist,
            verbose = verbose,
        )
    else:
        dataset = xr.open_mfdataset(
            filelist,
            data_vars = 'all'
        )
    # 
    if isinstance(call_sum_by_year, type(None)):
        # Check whether this variable is in the sea ice vars dictionary
        if this_var in sps.sea_ice_vars.keys():
            # Check whether this is a marker variable or not
            if sps.sea_ice_vars[this_var]['marker_var']: 
                call_sum_by_year = True 
            else:
                call_sum_by_year = False
        if verbose:
            print(f"(make_trend_map) `this_var` ({this_var}) is marker variable: {call_sum_by_year}")
    # Sum the data across time
    if call_sum_by_year:
        ## Overwrite the `dataset` variable to reduce memory overhead
        dataset = sum_by_year(
            dataset,
            find_mean = find_mean,
            verbose = verbose,
        )
        if find_mean:
            var_for_trend = f'{this_var}_year_mean'
        else:
            var_for_trend = f'{this_var}_year_sum'
        this_time_dim = 'year'
    else:
        var_for_trend = this_var
        this_time_dim = 'time'
    # Take the trend across time
    if calc_pvals:
        trend_dataset = trend_in_time_scipy(
            dataset = dataset,
            var = var_for_trend,
            mask_where_zero_across_time = False,
            verbose = verbose,
            time_dim = this_time_dim,
        )
    else:
        trend_dataset = trend_in_time(
            dataset = dataset,
            var = var_for_trend,
            mask_where_zero_across_time = mask_where_zero_across_time,
            verbose = verbose,
            time_dim = this_time_dim,
        )
    # Find the trend significance and interpolate the data, if necessary
    if use_hvplot == False:
        # Find the significance of trends dataset
        trend_dataset = find_significance(
            dataset,
            trend_dataset,
            var_for_trend,
            this_time_dim,
            verbose = verbose,
        )
        # Interpolate these datasets
        trend_dataset = interp_to_reg_grid(
            dataset = trend_dataset,
            targetgrid = 'data/target_grid_0-25_deg.nc',
            verbose = verbose,
            **kwargs,
        )
    # Plot the trends on a map
    trend_map_axis, plot_map_kwargs = plot_map(
        trend_dataset,
        f'{var_for_trend}_trends',
        map_projection = map_projection,
        diverging_cbar = True,
        use_hvplot = use_hvplot,
        verbose = verbose,
        return_plot_map_kwargs = True,
        **kwargs,
    )
    # Add trend significance to the map
    if use_hvplot == False and add_sig == True:
        # Re-interpolate the data for the significance of trends
        sig_trend_dataset = make_mask(
            trend_dataset,
            f'{var_for_trend}_trends_sig',
            mask_var_name = f'{var_for_trend}_trends_sig',
            mask_this_range = [0.9, 1.1],
            val_inside_range = 1,
            val_outside_range = 0,
            verbose = verbose,
        )
        # Add hatch lines
        handles = add_hatches(
            hatch_axis = trend_map_axis, 
            dataset = sig_trend_dataset,
            var = f'{var_for_trend}_trends_sig',
            hatch_label = 'significant',
            verbose = verbose,
            **kwargs,
        )
        # Add label for the hatches in the legend
        trend_map_axis.legend(handles=handles, loc='upper right')
        # Reset the map extent
        if re_trim_extent:
            map_extent = plot_map_kwargs['map_extent']
            map_projection = plot_map_kwargs['map_projection']
            if not isinstance(map_extent, type(None)):
                trend_map_axis.set_extent(
                    (map_extent[0], map_extent[1],
                    map_extent[2], map_extent[3]),
                    crs = map_projection,
                )
        # Set the axis title
        trend_map_axis.set_title(plot_map_kwargs['map_title'])

    if return_map:
        return trend_map_axis
    trend_map_axis