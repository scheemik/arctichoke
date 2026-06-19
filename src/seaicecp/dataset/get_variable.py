import xarray as xr 

from seaicecp.verify import verify_path
from seaicecp.params.var_params import meta_vars

def get_variable_name(
    dataset: (str, xr.DataArray, xr.Dataset),
):
    """ Get the variable name of the dataset.

        Opens the given dataset, checks the data variable attributes, and returns the variable name.

        Parameters
        ----------
        dataset : `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset for which to determine the variable name.

        Returns
        -------
        var_name : `str`
            The name of the variable
        
        Examples
        --------
        >>> from seaicecp.dataset.grid_type import get_variable_name
    """
    # Verify input arguments
    if not isinstance(dataset, (str, xr.Dataset, xr.DataArray)):
        raise TypeError(f"(get_variable_name) `dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(dataset)}")
    if isinstance(dataset, str):
        if not dataset.endswith('.nc'):
            raise TypeError(f"(get_variable_name) `dataset` must be a `.nc` filepath. Got: {dataset}")
        # Verify this is a valid path
        dataset = verify_path(dataset)
        # Open the dataset
        dataset = xr.open_dataset(dataset)
    
    # Get the `data_var` list
    data_var_list = list(dataset.data_vars)

    # Remove meta variables
    for meta_var in meta_vars:
        if meta_var in data_var_list:
            data_var_list.remove(meta_var)

    # Check how many variables are left
    if len(data_var_list) != 1:
        raise ValueError(f"(get_variable_name) Found {len(data_var_list)} variables: {data_var_list}")
    else:
        return data_var_list[0]
