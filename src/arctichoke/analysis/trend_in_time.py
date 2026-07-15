import numpy as np
import xarray as xr

from arctichoke import get_current_datetime_str
from arctichoke.dataset import get_variable_name, get_min_max, get_epoch_times, get_date_type
import arctichoke.params as sps
from arctichoke.verify import verify_path

def trend_in_time(
    dataset: (str, [str], xr.Dataset, xr.DataArray),
    var: str = None,
    time_dim: str = 'year',
    mask_where_zero_across_time: bool = False,
    use_xarray_polyfit: bool = True,
    save_as: str = None,
    verbose: bool = False,
    **kwargs,
):
    """ Find the trend for each grid cell along the time axis.

        For each grid cell in the dataset, find the trend in time for the given variable. 
        This results in a new dataset without a `time` dimension. 

        Parameters
        ----------
        dataset : `str`, list of `str`, `xarray.Dataset`, `xarray.DataArray`
            The dataset of which to find the sum across time.
        var : `str`, `None`, optional
            The variable in `dataset` for which to take the trend across time.
            This is required if `dataset` is an `xarray.Dataset`. 
            Default is `None`.
        time_dim : `str`, optional
            The name of the time dimension over which to find the trend.
            Default is `year`. 
        mask_where_zero_across_time : `bool`, optional
            Whether to mask out grid cells which have zero as a value across the entire time dimension using `mask_where_all_zero()`.
            Default is `False`. 
        use_xarray_polyfit : `bool`, optional
            If `True`, use `xarray.polyfit()` to take trends in time, which skips `nan` values. 
            If `False`, use `numpy.polyfit()` to take trends in time, which has `nan` values invalidate an index of the array across all time.
            Default is `True`.
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
            A dataset with the trends in time for the specified variable.
        
        Examples
        --------
        >>> from arctichoke.dataset.example_dataset import make_example_dataset
        >>> from arctichoke.path.manipulate_paths import make_file_path
        >>> # Create multiple example test files
        >>> test_file_dir = 'tests/test_analysis/example_datasets'
        >>> make_file_path(test_file_dir)
        >>> test_file_names = [
        >>>     f"{test_file_dir}/example_dataset_0.nc",
        >>>     f"{test_file_dir}/example_dataset_1.nc",
        >>>     f"{test_file_dir}/example_dataset_2.nc",
        >>> ]
        >>> offsets = [0, 1, 3]
        >>> for i in range(len(test_file_names)):
        >>>     make_example_dataset(
        >>>         n=3,
        >>>         offset=offsets[i],
        >>>         test_var_name='test_var',
        >>>         time_axis=(2000+i),
        >>>         save_as=test_file_names[i],
        >>>     )
        >>> import xarray as xr
        >>> test_dataset = xr.open_mfdataset(test_file_names)
        >>> test_dataset['test_var'].values
        array([[[ 0.,  1.,  2.],
                [ 3.,  4.,  5.],
                [ 6.,  7.,  8.]],
               [[ 0.,  1.,  2.],
                [ 3.,  4.,  5.],
                [ 6.,  7.,  8.]],
               [[ 1.,  2.,  3.],
                [ 4.,  5.,  6.],
                [ 7.,  8.,  9.]],
               [[ 1.,  2.,  3.],
                [ 4.,  5.,  6.],
                [ 7.,  8.,  9.]],
               [[ 3.,  4.,  5.],
                [ 6.,  7.,  8.],
                [ 9., 10., 11.]],
               [[ 3.,  4.,  5.],
                [ 6.,  7.,  8.],
                [ 9., 10., 11.]]])
        >>> from arctichoke.analysis.trend_in_time import trend_in_time
        >>> test_trends = trend_in_time(
        >>>     test_dataset,
        >>>     var='test_var',
        >>>     time_dim='time',
        >>> )
        >>> test_trends['test_var_trends'].values
        array([[1.49369, 1.49369, 1.49369],
               [1.49369, 1.49369, 1.49369],
               [1.49369, 1.49369, 1.49369]])
    """
    # Verify input arguments
    if not isinstance(verbose, bool):
        raise TypeError(f"(trend_in_time) `verbose` must be a `bool`. Got type: {type(verbose)}")
    if isinstance(dataset, str):
        # Wrap that string into a list
        dataset = [dataset]
    if isinstance(dataset, type([])):
        if len(dataset) < 1:
            raise ValueError(f"(trend_in_time) `dataset` must have at least one item. Got: {dataset}")
        for datafile in dataset:
            if not isinstance(datafile, str):
                raise TypeError(f"(trend_in_time) Each item in `dataset` list must be a string. Got: {type(datafile)}")
            # Verify this is a valid path
            datafile = verify_path(datafile)
            if not datafile.endswith('.nc'):
                raise TypeError(f"(plot_time_series) `datafile` must be a `.nc` filepath. Got: {datafile}")
        # Load all the files at once
        if verbose:
            print(f"(trend_in_time) When passing a list of files, ensure their coordinates match as that is not verified in this function.")
        dataset = xr.open_mfdataset(dataset)
    elif not isinstance(dataset, (xr.Dataset, xr.DataArray)):
        raise TypeError(f"(trend_in_time) `dataset` must be a string, `xr.Dataset`, or `xarray.DataArray`. Got type: {type(dataset)}")
    if not isinstance(var, (str, type(None))):
        raise TypeError(f"(trend_in_time) `var` must be a string or `None`. Got type: {type(var)}")
    if not isinstance(time_dim, str):
        raise TypeError(f"(trend_in_time) `time_dim` must be a string. Got type: {type(time_dim)}")
    if not isinstance(mask_where_zero_across_time, bool):
        raise TypeError(f"(trend_in_time) `mask_where_zero_across_time` must be a `bool`. Got type: {type(mask_where_zero_across_time)}")
    if not isinstance(use_xarray_polyfit, bool):
        raise TypeError(f"(trend_in_time) `use_xarray_polyfit` must be a `bool`. Got type: {type(use_xarray_polyfit)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(trend_in_time) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.nc' in save_as:
        raise TypeError(f"(trend_in_time) `save_as` must be a `.nc` filepath. Got: {save_as}")

    # Verify `dataset` has the specified variable
    if isinstance(dataset, xr.Dataset):
        actual_vars = get_variable_name(dataset)
        if var not in actual_vars:
            raise ValueError(f"(trend_in_time) `dataset` must have the specified `var` {var}. Available variables: {actual_vars}")
    else:
        # Get the name of the variable
        var = dataset.name
        # Convert `dataset` from `xr.DataArray` to `xr.Dataset`
        dataset = dataset.to_dataset()
    
    # Information to output
    if verbose:
        print(f"(trend_in_time) `save_as`: {save_as}")
    
    # Mask grid cells which have values of zero over all time
    if mask_where_zero_across_time:
        dataset = mask_where_all_zero(
            dataset,
            var,
            time_dim,
            verbose,
        )

    # Set the appropriate correction factor for the type of time axis
    if time_dim == 'time':
        # Determine the data type of the `time` dimension
        date_dtype = get_date_type(dataset)
        # Check whether the data type is `np.datetime64[ns]`
        if date_dtype == 'datetime64[ns]':
            # Calculate the correction factor to convert nanoseconds to years
            correction_factor = 60 * 60 * 24 * 365 * 1e9
        elif date_dtype == 'cftime.Datetime360Day':
            # Calculate the correction factor to convert seconds to years
            correction_factor = 60 * 60 * 24 * 365
        else:
            raise TypeError(f"(trend_in_time) Correction factor not yet set for time dimension type: {date_dtype}")
        if verbose:
            print(f"(trend_in_time) `dataset` has date type: {date_dtype}")
    elif time_dim == 'year':
        correction_factor = 1
    else:
        raise TypeError(f"(trend_in_time) Correction factor not yet set for `time_dim`: {time_dim}")

    # Store the variable attributes to put back later
    var_attrs = dataset[var].attrs
    
    # Get the trends in time
    if use_xarray_polyfit:
        ## Note: When using `polyfit()`, a dimenson `degree` gets added
        ## The index 0 of `degree` corresponds to the slope when using a 1st-order fit
        if verbose:
            print(f"(trend_in_time) Getting a first-degree polyfit")
        polyfit = (dataset[var].polyfit(time_dim, 1, skipna=True, full=True).isel(degree=0, drop=True) * correction_factor)
        if verbose:
        trends = polyfit['polyfit_coefficients']
    else:
        # Get the time axis values
        time_axis_epoch_y = get_epoch_times(
            dataset,
            time_dim,
        )
        if verbose:
            print(f"(trend_in_time) Getting a numpy array of the values for the given variable")
        # Get a numpy array of the values for the given variable
        vals = dataset[var].values
        if verbose:
            print(f"(trend_in_time) Reshaping array")
        # Reshape to an array with as many rows as years and as many columns as there are pixels
        vals2 = vals.reshape(len(time_axis_epoch_y), -1)
        if verbose:
            print(f"(trend_in_time) Getting a first-degree polyfit")
        # Do a first-degree polyfit
        polyfit = np.polyfit(time_axis_epoch_y, vals2, 1)
        if verbose:
            print(f"(trend_in_time) Get the coefficients")
        trends = polyfit[0,:].reshape(vals.shape[1], vals.shape[2])
    
    # Set `dataset` to be just the first time slice
    dataset = dataset.isel({time_dim:0}, drop=True)

    # Rename the variable, giving it the suffix `_trends`
    dataset = dataset.rename_vars({var: f'{var}_trends'})
    # Put the trends into the original dataset
    if use_xarray_polyfit:
        dataset[f'{var}_trends'] = trends
    else:
        dataset[f'{var}_trends'].values = trends
    # Restore the variable attributes
    dataset[f'{var}_trends'].attrs = var_attrs
    # Add this operation to the history
    if 'history' in dataset.attrs.keys():
        original_history = dataset.attrs['history']
    else:
        original_history = ''
    dataset.attrs['history'] = f"{get_current_datetime_str()} altered by `arctichoke`: Calculated trends across `{time_dim}` of `{var}` values to get `{var}_trends`. {original_history}"
    # Get the reference to this variable
    xr_var_to_add_attrs = dataset[f'{var}_trends']
        
    if verbose:
        print(f"(trend_in_time) Modifing dataset attributes")
    # Modify the attributes of the dataset to reflect the changes
    xr_var_to_add_attrs.attrs['standard_name'] = f'{var}_trends'
    if 'long_name' in xr_var_to_add_attrs.attrs.keys():
        xr_var_to_add_attrs.attrs['long_name'] = f'Trend in {xr_var_to_add_attrs.attrs['long_name']}'
    else:
        xr_var_to_add_attrs.attrs['long_name'] = f'Trend in {var}'
    if 'units' in xr_var_to_add_attrs.attrs.keys():
        xr_var_to_add_attrs.attrs['units'] = f'{xr_var_to_add_attrs.attrs['units']}/yr'
    else:
        xr_var_to_add_attrs.attrs['units'] = f'N/P'
    if 'comment' in xr_var_to_add_attrs.attrs.keys():
        xr_var_to_add_attrs.attrs['comment'] = f'Trend in {xr_var_to_add_attrs.attrs['comment']}'
    else:
        xr_var_to_add_attrs.attrs['comment'] = f'N/P'
    xr_var_to_add_attrs.attrs['original_name'] = f'{var}_trends'
    if 'history' in xr_var_to_add_attrs.attrs.keys():
        original_history = xr_var_to_add_attrs.attrs['history']
    else:
        original_history = ''
    xr_var_to_add_attrs.attrs['history'] = f"{get_current_datetime_str()} altered by `arctichoke`: Calculated trends across `{time_dim}` of `{var}` values to get `{var}_trends`. {original_history}"

    # Save the modified dataset, if applicable
    if not isinstance(save_as, type(None)):
        # Save the plot to file
        dataset.to_netcdf(save_as)
    
    return dataset

def mask_where_all_zero(
    dataset: (str, [str], xr.Dataset, xr.DataArray),
    var: str = None,
    time_dim: str = 'year',
    verbose: bool = False,
):
    """ Masks out grid cells which are zero across time.

        For each grid cell in the dataset, if that grid cell is equal to zero across the entire time dimension, set those values to `nan`.
        This will allow masking out grid cells which have no trend in time not because the values don't change, but because they are missing data. 
        Note, this is done by summing across time to find which cells have a sum of zero, so this should not be used for any variable which could have negative values. 

        Parameters
        ----------
        dataset : `str`, list of `str`, `xarray.Dataset`, `xarray.DataArray`
            The dataset of which to mask zeros across time.
        var : `str`, `None`, optional
            The variable in `dataset` for which to mask zeros across time.
            This is required if `dataset` is an `xarray.Dataset`. 
            Default is `None`.
        time_dim : `str`, optional
            The name of the time dimension over which to find zeros.
            Default is `year`. 
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.

        Returns
        -------
        trends_dataset : `xarray.Dataset` or `xarray.DataArray`
            A dataset with the trends in time for the specified variable.
        
        Examples
        --------
        >>> import xarray as xr
        >>> xr_ds = xr.Dataset({
        >>>     'test_var': (
        >>>         ['t', 'i', 'j'], 
        >>>         [[[ 0,  0,  0],
        >>>         [ 1,  1,  1],
        >>>         [ 0,  0,  0]],
        >>>         [[ 0,  1,  1],
        >>>         [ 1,  0,  0],
        >>>         [ 0,  0,  0]]]
        >>>     )
        >>> })
        >>> xr_ds['test_var'].values
        array([[[0, 0, 0],
                [1, 1, 1],
                [0, 0, 0]],

               [[0, 1, 1],
                [1, 0, 0],
                [0, 0, 0]]])
        >>> from arctichoke.analysis.trend_in_time import mask_where_all_zero
        >>> xr_ds_nan = mask_where_all_zero(
        >>>     xr_ds,
        >>>     'test_var',
        >>>     time_dim = 't'
        >>> )
        >>> xr_ds_nan['test_var'].values
        array([[[nan,  0.,  0.],
                [ 1.,  1.,  1.],
                [nan, nan, nan]],

               [[nan,  1.,  1.],
                [ 1.,  0.,  0.],
                [nan, nan, nan]]])
    """
    # Verify input arguments
    if not isinstance(verbose, bool):
        raise TypeError(f"(mask_where_all_zero) `verbose` must be a `bool`. Got type: {type(verbose)}")
    if isinstance(dataset, str):
        # Wrap that string into a list
        dataset = [dataset]
    if isinstance(dataset, type([])):
        if len(dataset) < 1:
            raise ValueError(f"(mask_where_all_zero) `dataset` must have at least one item. Got: {dataset}")
        for datafile in dataset:
            if not isinstance(datafile, str):
                raise TypeError(f"(mask_where_all_zero) Each item in `dataset` list must be a string. Got: {type(datafile)}")
            # Verify this is a valid path
            datafile = verify_path(datafile)
            if not datafile.endswith('.nc'):
                raise TypeError(f"(plot_time_series) `datafile` must be a `.nc` filepath. Got: {datafile}")
        # Load all the files at once
        if verbose:
            print(f"(mask_where_all_zero) When passing a list of files, ensure their coordinates match as that is not verified in this function.")
        dataset = xr.open_mfdataset(dataset)
    elif not isinstance(dataset, (xr.Dataset, xr.DataArray)):
        raise TypeError(f"(mask_where_all_zero) `dataset` must be a string, `xr.Dataset`, or `xarray.DataArray`. Got type: {type(dataset)}")
    if not isinstance(var, (str, type(None))):
        raise TypeError(f"(mask_where_all_zero) `var` must be a string or `None`. Got type: {type(var)}")
    if not isinstance(time_dim, str):
        raise TypeError(f"(mask_where_all_zero) `time_dim` must be a string. Got type: {type(time_dim)}")

    # Verify `dataset` has the specified variable
    if isinstance(dataset, xr.Dataset):
        actual_vars = get_variable_name(dataset)
        if var not in actual_vars:
            raise ValueError(f"(mask_where_all_zero) `dataset` must have the specified `var` {var}. Available variables: {actual_vars}")

    # Sum the dataset across the time dimension
    dataset_time_sum = dataset.sum(dim=time_dim)
    # Check to see whether any values are negative
    vmin, vmax = get_min_max(
        dataset_time_sum.compute(),
        var,
    )
    if vmin < 0:
        raise ValueError(f"(mask_where_all_zero) The chosen `var` ({var}) in `dataset` must not have negative values. Found a minimum value of the sum across time of: {vmin}")

    if isinstance(dataset, xr.Dataset):
        # Point to the specific variable
        data_to_replace = dataset[var]
    else:
        # Point to the whole data array
        data_to_replace = dataset

    if verbose:
        print(f"(mask_where_all_zero) Masking cells which have zeros across all time.")
    # Replace values in grid cells that have zeros for all time with `np.nan`
    dataset_w_nan = dataset.where(
        lambda val:
            dataset_time_sum != 0,
        lambda val:
            np.nan
    )
    
    return dataset_w_nan
