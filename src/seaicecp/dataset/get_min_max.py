import xarray as xr 

from seaicecp.dataset.get_variable import get_variable_name
from seaicecp.verify import verify_path

def get_min_max(
    dataset: (str, xr.DataArray, xr.Dataset),
    var: str = None,
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

        Returns
        -------
        var_min : `int`, `float`
            The minimum value of the data.
        var_max : `int`, `float`
            The maximum value of the data.
        
        Examples
        --------
        >>> from seaicecp.dataset.example_dataset import make_example_dataset
        >>> from seaicecp.dataset.get_min_max import get_min_max
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
        if var not in actual_vars:
            raise ValueError(f"(trend_in_time) `dataset` must have the specified `var` {var}. Available variables: {actual_vars}")
        dataset = dataset[var]
    
    # Get the minimum value
    var_min = dataset.min(skipna=True).item()
    # Get the maximum value
    var_max = dataset.max(skipna=True).item()

    return var_min, var_max
