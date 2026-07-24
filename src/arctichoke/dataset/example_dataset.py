import xarray as xr
import numpy as np

from arctichoke.verify import verify_path

def make_example_dataset(
    save_as: str = None,
    n: int = 10,
    offset: (int, float) = 0, 
    test_var_name: str = 'test_var',
    time_dim: str = None,
    time_len: int = 1,
    start_year: int = 2026,
    overwrite: bool = True,
):
    """ Create an example dataset for testing.

        Construct a dataset such that it is minimal in size yet contains all notable features of the datasets of HighResMIP data, and save it to a netCDF file.

        Parameters
        ----------
        save_as : `str`, `None`, optional
            The absolute file path to which to save the example dataset.
            Default is `None`, which doesn't save the dataset to a file.
        n : `int`, optional
            The number of values in each dimension.
            Default is `10`.
        offset : `int`, `float`, optional
            A constant offset value to add to every value in the dataset.
            Default is `0`. 
        test_var_name : `str`, optional
            The name to give the test variable.
            Default is `test_var`.
        time_dim : `str`, `None`, optional
            The name of the time dimension to use.
            If `None` is given, no time dimension is added.
            Default is `None`.
        time_len : `int`, optional
            The length to make the time dimension.
            This argument has no effect if `time_dim` is `None`.
            Default is `1`.
        overwrite : `bool`, optional
            Whether to overwrite an existing file at the given filepath in `save_as`.
            Default is `True`.

        Returns
        -------
        example_dataset : `xr.Dataset`
            A list, sorted alphabetically, of the names of the available models.
        
        Examples
        --------
        >>> from arctichoke.dataset.example_dataset import make_example_dataset
        >>> dataset = make_example_dataset(n=3, time_dim='year')
        >>> dataset['test_var'].values
        array([[[0., 1., 2.],
                [3., 4., 5.],
                [6., 7., 8.]],

               [[0., 1., 2.],
                [3., 4., 5.],
                [6., 7., 8.]]])
    """
    # Verify input arguments
    if isinstance(save_as, str):
        if not save_as.endswith('.nc'):
            raise ValueError(f"(plot_time_series) `save_as` must be a `.nc` save_as. Got: {save_as}")
    elif not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(make_example_dataset) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    if not isinstance(n, int):
        raise TypeError(f"(make_example_dataset) `n` must be an integer. Got type: {type(n)}")
    if not isinstance(offset, (int, float)):
        raise TypeError(f"(make_example_dataset) `offset` must be an integer or float. Got type: {type(offset)}")
    if not isinstance(test_var_name, str):
        raise TypeError(f"(make_example_dataset) `test_var_name` must be a string. Got type: {type(test_var_name)}")
    if not isinstance(time_dim, (str, type(None))):
        raise TypeError(f"(make_example_dataset) `time_dim` must be a string or `None`. Got type: {type(time_dim)}")
    if not isinstance(time_len, int):
        raise TypeError(f"(make_example_dataset) `time_len` must be an integer. Got type: {type(time_len)}")
    if time_len < 1:
        raise ValueError(f"(make_example_dataset) `time_len` must be 1 or greater. Got: {time_len}")
    if not isinstance(start_year, int):
        raise TypeError(f"(make_example_dataset) `start_year` must be an integer. Got type: {type(start_year)}")
    if not isinstance(overwrite, bool):
        raise TypeError(f"(make_example_dataset) `overwrite` must be `bool`. Got type: {type(overwrite)}")

    # Initialize the dataset
    xr_dataset = xr.Dataset()
    
    # Add dimensions
    j_arr = np.arange(n, dtype=np.float64)
    xr_dataset['j'] = ('j',j_arr)
    i_arr = np.arange(n+1,2*n+1, dtype=np.float64)
    xr_dataset['i'] = ('i',i_arr)

    # Assign longitude and latitude coordinates
    lon_arr = np.reshape([np.arange(2*n+1,3*n+1, dtype=np.float64)]*n, (n,n))
    lat_arr = np.reshape([np.arange(3*n+1,4*n+1, dtype=np.float64)]*n, (n,n)).T
    xr_dataset = xr_dataset.assign_coords(
        {
            'longitude': (['j','i'], lon_arr),
            'latitude': (['j','i'], lat_arr),
        }
    )

    # Add a test variable
    test_var = np.reshape(np.arange(offset, n*n+offset, dtype=np.float64), (n,n))
    xr_dataset[test_var_name] = (['j','i'],test_var)

    # Add time dimension, if applicable
    if not isinstance(time_dim, type(None)):
        if time_dim == 'year':
            # Create an array of integers, one per year
            time_arr = np.arange(start_year, start_year+time_len)
        elif time_dim == 'time':
            # Get the start and end dates
            start_date = np.datetime64(f'{start_year}-01', 'M')
            end_date = start_date + np.timedelta64(time_len, 'M')
            # Create an array of dates, one per month ('M')
            time_arr = np.arange(start_date, end_date, dtype='datetime64[M]')
            # Set the date format to `[ns]`
            time_arr = time_arr.astype('datetime64[ns]')
            # Add 15 days to each date to match monthly average datetimes
            time_arr += np.timedelta64(15, 'D')
        else:
            raise NotImplementedError(f"(make_example_dataset) `time_dim={time_dim}` not yet implemented. Current `time_dim` options: `year`, `time`")
        # Expand the dimensions to include time
        xr_dataset = xr_dataset.expand_dims(dim={time_dim: time_arr}, axis=0)

    if not isinstance(save_as, type(None)):
        # Check whether the file exists
        try:
            verify_path(save_as)
            if overwrite == False:
                raise FileExistsError(f"(trim_files) file `{save_as}` exists already. To overwrite this file, set `overwrite` to `True`.")
            else:
                print(f"\tOverwriting file `{save_as}`.")
        except (FileNotFoundError):
            foo = 2

        # Save this dataset to a file
        xr_dataset.to_netcdf(save_as)

        # Verify that file was save correctly
        save_as = verify_path(save_as)

    return xr_dataset