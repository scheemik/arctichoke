import xarray as xr

from arctichoke.analysis import sum_by_year, trend_in_time, trend_in_time_scipy
from arctichoke.dataset import get_field_mean, select_months
import arctichoke.params as sps
from arctichoke.path import list_variable_files, list_variant_labels
from arctichoke.plot import make_title, plot_time_series

def plot_multi_time_series(
    this_source_id: str,
    this_var: str,
    this_modification: str,
    add_regression: bool = True,
    select_summer: bool = True,
    call_sum_by_year: bool = True,
    find_mean: bool = True,
    verbose: bool = False,
    **kwargs,
):
    """ Plot multiple time series on the same axis.

        Plots the specified time series, one for each variant / realization available for the specified model and variable.

        Parameters
        ----------
        this_source_id : `str`
            The source ID of the model to plot.
            Example: `'EC-Earth3P-HR'`.
        this_var : `str`
            The variable ID of the variable to plot.
            Example: `'silandfast'`.
        this_modification : `str`
            The modification of the data to plot.
            Example: `'trim_CAA_'`.
        add_regression : `bool`, optional
            Whether to add a linear regression line to the plot.
            Default is `True`.
        select_summer : `bool`, optional
            Whether to use `select_months()` to only plot the summer months (June-October).
            Default is `True`.
        call_sum_by_year : `bool`, `None`, optional
            Whether to use `sum_by_year()` to sum the variable across each year before taking the trends across time.
            Default is `True`.
        find_mean : `bool`, optional
            Whether to find the mean instead of sum when calling `sum_by_year()`.
            This is only relevant when `call_sum_by_year` is `True` or when it is `None` and `this_var` is a marker variable.
            Default is `True`.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `list_variable_files()` and `plot_time_series()`.

        Returns
        -------
        None
        
        Examples
        --------
        >>> from arctichoke.plot import plot_multi_time_series
        >>> plot_multi_time_series(
        >>>     this_source_id = 'EC-Earth3P-HR',
        >>>     this_var = 'silandfast',
        >>>     this_modification = 'trim_CAA_',
        >>>     verbose = True,
        >>> )
    """
    # Verify input arguments
    if not isinstance(add_regression, (type(True))):
        raise TypeError(f"(plot_multi_time_series) `add_regression` must be a `bool`. Got type: {type(add_regression)}")
    if not isinstance(select_summer, bool):
        raise TypeError(f"(plot_multi_time_series) `select_summer` must be a `bool`. Got type: {type(select_summer)}")
    if not isinstance(call_sum_by_year, (bool, type(None))):
        raise TypeError(f"(plot_multi_time_series) `call_sum_by_year` must be a `bool` or `None`. Got type: {type(call_sum_by_year)}")
    if not isinstance(find_mean, (bool, type(None))):
        raise TypeError(f"(plot_multi_time_series) `find_mean` must be a `bool` or `None`. Got type: {type(find_mean)}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(plot_multi_time_series) `verbose` must be a `bool`. Got type: {type(verbose)}")
    
    # Get the list of variant labels for this model
    variant_label_list = list_variant_labels(
        source_id = this_source_id,
        **kwargs,
    )

    # Loop across the different variant labels
    for i in range(len(variant_label_list)):
        this_variant_label = variant_label_list[i]
        # Get the list of `relevant` files
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
                print(f"(plot_multi_time_series) `this_var` ({this_var}) is marker variable: {call_sum_by_year}")
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
        # Take the spatial mean
        dataset = get_field_mean(
            dataset = dataset,
            verbose = verbose,
        )
        # Get the plot title
        this_plot_title = make_title(
            dataset,
            add_variant_label = False,
        )
        # Plot the time series
        plot_time_series(
            dataset,
            var_for_trend,
            add_regression = add_regression,
            reg_label = this_variant_label,
            line_clr = sps.sb_clrs[i],
            plt_title = this_plot_title,
            verbose = verbose,
            **kwargs,
        )