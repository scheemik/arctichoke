import xarray as xr

from arctichoke.analysis import sum_by_year, trend_in_time, trend_in_time_scipy
from arctichoke.dataset import select_months
import arctichoke.params as sps
from arctichoke.path import list_variable_files
from arctichoke.plot import make_title, quadmesh_map

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
            Whether to find the mean instead of sum when calling `sum_by_year.
            This is only relevant when `call_sum_by_year` is `True` or when it is `None` and `this_var` is a marker variable.
            Default is `False`.
        map_projection : `str`, optional
            The map projection to use.
            Default is `'Orthographic'`.
        return_map : `bool`, optional
            Whether to return the map object or not.
            Default is `False`.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `list_variable_files()` and `quadmesh_map()`.

        Returns
        -------
        sum_year_trend_map : `holoviews.core.overlay.Overlay`
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
    if not isinstance(return_map, bool):
        raise TypeError(f"(make_trend_map) `return_map` must be a `bool`. Got type: {type(return_map)}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(make_trend_map) `verbose` must be a `bool`. Got type: {type(verbose)}")
    # Get the list of `silandfast` files
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
        dataset = trend_in_time_scipy(
            dataset = dataset,
            var = var_for_trend,
            mask_where_zero_across_time = False,
            verbose = verbose,
            time_dim = this_time_dim,
        )
    else:
        dataset = trend_in_time(
            dataset = dataset,
            var = var_for_trend,
            mask_where_zero_across_time = mask_where_zero_across_time,
            verbose = verbose,
            time_dim = this_time_dim,
        )
    # Plot the trends on a map
    sum_year_trend_map = quadmesh_map(
        dataset,
        f'{var_for_trend}_trends',
        map_projection = map_projection,
        diverging_cbar = True,
        verbose = verbose,
        **kwargs,
    )
    if return_map:
        return sum_year_trend_map
    sum_year_trend_map