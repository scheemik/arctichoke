import numpy as np
import xarray as xr

from arctichoke import get_current_datetime_str
from arctichoke.dataset.get_variable import get_variable_name
import arctichoke.params as sps
from arctichoke.verify import verify_path

def sum_by_year(
    dataset: (str, [str], xr.DataArray, xr.Dataset),
    attr_long_name: str = None,
    attr_units: str = None,
    drop_bnds: bool = False,
    save_as: str = None,
    verbose: bool = False,
    **kwargs,
):
    """ Sum a dataset by year along the time axis.

        Groups the dataset by year and sums each year.
        This results in one time step for each year in the given dataset.

        Parameters
        ----------
        dataset : `str`, list of `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset of which to sum by year.
        attr_long_name : `str`, `None`, optional
            The name of the variable for which to put in the `long_name` attribute.
            Default is `None`, which uses the original `long_name` plus `'Yearly Sum of '`.
        attr_units : `str`, `None`, optional
            The units of the variable for which to put in the `units` attribute.
            Default is `None`, which uses the original `units` plus `'_per_year'`.
        drop_bnds : `bool`, optional
            Whether to drop all meta variables that contain `bnds` such as `latitude_bnds`.
            Default is `False`.
        save_as : `str`, `None`, optional
            The file name to which to save the modified dataset.
            Default is `None`, which doesn't save the dataset to a file.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `xr.sum()`.

        Returns
        -------
        dataset : `xarray.Dataset`
            A dataset where the data has been summed by year.
        
        Examples
        --------
        >>> from arctichoke.dataset.example_dataset import make_example_dataset
        >>> dataset = make_example_dataset(n=3, time_dim='time', time_len=2)
        >>> dataset['test_var'].values
        array([[[0., 1., 2.],
                [3., 4., 5.],
                [6., 7., 8.]],

               [[0., 1., 2.],
                [3., 4., 5.],
                [6., 7., 8.]]])
        >>> from arctichoke.analysis.sum_by_year import sum_by_year
        >>> dataset_year_sum = sum_by_year(dataset)
        >>> dataset_year_sum['test_var_year_sum'].values
        array([[[ 0.,  2.,  4.],
                [ 6.,  8., 10.],
                [12., 14., 16.]]])
    """
    # Verify input arguments
    if not isinstance(verbose, bool):
        raise TypeError(f"(sum_by_year) `verbose` must be a `bool`. Got type: {type(verbose)}")
    if isinstance(dataset, str):
        # Wrap that string into a list
        dataset = [dataset]
    if isinstance(dataset, type([])):
        if len(dataset) < 1:
            raise ValueError(f"(sum_by_year) `dataset` must have at least one item. Got: {dataset}")
        for datafile in dataset:
            if not isinstance(datafile, str):
                raise TypeError(f"(sum_by_year) Each item in `dataset` list must be a string. Got: {type(datafile)}")
            # Verify this is a valid path
            datafile = verify_path(datafile)
            if not datafile.endswith('.nc'):
                raise TypeError(f"(sum_by_year) `datafile` must be a `.nc` filepath. Got: {datafile}")
        # Load all the files at once
        if verbose:
            print(f"(sum_by_year) When passing a list of files, ensure their coordinates match as that is not verified in this function.")
        dataset = xr.open_mfdataset(dataset)
    elif not isinstance(dataset, (xr.Dataset, xr.DataArray)):
        raise TypeError(f"(sum_by_year) `dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(dataset)}")
    if not isinstance(attr_long_name, (str, type(None))):
        raise TypeError(f"(sum_by_year) `attr_long_name` must be a string or `None`. Got type: {type(attr_long_name)}")
    if not isinstance(attr_units, (str, type(None))):
        raise TypeError(f"(sum_by_year) `attr_units` must be a string or `None`. Got type: {type(attr_units)}")
    if not isinstance(drop_bnds, bool):
        raise TypeError(f"(sum_by_year) `drop_bnds` must be a `bool`. Got type: {type(drop_bnds)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(sum_by_year) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.nc' in save_as:
        raise TypeError(f"(sum_by_year) `save_as` must be a `.nc` filepath. Got: {save_as}")
    
    # Information to output
    if verbose:
        print(f"(sum_by_year) `save_as`: {save_as}")
    
    if isinstance(dataset, xr.Dataset):
        # Get the `data_var` list
        data_var_list = list(dataset.data_vars)
        if verbose:
            print(f"(sum_by_year) `data_var_list`: {data_var_list}")

        # Remove meta variables having to do with time
        for meta_var in sps.meta_vars:
            if 'time' in meta_var or (drop_bnds and 'bnds' in meta_var):
                if meta_var in data_var_list:
                    if verbose:
                        print(f"(sum_by_year) Removing `meta_var`: {meta_var}")
                    dataset = dataset.drop_vars([meta_var])
        
        # Record the fact that `dataset` is an `xr.Dataset`
        dataset_is_Dataset = True
    else:
        dataset_is_Dataset = False

    # Sum the dataset by year
    ## Passing `min_count=1` prevents grid cells with all `nan` values across time from being set to zero instead of the expected `nan`
    ## Removing the `min_count` argument results in a spiky artifact on maps
    dataset = dataset.groupby('time.year').sum(dim='time', min_count=1, **kwargs)
    if verbose:
        print(f"(sum_by_year) Completed summing by year.")
    # return dataset

    if dataset_is_Dataset:
        # Get the name of the variable in the dataset
        var_name = get_variable_name(dataset)
        if not isinstance(var_name, str):
            raise ValueError(f"(sum_by_year) `dataset` must only have one variable. Available variables: {var_name}")
        # Rename the variable, giving it the suffix `_year_sum`
        dataset = dataset.rename_vars({var_name: f'{var_name}_year_sum'})
        # Get the reference to this variable
        xr_var_to_add_attrs = dataset[f'{var_name}_year_sum']
        # Add this operation to the history
        if 'history' in dataset.attrs.keys():
            original_history = dataset.attrs['history']
        else:
            original_history = ''
        dataset.attrs['history'] = f"{get_current_datetime_str()} altered by `arctichoke`: Calculated the sum of the `{var_name}` values per year in `{var_name}_year_sum`. {original_history}"
    else:
        # Get the name of the variable in the dataset
        var_name = dataset.name
        # Get the reference to this variable
        xr_var_to_add_attrs = dataset
    
    if var_name == 'silandfast':
        if isinstance(attr_long_name, type(None)):
            attr_long_name = "Annual Landfast Ice Months"
        if isinstance(attr_units, type(None)):
            attr_units = "months/yr"

    if verbose:
        print(f"(sum_by_year) Modifying the dataset attributes.")
    # Modify the attributes of the dataset to reflect the changes
    xr_var_to_add_attrs.attrs['standard_name'] = f'{var_name}_year_sum'
    if not isinstance(attr_long_name, type(None)):
        xr_var_to_add_attrs.attrs['long_name'] = attr_long_name
    elif 'long_name' in xr_var_to_add_attrs.attrs.keys():
        xr_var_to_add_attrs.attrs['long_name'] = f'Yearly Sum of {xr_var_to_add_attrs.attrs['long_name']}'
    else:
        xr_var_to_add_attrs.attrs['long_name'] = f'Yearly Sum of {var_name}'
    if not isinstance(attr_units, type(None)):
        xr_var_to_add_attrs.attrs['units'] = attr_units
    elif 'units' in xr_var_to_add_attrs.attrs.keys():
        xr_var_to_add_attrs.attrs['units'] = f'{xr_var_to_add_attrs.attrs['units']}/yr'
    else:
        xr_var_to_add_attrs.attrs['units'] = f'N/P'
    if 'comment' in xr_var_to_add_attrs.attrs.keys():
        xr_var_to_add_attrs.attrs['comment'] = f'Yearly Sum of {xr_var_to_add_attrs.attrs['comment']}'
    else:
        xr_var_to_add_attrs.attrs['comment'] = f'N/P'
    xr_var_to_add_attrs.attrs['original_name'] = f'{var_name}_year_sum'
    if 'history' in xr_var_to_add_attrs.attrs.keys():
        original_history = xr_var_to_add_attrs.attrs['history']
    else:
        original_history = ''
    xr_var_to_add_attrs.attrs['history'] = f"{get_current_datetime_str()} altered by `arctichoke`: Calculated the sum of the `{var_name}` values to get `{var_name}_year_sum`. {original_history}"
    
    # Save the modified dataset, if applicable
    if not isinstance(save_as, type(None)):
        if verbose:
            print(f"(sum_by_year) Saving the dataset file: {save_as}")
        # Save the plot to file
        dataset.to_netcdf(save_as)
        if verbose:
            print(f"(sum_by_year) Done saving dataset file.")
    
    return dataset
