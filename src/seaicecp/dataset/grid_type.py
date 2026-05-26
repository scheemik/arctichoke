import xarray as xr 

from seaicecp.verify import verify_path
from seaicecp.dataset.get_variable import get_variable_name

def get_grid_type(
    dataset: (str, xr.DataArray, xr.Dataset),
):
    """ Get the grid type of the dataset.

        Opens the given datasets, checks the dimensions, and determines the type of grid: regular, irregular, or other.

        Parameters
        ----------
        dataset : `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset for which to determine the grid type.

        Returns
        -------
        grid_type : `str`
            The type of grid that the dataset has which will be `'regular'`, `'irregular'`, or `'other'`.
        
        Examples
        --------
        >>> from seaicecp.dataset.grid_type import get_grid_type
        >>> get_grid_type('/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201401-201412.nc')
        irregular
    """
    # Verify input arguments
    if not isinstance(dataset, (str, xr.Dataset, xr.DataArray)):
        raise TypeError(f"(get_grid_type) `dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(dataset)}")
    if isinstance(dataset, str):
        # Verify this is a valid path
        dataset = verify_path(dataset)
        if not dataset.endswith('.nc'):
            raise TypeError(f"(get_grid_type) `dataset` must be a `.nc` filepath. Got: {dataset}")
        # Open the dataset
        dataset = xr.open_dataset(dataset)
    
    # Get the variable name for this dataset
    variable_id = get_variable_name(dataset)
    
    # Get the names of the dimensions of the dataset
    ## Note: Use `.sizes` instead of `.dims` for consistency across Datasets and DataArrays
    dims = list(dataset.sizes.keys())

    # Determine the type of spatial grid the dataset has
    if 'j' in dims and 'i' in dims:
        return 'irregular'
    elif ('lat' in dims and 'lon' in dims) or ('latitude' in dims and 'longitude' in dims):
        return 'regular'
    else:
        return 'other'

def summarize_grid_types(
    datasets: [(str, xr.DataArray, xr.Dataset)],
):
    """ Summarizes the types of grids for the datasets.

        Uses the `get_grid_type()` function on each dataset in the list and reports the number of datasets with the grid types `'regular'`, `'irregular'`, or `'other'`.

        Parameters
        ----------
        datasets : List of `str`, `xarray.DataArray`, `xarray.Dataset`
            The list of datasets for which to summarize the grid types.

        Returns
        -------
        grid_type_dict : `dict`
            A dictionary showing the number of datasets with the grid types `'regular'`, `'irregular'`, or `'other'`.
        
        Examples
        --------
        >>> from seaicecp.path import list_variable_files
        >>> this_list = list_variable_files(source_id='EC-Earth3P-HR', variable_id='siconc', variant_label='r2i1p2f1')
        >>> from seaicecp.dataset.grid_type import summarize_grid_types
        >>> summarize_grid_types(this_list)
        {'total': 65, 'irregular': 65}
        >>> this_list = list_variable_files(source_id='HadGEM3-GC31-MM', variable_id='siconc', experiment_id='highres-future', variant_label='r1i1p1f1')
        {'total': 36, 'regular': 36}
    """
    # Verify input arguments
    if not isinstance(datasets, type([])):
        raise TypeError(f"(summarize_grid_types) `datasets` must be a list. Got type: {type(datasets)}")
    # Each element in `datasets` is verified by `get_grid_type()`
    
    # Get the grid type of each dataset
    grid_types = []
    for dataset in datasets:
        grid_types.append(get_grid_type(dataset))
    
    # Get the grid types present
    unique_grid_types = list(set(grid_types))
    
    # Make a grid types summary dictionary
    grid_type_dict = {
        'total': len(datasets)
    }
    for this_grid_type in unique_grid_types:
        grid_type_dict[this_grid_type] = sum(1 for g_type in grid_types if g_type == this_grid_type)
    
    return grid_type_dict