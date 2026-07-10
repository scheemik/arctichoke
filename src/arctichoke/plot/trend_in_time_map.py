import xarray as xr
from arctichoke.analysis.sum_by_year import sum_by_year
from arctichoke.analysis.trend_in_time import trend_in_time
from arctichoke.path.file_lists import list_variable_files
from arctichoke.plot.hvplots import quadmesh_map

def make_trend_map(
    this_source_id: str,
    this_var: str,
    this_variant_label: str,
    this_modification: str,
    mask_where_zero_across_time: bool = True,
    map_projection: str = 'Orthographic',
    verbose: bool = False,
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
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.

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
    # Get the list of `silandfast` files
    filelist = list_variable_files(
        source_id = this_source_id,
        variable_id = this_var,
        variant_label = this_variant_label,
        with_modification = this_modification,
        verbose = verbose,
    )
    # Open those files into a multi-file dataset
    xr_ds = xr.open_mfdataset(
        filelist,
        data_vars = 'all'
    )
    # Sum the data across time
    sum_year_xr = sum_by_year(
        xr_ds,
        verbose = verbose,
    )
    # Take the trend across time
    sum_year_trend_xr = trend_in_time(
        dataset = sum_year_xr,
        var = f'{this_var}_year_sum',
        mask_where_zero_across_time = mask_where_zero_across_time,
        verbose = verbose,
    )
    # Plot the trends on a map
    sum_year_trend_map = quadmesh_map(
        sum_year_trend_xr,
        f'{this_var}_year_sum_trends',
        map_projection = map_projection,
        diverging_cbar = True,
        verbose = verbose,
    )
    sum_year_trend_map