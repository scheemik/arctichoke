import xarray as xr

from arctichoke import get_current_datetime_str
from arctichoke.verify import verify_path

def select_months(
    dataset: (str, [str], xr.Dataset, xr.DataArray),
    months: [int] = [6,7,8,9,10],
    verbose: bool = False,
):
    """ Select only the given months of the year from the dataset.

        Across all years of the given dataset, select the given months and return a new dataset with only those months present. 

        Parameters
        ----------
        dataset : `str`, list of `str`, `xarray.Dataset`, `xarray.DataArray`
            The dataset for which to select months.
        months: list of `int`, optional
            The months of the year to select where 1 = January, 2 = February, etc.
            Default is `[6,7,8,9,10]`.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.

        Returns
        -------
        dataset : `xarray.DataArray`, `xarray.Dataset`
            The dataset with the date data type converted, if necessary.

        Examples
        --------
        >>> from arctichoke.dataset import make_example_dataset
        >>> ex_xr = make_example_dataset(n = 2, time_dim = 'time', time_len = 36, start_year = 2026)
        >>> from arctichoke.dataset import select_months
        >>> ex_xr_sel = select_months(ex_xr)
        >>> ex_xr_sel['time'].size
        15
        >>> ex_xr_sel.attrs['select_months']
        '[6, 7, 8, 9, 10]'
    """
    # Verify input arguments
    if not isinstance(verbose, bool):
        raise TypeError(f"(select_months) `verbose` must be a `bool`. Got type: {type(verbose)}")
    if isinstance(dataset, str):
        # Wrap that string into a list
        dataset = [dataset]
    if isinstance(dataset, type([])):
        if len(dataset) < 1:
            raise ValueError(f"(select_months) `dataset` must have at least one item. Got: {dataset}")
        for datafile in dataset:
            if not isinstance(datafile, str):
                raise TypeError(f"(select_months) Each item in `dataset` list must be a string. Got: {type(datafile)}")
            # Verify this is a valid path
            datafile = verify_path(datafile)
            if not datafile.endswith('.nc'):
                raise TypeError(f"(select_months) `datafile` must be a `.nc` filepath. Got: {datafile}")
        # Load all the files at once
        if verbose:
            print(f"(select_months) When passing a list of files, ensure their coordinates match as that is not verified in this function.")
        dataset = xr.open_mfdataset(dataset)
    elif not isinstance(dataset, (xr.Dataset, xr.DataArray)):
        raise TypeError(f"(select_months) `dataset` must be a string, `xr.Dataset`, or `xarray.DataArray`. Got type: {type(dataset)}")
    if isinstance(months, int):
        months = [months]
    if isinstance(months, type([])):
        if len(months) < 1:
            raise ValueError(f"(select_months) `months` must have at least one entry. Got: {months}")
        for month in months:
            if not isinstance(month, int):
                raise TypeError(f"(select_months) `months` values must be integers. For month `{month}` got type: {type(month)}")
            if month < 1 or month > 12:
                raise ValueError(f"(select_months) `months` values must be 1 to 12. Got month: {month}")
    else:
        raise TypeError(f"(select_months) `months` must be a list. Got type: {type(months)}")
    
    # Ensure `dataset` has a `time` dimension
    if 'time' not in list(dataset.dims):
        raise ValueError(f"(select_months) `dataset` must have a `time` dimension. Available dimensions: {list(dataset.dims)}")
    
    if verbose: 
        print(f"(select_months) Selecting months: {months}")
    
    # Select just the given months
    dataset = dataset.sel(time=dataset.time.dt.month.isin(months))
    # Modify attributes to mark this change
    if 'history' in dataset.attrs.keys():
        original_history = dataset.attrs['history']
    else:
        original_history = ''
    dataset.attrs['history'] = f"{get_current_datetime_str()} altered by `arctichoke`: Kept only the months: {months}. {original_history}"
    dataset.attrs['select_months'] = f"{months}"

    return dataset