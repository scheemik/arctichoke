import cftime
import numpy as np
import xarray as xr

from arctichoke.verify import verify_path

def get_date_type(
    dataset: (str, xr.DataArray, xr.Dataset),
):
    """ Get the data type of the dates of a dataset.

        Determine the data type of the dates, the `time` dimension, of the given dataset, if applicable.

        Parameters
        ----------
        dataset : `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset for which to get the date type.

        Returns
        -------
        date_dtype : `str`
            The data type of the dates in the dataset as a string.

        Examples
        --------
        >>> from arctichoke.dataset import make_example_dataset
        >>> ex_xr = make_example_dataset(time_axis = True)
        >>> from arctichoke.dataset import get_date_type
        >>> get_date_type(ex_xr)
        'datetime64[ns]'
    """
    # Verify input arguments
    if not isinstance(dataset, (str, xr.Dataset, xr.DataArray)):
        raise TypeError(f"(get_date_type) `dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(dataset)}")
    if isinstance(dataset, str):
        # Verify this is a valid path
        dataset = verify_path(dataset)
        if not dataset.endswith('.nc'):
            raise TypeError(f"(get_date_type) `dataset` must be a `.nc` filepath. Got: {dataset}")
        # Open the dataset
        dataset = xr.open_dataset(dataset)

    # Get the names of the dimensions of the dataset
    ## Note: Use `.sizes` instead of `.dims` for consistency across Datasets and DataArrays
    dims = list(dataset.sizes.keys())
    # Verify that the dataset has a `time` dimension
    if not 'time' in dims:
        raise ValueError(f"(get_date_type) `dataset` must have a `'time'` dimension. Got dimensions: {dims}")
    
    # Determine the data type of the `time` dimension
    date_dtype = str(dataset['time'].dtype)
    if date_dtype == 'datetime64[ns]':
        return date_dtype
    elif date_dtype == 'object':
        # Check whether the time axis is `cftime.Datetime360Day`
        if isinstance(dataset['time'].values[0], cftime.Datetime360Day):
            date_dtype = 'cftime.Datetime360Day'
        else:
            raise ValueError(f"(get_date_type) Got `{date_dtype}` for `str(dataset['time'].dtype)`, but data type is not `cftime.Datetime360Day`.")
        return date_dtype
    else:
        raise ValueError(f"(get_date_type) `dataset` has unrecognized dtype for the `time` axis: {date_dtype}")

def get_epoch_times(
    dataset: (str, xr.DataArray, xr.Dataset),
    time_dim: str = 'time',
):
    """ Get the epoch times of the times in a dataset.

        Calculate the epoch time in years from Jaunary 1st, 1970 for the datetimes in the dataset.

        Parameters
        ----------
        dataset : `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset for which to get the date type.
        time_dim : `str`, optional
            The name of the time dimension for which to find the epoch times.
            Default is `time`. 

        Returns
        -------
        epoch_times : List of `float`
            The epoch times in years from Jaunary 1st, 1970 for the datetimes in the dataset.

        Examples
        --------
        >>> from arctichoke.dataset import make_example_dataset
        >>> ex_xr = make_example_dataset(time_axis = True)
        >>> from arctichoke.dataset import get_epoch_times
        >>> get_date_type(get_epoch_times)
        [np.float64(56.07945205479452), np.float64(56.16438356164384)]
    """
    # Verify input arguments
    if not isinstance(dataset, (str, xr.Dataset, xr.DataArray)):
        raise TypeError(f"(get_epoch_times) `dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(dataset)}")
    if isinstance(dataset, str):
        # Verify this is a valid path
        dataset = verify_path(dataset)
        if not dataset.endswith('.nc'):
            raise TypeError(f"(get_epoch_times) `dataset` must be a `.nc` filepath. Got: {dataset}")
        # Open the dataset
        dataset = xr.open_dataset(dataset)
    if not isinstance(time_dim, str):
        raise TypeError(f"(trend_in_time) `time_dim` must be a string. Got type: {type(time_dim)}")

    # Get the names of the dimensions of the dataset
    ## Note: Use `.sizes` instead of `.dims` for consistency across Datasets and DataArrays
    dims = list(dataset.sizes.keys())
    # Verify that the dataset has a `time` dimension
    if not time_dim in dims:
        raise ValueError(f"(get_epoch_times) `dataset` must have a `'{time_dim}'` dimension. Got dimensions: {dims}")
    
    # Get the values of the time dimension
    time_dim_vals = dataset[time_dim].values
    if time_dim == 'time':
        # Determine the data type of the `time` dimension
        date_dtype = get_date_type(dataset)
        # Check whether the data type is `np.datetime64[ns]`
        if date_dtype == 'datetime64[ns]':
            # Calculate the correction factor to convert nanoseconds to years
            correction_factor = 60 * 60 * 24 * 365 # * 1e9
            # Define an epoch as January 1st, 1970
            epoch = np.datetime64('1970-01-01T00:00:00')
        elif date_dtype == 'cftime.Datetime360Day':
            # Calculate the correction factor to convert seconds to years
            correction_factor = 60 * 60 * 24 * 365
            # Define an epoch as January 1st, 1970
            epoch = cftime.Datetime360Day(1970, 1, 1, 0, 0, 0, 0, has_year_zero=True)
        else:
            raise TypeError(f"(get_epoch_times) Correction factor not yet set for time dimension type: {date_dtype}")
        # Convert datetimes to seconds from the epoch, then divide to get units of years
        epoch_times = [((x - epoch) / np.timedelta64(1, 's')) / correction_factor for x in time_dim_vals]
    elif time_dim == 'year':
        date_dtype = int
        # Calculate the epoch times
        epoch_times = time_dim_vals - 1970
    else:
        raise ValueError(f"(get_epoch_times) `time_dim` must be `time` or `year`. Got: {time_dim}")

    return epoch_times