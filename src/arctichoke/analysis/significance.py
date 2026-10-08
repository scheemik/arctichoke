import numpy as np
import xarray as xr

from arctichoke.analysis import find_standard_error, trend_in_time, make_mask
from arctichoke.dataset import get_variable_name

def find_significance(
    dataset: (xr.DataArray, xr.Dataset),
    trend_dataset: xr.Dataset,
    var: str,
    time_dim: str = 'year',
    verbose: bool = False,
    **kwargs,
):
    """ Sum a dataset by year along the time axis.

        Groups the dataset by year and sums each year.
        This results in one time step for each year in the given dataset.

        Parameters
        ----------
        dataset : `xarray.DataArray`, `xarray.Dataset`
            The original dataset from which trends were found.
        trend_dataset : `xarray.Dataset`
            The dataset of trends calculated from the original dataset using `trend_in_time()`.
            These are the trends whose significance will be found.
        var : `str`, `None`
            The name of the variable from the original dataset.
            Expects that the name of the trend variable from `trend_dataset` is `f'{var}_trends'`.
        time_dim : `str`, optional
            The name of the time dimension over which the trends were found.
            Default is `year`. 
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to handle extras that might have been passed by the function above this one.

        Returns
        -------
        trend_dataset : `xarray.Dataset`
            The same as the given `trend_dataset`, but with a new variable of the trend significance added.
        
        Examples
        --------
        >>> 
    """
    # Verify input arguments
    if not isinstance(dataset, (xr.Dataset, xr.DataArray)):
        raise TypeError(f"(find_significance) `dataset` must be `xr.Dataset` or `xarray.DataArray`. Got type: {type(dataset)}")
    if not isinstance(trend_dataset, xr.Dataset):
        raise TypeError(f"(find_significance) `trend_dataset` must be `xr.Dataset`. Got type: {type(trend_dataset)}")
    if not isinstance(var, (str, type(None))):
        raise TypeError(f"(find_significance) `var` must be a string or `None`. Got type: {type(var)}")
    if not isinstance(time_dim, str):
        raise TypeError(f"(find_significance) `time_dim` must be a string. Got type: {type(time_dim)}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(find_significance) `verbose` must be a `bool`. Got type: {type(verbose)}")

    # Verify `dataset` has the specified variable
    if isinstance(dataset, xr.Dataset):
        actual_vars = get_variable_name(dataset)
        if var not in actual_vars:
            raise ValueError(f"(find_significance) `dataset` must have the specified `var` {var}. Available variables: {actual_vars}")
    else:
        # Get the name of the variable
        var = dataset.name
        # Convert `dataset` from `xr.DataArray` to `xr.Dataset`
        dataset = dataset.to_dataset()
    # Verify `trend_dataset` has the needed variables
    actual_vars = get_variable_name(trend_dataset)
    for trend_var in [f'{var}_trends', f'{var}_intercepts']:
        if trend_var not in actual_vars:
            raise ValueError(f"(find_significance) `trend_dataset` must have the specified trend variable {trend_var}. Available variables: {actual_vars}")
    
    # Find the trend lines
    x = dataset[time_dim].values
    m = trend_dataset[f'{var}_trends'].values
    b = trend_dataset[f'{var}_intercepts'].values
    trend_start = m * x[0] + b
    trend_end = m * x[-1] + b
    # Find the standard error
    stderr = find_standard_error(
        trend_dataset[f'{var}_residuals'],
        trend_dataset.attrs['original_time_length'],
    )
    # Find the standard error interval from the trend end
    interval_upper = trend_end + stderr
    interval_lower = trend_end - stderr
    # If trend_start is between interval_upper and interval_lower, then we will find
    #  (interval_lower - trend_start) is negative and (interval_upper - trend_start) is positive
    # If trend_start is below the interval, both those will be positive
    # If trend_start is above the interval, both those will be negative
    # Therefore, the trend isn't significant if and only if the following result is negative
    trend_dataset[f'{var}_significance_test'] = (interval_lower - trend_start) * (interval_upper - trend_start)

    # Get the minimum possible integer to cover all reasonable values
    numpy_int32_min = np.iinfo(np.int32).min
    # Mask out trends that aren't significant below the threshold
    trend_sig_dataset = make_mask(
        trend_dataset,
        var = f'{var}_significance_test',
        mask_var_name = f'{var}_trends_sig',
        mask_this_range = [numpy_int32_min, 0],
        val_inside_range = 0,
        val_outside_range = 1,
        verbose = verbose,
    )
    # Add the trend significance to the trend dataset
    trend_dataset[f'{var}_trends_sig'] = trend_sig_dataset[f'{var}_trends_sig']
    return trend_dataset