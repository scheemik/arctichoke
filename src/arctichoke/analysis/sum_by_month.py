import numpy as np
import xarray as xr

from arctichoke import get_current_datetime_str
from arctichoke.dataset.get_variable import get_variable_name
import arctichoke.params as sps
from arctichoke.verify import verify_path

def sum_by_month(
    dataset: (str, [str], xr.DataArray, xr.Dataset),
    attr_long_name: str = None,
    attr_units: str = None,
    drop_bnds: bool = True,
    find_mean: bool = False,
    save_as: str = None,
    verbose: bool = False,
    **kwargs,
):
    """ Sum a dataset by month along the time axis.

        Groups the dataset by month and sums each month.
        This results in one time step for each month in the given dataset, meaning the time axis will be between 1-12 in length.
        Can also use the `find_mean` argument to take the mean instead of the sum.

        Parameters
        ----------
        dataset : `str`, list of `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset of which to sum by month.
        attr_long_name : `str`, `None`, optional
            The name of the variable for which to put in the `long_name` attribute.
            Default is `None`, which uses the original `long_name` plus `'Monthly Sum of '`.
        attr_units : `str`, `None`, optional
            The units of the variable for which to put in the `units` attribute.
            Default is `None`, which uses the original `units` plus `'_per_month'`.
        drop_bnds : `bool`, optional
            Whether to drop all meta variables that contain `bnds` such as `latitude_bnds`.
            Default is `False`.
        find_mean : `boo`, optional
            Whether to take the mean instead of the sum by month.
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
            A dataset where the data has been summed by month.
        
        Examples
        --------
        >>> from arctichoke.dataset import make_example_dataset
        >>> from arctichoke.path import make_file_path
        >>> test_file_dir = 'tests/test_analysis/example_datasets'
        >>> make_file_path(test_file_dir)
        >>> test_file_names = [
        >>>     f"{test_file_dir}/example_dataset_0.nc",
        >>>     f"{test_file_dir}/example_dataset_1.nc",
        >>>     f"{test_file_dir}/example_dataset_2.nc",
        >>> ]
        >>> for i in range(len(test_file_names)):
        >>>     make_example_dataset(
        >>>         n=2,
        >>>         test_var_name='test_var',
        >>>         time_dim='time',
        >>>         time_len=i+2,
        >>>         start_year=(2000+i),
        >>>         offset=i,
        >>>         save_as=test_file_names[i],
        >>>     )
        >>> import xarray as xr 
        >>> test_dataset = xr.open_mfdataset(test_file_names)
        >>> test_dataset['test_var'].values
        array([[[0., 1.],
                [2., 3.]],
                ...
               [[1., 2.],
                [3., 4.]],
                ...
               [[2., 3.],
                [4., 5.]],
                ...
            ])
        >>> from arctichoke.analysis.sum_by_month import sum_by_month
        >>> dataset_month_sum = sum_by_month(test_dataset)
        >>> dataset_month_sum['test_var_month_sum'].values
        array([[[ 3.,  6.],
                [ 9., 12.]],

               [[ 3.,  6.],
                [ 9., 12.]],

               [[ 3.,  5.],
                [ 7.,  9.]],

               [[ 2.,  3.],
                [ 4.,  5.]]])
    """
    # Verify input arguments
    if not isinstance(verbose, bool):
        raise TypeError(f"(sum_by_month) `verbose` must be a `bool`. Got type: {type(verbose)}")
    if isinstance(dataset, str):
        # Wrap that string into a list
        dataset = [dataset]
    if isinstance(dataset, type([])):
        if len(dataset) < 1:
            raise ValueError(f"(sum_by_month) `dataset` must have at least one item. Got: {dataset}")
        for datafile in dataset:
            if not isinstance(datafile, str):
                raise TypeError(f"(sum_by_month) Each item in `dataset` list must be a string. Got: {type(datafile)}")
            # Verify this is a valid path
            datafile = verify_path(datafile)
            if not datafile.endswith('.nc'):
                raise TypeError(f"(sum_by_month) `datafile` must be a `.nc` filepath. Got: {datafile}")
        # Load all the files at once
        if verbose:
            print(f"(sum_by_month) When passing a list of files, ensure their coordinates match as that is not verified in this function.")
        dataset = xr.open_mfdataset(dataset, data_vars='all')
    elif not isinstance(dataset, (xr.Dataset, xr.DataArray)):
        raise TypeError(f"(sum_by_month) `dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(dataset)}")
    if not isinstance(attr_long_name, (str, type(None))):
        raise TypeError(f"(sum_by_month) `attr_long_name` must be a string or `None`. Got type: {type(attr_long_name)}")
    if not isinstance(attr_units, (str, type(None))):
        raise TypeError(f"(sum_by_month) `attr_units` must be a string or `None`. Got type: {type(attr_units)}")
    if not isinstance(drop_bnds, bool):
        raise TypeError(f"(sum_by_month) `drop_bnds` must be a `bool`. Got type: {type(drop_bnds)}")
    if not isinstance(find_mean, bool):
        raise TypeError(f"(sum_by_month) `find_mean` must be a `bool`. Got type: {type(find_mean)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(sum_by_month) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.nc' in save_as:
        raise TypeError(f"(sum_by_month) `save_as` must be a `.nc` filepath. Got: {save_as}")
    
    # Information to output
    if verbose:
        print(f"(sum_by_month) `save_as`: {save_as}")
    
    if isinstance(dataset, xr.Dataset):
        # Get the `data_var` list
        data_var_list = list(dataset.data_vars)
        if verbose:
            print(f"(sum_by_month) `data_var_list`: {data_var_list}")

        # Remove meta variables having to do with time
        for meta_var in sps.meta_vars:
            if 'time' in meta_var or (drop_bnds and 'bnds' in meta_var):
                if meta_var in data_var_list:
                    if verbose:
                        print(f"(sum_by_month) Removing `meta_var`: {meta_var}")
                    dataset = dataset.drop_vars([meta_var])
        
        # Record the fact that `dataset` is an `xr.Dataset`
        dataset_is_Dataset = True
    else:
        dataset_is_Dataset = False

    if find_mean:
        # Take the mean of the dataset by month
        dataset = dataset.groupby('time.month').mean(dim='time', **kwargs)
        if verbose:
            print(f"(sum_by_month) Completed taking the mean by month.")
        # Set attribute variables
        mod_suffix = 'mean'
        units_suffix = ''
    else:
        # Sum the dataset by month
        ## Passing `min_count=1` prevents grid cells with all `nan` values across time from being set to zero instead of the expected `nan`
        ## Removing the `min_count` argument results in a spiky artifact on maps
        dataset = dataset.groupby('time.month').sum(dim='time', min_count=1, **kwargs)
        if verbose:
            print(f"(sum_by_month) Completed summing by month.")
        # Set attribute variables
        mod_suffix = 'sum'
        units_suffix = '/yr'

    if dataset_is_Dataset:
        # Get the name of the variable in the dataset
        var_name = get_variable_name(dataset)
        if not isinstance(var_name, str):
            raise ValueError(f"(sum_by_month) `dataset` must only have one variable. Available variables: {var_name}")
        # Rename the variable, giving it the suffix `_month_{mod_suffix}`
        dataset = dataset.rename_vars({var_name: f'{var_name}_month_{mod_suffix}'})
        # Get the reference to this variable
        xr_var_to_add_attrs = dataset[f'{var_name}_month_{mod_suffix}']
        # Add this operation to the history
        if 'history' in dataset.attrs.keys():
            original_history = dataset.attrs['history']
        else:
            original_history = ''
        dataset.attrs['history'] = f"{get_current_datetime_str()} altered by `arctichoke`: Calculated the {mod_suffix} of the `{var_name}` values per month in `{var_name}_month_{mod_suffix}`. {original_history}"
    else:
        # Get the name of the variable in the dataset
        var_name = dataset.name
        # Get the reference to this variable
        xr_var_to_add_attrs = dataset
    
    # Check whether this variable is in the sea ice vars dictionary
    if var_name in sps.sea_ice_vars.keys():
        # Check whether this is a marker variable or not
        if sps.sea_ice_vars[var_name]['marker_var']:
            if isinstance(attr_long_name, type(None)):
                attr_long_name = f"Annual {sps.sea_ice_vars[var_name]['label_name']} Months"
            if isinstance(attr_units, type(None)):
                if not find_mean:
                    attr_units = "months/yr"

    if verbose:
        print(f"(sum_by_month) Modifying the dataset attributes.")
    # Modify the attributes of the dataset to reflect the changes
    xr_var_to_add_attrs.attrs['standard_name'] = f'{var_name}_month_{mod_suffix}'
    if not isinstance(attr_long_name, type(None)):
        xr_var_to_add_attrs.attrs['long_name'] = attr_long_name
    elif 'long_name' in xr_var_to_add_attrs.attrs.keys():
        xr_var_to_add_attrs.attrs['long_name'] = f'Monthly {mod_suffix} of {xr_var_to_add_attrs.attrs['long_name']}'
    else:
        xr_var_to_add_attrs.attrs['long_name'] = f'Monthly {mod_suffix} of {var_name}'
    if not isinstance(attr_units, type(None)):
        xr_var_to_add_attrs.attrs['units'] = attr_units
    elif 'units' in xr_var_to_add_attrs.attrs.keys():
        xr_var_to_add_attrs.attrs['units'] = f'{xr_var_to_add_attrs.attrs['units']}{units_suffix}'
    else:
        xr_var_to_add_attrs.attrs['units'] = f'N/P'
    if 'comment' in xr_var_to_add_attrs.attrs.keys():
        xr_var_to_add_attrs.attrs['comment'] = f'Monthly {mod_suffix} of {xr_var_to_add_attrs.attrs['comment']}'
    else:
        xr_var_to_add_attrs.attrs['comment'] = f'N/P'
    xr_var_to_add_attrs.attrs['original_name'] = f'{var_name}_month_{mod_suffix}'
    if 'history' in xr_var_to_add_attrs.attrs.keys():
        original_history = xr_var_to_add_attrs.attrs['history']
    else:
        original_history = ''
    xr_var_to_add_attrs.attrs['history'] = f"{get_current_datetime_str()} altered by `arctichoke`: Calculated the {mod_suffix} of the `{var_name}` values to get `{var_name}_month_{mod_suffix}`. {original_history}"
    
    # Save the modified dataset, if applicable
    if not isinstance(save_as, type(None)):
        if verbose:
            print(f"(sum_by_month) Saving the dataset file: {save_as}")
        # Save the plot to file
        dataset.to_netcdf(save_as)
        if verbose:
            print(f"(sum_by_month) Done saving dataset file.")
    
    return dataset
