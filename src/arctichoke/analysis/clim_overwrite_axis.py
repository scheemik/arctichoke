import xarray as xr 

def overwrite_month_with_time(
    dataset_clim: xr.Dataset,
    dataset_regular: xr.Dataset,
    dataset_w_clim_attrs: (str, xr.Dataset) = None,
    verbose: bool = False,
):
    """ Overwrites the `month` axis with a `time` axis.

        Given a climatology dataset with `month` as its time axis and a corresponding regular file with a `time` axis, copy the `time` axis values from the regular file to overwrite the values in the `month` axis in the climatology dataset, then rename the `month` axis to `time`.
        This allows these two files to then be interoperable.  

        Parameters
        ----------
        dataset_clim : `xarray.Dataset`
            The climatology dataset in which to overwrite the `month` axis.
        dataset_regular : `xarray.Dataset`
            The regular dataset from which to use the `time` axis for the overwrite.
        dataset_w_clim_attrs : `xarray.Dataset`, optional
            The dataset from which to use the `climatology_start` and `climatology_end` attributes if `dataset_clim` does not contain them.
            If neither `dataset_clim` nor `dataset_w_clim_attrs` contain the `climatology_start` and `climatology_end` attributes, none are written to `dataset_regular`. 
            Default is `None`.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `list_variable_files()`.

        Returns
        -------
        dataset_clim : `xarray.Dataset`
            The climatology dataset with the `month` axis replaced with `time`.
        dataset_regular : `xarray.Dataset`
            The regular dataset, possibly with the `climatology_start` and `climatology_end` attributes added.
        
        Examples
        --------
        >>> from arctichoke.analysis import overwrite_month_with_time
    """
    # Verify input arguments
    if not isinstance(dataset_clim, xr.Dataset):
        raise TypeError(f"(make_climatology) `dataset_clim` must be a `xr.Dataset`. Got type: {type(dataset_clim)}")
    if not isinstance(dataset_regular, xr.Dataset):
        raise TypeError(f"(make_climatology) `dataset_regular` must be a `xr.Dataset`. Got type: {type(dataset_regular)}")
    if not isinstance(dataset_w_clim_attrs, (str, xr.Dataset)):
        raise TypeError(f"(make_climatology) `dataset_w_clim_attrs` must be a string or `xr.Dataset`. Got type: {type(dataset_w_clim_attrs)}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(make_climatology) `verbose` must be a `bool`. Got type: {type(verbose)}")

    # Overwrite the `month` axis in the `dataset_clim` with the `time` axis from the `dataset_regular`
    dataset_clim = dataset_clim.rename_dims({'month': 'time'})
    dataset_clim = dataset_clim.assign_coords({'time': (['time'], dataset_regular['time'].values)})
    dataset_clim = dataset_clim.drop_vars('month')

    # Decide where to pull climatology attributes from
    if isinstance(dataset_w_clim_attrs, type(None)):
        dataset_w_clim_attrs = dataset_clim
    elif isinstance(dataset_w_clim_attrs, str):
        if verbose:
            print(f"(overwrite_month_with_time) Using `dataset_w_clim_attrs` for climatology attributes.")
        dataset_w_clim_attrs = xr.open_dataset(dataset_w_clim_attrs)
    # Copy over the climatology attributes
    for clim_attr in ['climatology_start', 'climatology_end']:
        if clim_attr in dataset_w_clim_attrs.attrs.keys():
            if verbose:
                print(f"(overwrite_month_with_time) Writing attribute `{clim_attr}`.")
            dataset_regular.attrs[clim_attr] = dataset_w_clim_attrs.attrs[clim_attr]

    return dataset_clim, dataset_regular