import xarray as xr

from seaicecp.verify.verify_path import verify_path

def make_title(
    dataset: (str, [str], xr.Dataset),
    add_source_id: bool = True,
    add_experiment_id: bool = True,
    add_variant_label: bool = True,
    add_time_stamp: bool = True,
):
    """ Create a title for the dataset for use in plots.

        Assemble a title to be used in plots for this dataset based on the specified attributes.

        Parameters
        ----------
        dataset : `str`, list of `str`, `xarray.Dataset`
            The dataset for which to make a title.
        add_source_id : `bool`, optional
            Whether to add the source ID to the title.
            Default is `True`.
        add_experiment_id : `bool`, optional
            Whether to add the eperiment ID to the title.
            Default is `True`.
        add_variant_label : `bool`, optional
            Whether to add the variant label to the title.
            Default is `True`.
        add_time_stamp : `bool`, optional
            Whether to add the time stamp to the title. 
            This is only done if the given dataset only has one time value. 
            Default is `True`.

        Returns
        -------
        dataset_title : `str`
            The title for the dataset.
        
        Examples
        --------
        >>> from seaicecp.plot.labes_and_titles import make_title
        >>> example_file = '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_200001-200012.nc'
        >>> make_title(example_file)
        'EC-Earth3P-HR hist-1950 r1i1p1f1 '
        >>> import xarray as xr
        >>> example_xr = xr.open_dataset(example_file).isel(time=6)
        >>> make_title(example_xr)
        'EC-Earth3P-HR hist-1950 r1i1p1f1 2000-07-16T12:00:00.000000000 '
    """
    # Verify input arguments
    if isinstance(dataset, str):
        # Wrap that string into a list
        dataset = [dataset]
    if isinstance(dataset, type([])):
        if len(dataset) < 1:
            raise ValueError(f"(make_title) `dataset` must have at least one item. Got: {dataset}")
        for datafile in dataset:
            if not isinstance(datafile, str):
                raise TypeError(f"(make_title) Each item in `dataset` list must be a string. Got: {type(datafile)}")
            # Verify this is a valid path
            datafile = verify_path(datafile)
            if not datafile.endswith('.nc'):
                raise TypeError(f"(plot_time_series) `datafile` must be a `.nc` filepath. Got: {datafile}")
        # Load all the files at once
        dataset = xr.open_mfdataset(dataset)
    elif not isinstance(dataset, (xr.Dataset)):
        raise TypeError(f"(make_title) `dataset` must be a string, `xr.Dataset`. Got type: {type(dataset)}")
    if not isinstance(add_source_id, bool):
        raise TypeError(f"(make_title) `add_source_id` must be a `bool`. Got type: {type(add_source_id)}")
    if not isinstance(add_experiment_id, bool):
        raise TypeError(f"(make_title) `add_experiment_id` must be a `bool`. Got type: {type(add_experiment_id)}")
    if not isinstance(add_variant_label, bool):
        raise TypeError(f"(make_title) `add_variant_label` must be a `bool`. Got type: {type(add_variant_label)}")
    if not isinstance(add_time_stamp, bool):
        raise TypeError(f"(make_title) `add_time_stamp` must be a `bool`. Got type: {type(add_time_stamp)}")

    # Get the dataset's attribute keys
    attr_keys = dataset.attrs.keys()

    # Start the title string
    dataset_title = ""

    # Add the source ID
    if add_source_id:
        if 'source_id' not in attr_keys:
            raise KeyError(f"(make_title) `dataset` has no `source_id` attribute. Available attributes: {attr_keys}")
        dataset_title = f"{dataset_title}{dataset.attrs['source_id']} "
    # Add the experiment ID
    if add_experiment_id:
        if 'experiment_id' not in attr_keys:
            raise KeyError(f"(make_title) `dataset` has no `experiment_id` attribute. Available attributes: {attr_keys}")
        dataset_title = f"{dataset_title}{dataset.attrs['experiment_id']} "
    # Add the variant label
    if add_variant_label:
        if 'variant_label' in attr_keys:
            variant_label_attr = 'variant_label'
        elif 'parent_variant_label' in attr_keys:
            variant_label_attr = 'parent_variant_label'
        else:
            raise KeyError(f"(make_label) `dataset` has no `variant_label` or `parent_variant_label` attribute. Available attributes: {attr_keys}")
        dataset_title = f"{dataset_title}{dataset.attrs[variant_label_attr]} "
    # Add the time stamp
    if add_time_stamp:
        # Get the coordinate names
        coord_names = list(dataset.coords.keys())
        # Find the time coordinate
        if 'time' in coord_names:
            time_coord = 'time'
        elif 'year' in coord_names:
            time_coord = 'year'
        else:
            return dataset_title
        # Check whether there is more than one time slice
        if dataset[time_coord].size == 1:
            # Get the value of the time stamp as a string
            this_time_stamp = str(dataset[time_coord].values)
            # Add the time stamp to the title
            dataset_title = f"{dataset_title}{this_time_stamp} "
    
    return dataset_title
