import cftime
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
        >>> from arctichoke.verify.get_date_type import get_date_type
        >>> get_date_type()
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
