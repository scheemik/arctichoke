import numpy as np
import xarray as xr

from seaicecp.dataset.get_variable import get_variable_name
import seaicecp.params as sps
from seaicecp.verify import verify_path

def trend_in_time(
    dataset: (str, [str], xr.Dataset, xr.DataArray),
    var: str = None,
    time_dim: str = 'year',
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
        trends_dataset : `xarray.Dataset` or `xarray.DataArray`
            A dataset with the trends in time for the specified variable.
        
        Examples
        --------
        >>> from seaicecp.dataset.example_dataset import make_example_dataset
        from seaicecp.path.manipulate_paths import make_file_path
        # Create multiple example test files
        test_file_dir = 'tests/test_analysis/example_datasets'
        make_file_path(test_file_dir)
        test_file_names = [
            f"{test_file_dir}/example_dataset_0.nc",
            f"{test_file_dir}/example_dataset_1.nc",
            f"{test_file_dir}/example_dataset_2.nc",
        ]
        offsets = [0, 1, 3]
        for i in range(len(test_file_names)):
            make_example_dataset(
                n=3,
                offset=offsets[i],
                test_var_name='test_var',
                time_axis=(2000+i),
                save_as=test_file_names[i],
            )
        import xarray as xr
        test_dataset = xr.open_mfdataset(test_file_names)
        test_dataset['test_var'].values
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
        from seaicecp.analysis.trend_in_time import trend_in_time
        test_trends = trend_in_time(
            test_dataset,
            var='test_var',
            time_dim='time',
        )
        test_trends['test_var_trends'].values
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
    if not isinstance(time_dim, (str, type(None))):
        raise TypeError(f"(trend_in_time) `time_dim` must be a string or `None`. Got type: {type(time_dim)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(trend_in_time) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.nc' in save_as:
        raise TypeError(f"(trend_in_time) `save_as` must be a `.nc` filepath. Got: {save_as}")

    # Verify `dataset` has the specified variable
    if isinstance(dataset, xr.Dataset):
        actual_vars = get_variable_name(dataset)
        if var not in actual_vars:
            raise ValueError(f"(trend_in_time) `dataset` must have the specified `var` {var}. Available variables: {actual_vars}")
    
    # Information to output
    if verbose:
        print(f"(trend_in_time) `save_as`: {save_as}")

    # Get the time axis values
    time_axis_vals = dataset[time_dim].values
    if time_dim == 'time':
        # Define an epoch as January 1st, 1970
        epoch = np.datetime64('1970-01-01T00:00:00')
        # Convert datetimes to seconds from the epoch, then divide to get units of years
        time_axis_epoch_y = [((x - epoch) / np.timedelta64(1, 's')) / (60 * 60 * 24 * 365) for x in time_axis_vals]
    elif time_dim == 'year':
        time_axis_epoch_y = time_axis_vals
    else:
        raise ValueError(f"(trend_in_time) `time_dim` must be `time` or `year`. Got: {time_dim}")

    if isinstance(dataset, xr.Dataset):
        # Get a numpy array of the values for the given variable
        vals = dataset[var].values
        # Create a new dataset with just the 
        trends_dataset = dataset.isel({time_dim:0}, drop=True)
    else:
        # Get a numpy array of the values for the given variable
        vals = dataset.values
        # Create a new dataset with just the 
        trends_dataset = dataset.isel({time_dim:0}, drop=True)
    # Reshape to an array with as many rows as years and as many columns as there are pixels
    vals2 = vals.reshape(len(time_axis_epoch_y), -1)
    # Do a first-degree polyfit
    regressions = np.polyfit(time_axis_epoch_y, vals2, 1)
    # Get the coefficients back
    trends = regressions[0,:].reshape(vals.shape[1], vals.shape[2])
    if isinstance(dataset, xr.Dataset):
        # Rename the variable, giving it the suffix `_trends`
        trends_dataset = trends_dataset.rename_vars({var: f'{var}_trends'})
        # Put the trends data into the dataset
        trends_dataset[f'{var}_trends'].values = trends
    else:
        trends_dataset.values = trends

    # Save the modified dataset, if applicable
    if not isinstance(save_as, type(None)):
        # Save the plot to file
        trends_dataset.to_netcdf(save_as)
    
    return trends_dataset
