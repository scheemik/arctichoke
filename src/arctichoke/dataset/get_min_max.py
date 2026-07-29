import numpy as np
import xarray as xr 

from arctichoke.dataset.get_variable import get_variable_name
from arctichoke.verify import verify_path

def get_min_max(
    dataset: (str, xr.DataArray, xr.Dataset),
    var: str = None,
    ignore_val: (int, float) = None,
    ignore_tol: (int, float) = 1,
    verbose: bool = False,
    **kwargs,
):
    """ Get the minimum / maximum of the dataset.

        Opens the given dataset, finds the given variable if `xr.Dataset`, returns the minimum / maximum values of that data.

        Parameters
        ----------
        dataset : `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset for which to determine the minimum / maximum values.
        var : `str`, `None`, optional
            The variable in `dataset` for which to find the minimum / maximum.
            Default is `None`. 
        ignore_val : `int`, `float`, `None`, optional
            A value which will be ignored when finding the minimum and maximum values.
            Default is `None`, which does not ignore any values.
        ignore_tol : `int`, `float`, optional
            A tolerance around `ignore_val` which will be counted as the value to ignore.
            This tolerance is applied evenly on either side of `ignore_val`.
            For example, with `ignore_val=0` and `ignore_tol=1`, values between `-1` and `1` will be ignored.
            Default is `1`.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to handle extras that might have been passed by the function above this one.

        Returns
        -------
        var_min : `int`, `float`
            The minimum value of the data.
        var_max : `int`, `float`
            The maximum value of the data.
        
        Examples
        --------
        >>> from arctichoke.dataset.example_dataset import make_example_dataset
        >>> from arctichoke.dataset.get_min_max import get_min_max
        >>> dataset = make_example_dataset(n=3)
        >>> min, max = get_min_max(dataset, var='test_var')
        >>> print('min:',min,'max:',max)
        min: 0.0 max: 8.0
    """
    # Verify input arguments
    if not isinstance(dataset, (str, xr.Dataset, xr.DataArray)):
        raise TypeError(f"(get_min_max) `dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(dataset)}")
    if isinstance(dataset, str):
        if not dataset.endswith('.nc'):
            raise ValueError(f"(get_min_max) `dataset` must be a `.nc` filepath. Got: {dataset}")
        # Verify this is a valid path
        dataset = verify_path(dataset)
        # Open the dataset
        dataset = xr.open_dataset(dataset)
    if isinstance(dataset, xr.Dataset):
        if not isinstance(var, str):
            raise TypeError(f"(get_min_max) `var` must be a string. Got type: {type(var)}")
        # Verify `dataset` has the specified variable
        actual_vars = get_variable_name(dataset)
        if var not in actual_vars and var not in list(dataset.coords):
            raise ValueError(f"(get_min_max) `dataset` must have the specified `var` {var}. Available variables: {actual_vars}")
        dataset = dataset[var]
    if not isinstance(ignore_val, (int, float, type(None))):
        raise TypeError(f"(get_min_max) `ignore_val` must be an integer, `float` or `None`. Got type: {type(ignore_val)}")
    if not isinstance(ignore_tol, (int, float)):
        raise TypeError(f"(get_min_max) `ignore_tol` must be an integer or `float`. Got type: {type(ignore_tol)}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(get_min_max) `verbose` must be a `bool`. Got type: {type(verbose)}")
    
    # Get the minimum value
    var_min = dataset.min(skipna=True).compute().item()
    # Get the maximum value
    var_max = dataset.max(skipna=True).compute().item()

    # Check whether there are erroneous values near 0 if variable is `latitude` or `longitude`
    if var in ['latitude', 'longitude']:
        if var_min < ignore_tol:
            ignore_val = 0.0
        if verbose: 
            print(f"(get_min_max) Found `var_min` = {var_min} for {var}")
    # Recompute if `ignore_val` is given
    if not isinstance(ignore_val, type(None)):
        if verbose: 
            print(f"(get_min_max) Ignoring value {ignore_val} within a tolerance of {ignore_tol}")
        dataset_ignore_val = dataset.where(lambda a: (a < ignore_val-ignore_tol) | (a > ignore_val+ignore_tol), np.nan)
        # Get the minimum value
        var_min = dataset_ignore_val.min(skipna=True).compute().item()
        # Get the maximum value
        var_max = dataset_ignore_val.max(skipna=True).compute().item()

    return var_min, var_max
