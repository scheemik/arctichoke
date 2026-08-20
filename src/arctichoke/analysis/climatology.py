import numpy as np
import os
import warnings
import xarray as xr

# Need to specify the sub-module when pulling from the same parent module
from arctichoke import get_current_datetime_str
from arctichoke.analysis.sum_by_month import sum_by_month
from arctichoke.dataset import make_mask, select_months
from arctichoke.path import list_variable_files, make_file_path, select_files_by_time
from arctichoke.verify import verify_path

def make_climatology(
    this_source_id: str,
    this_var: str,
    this_variant_label: str,
    this_modification: str,
    start_year: int = 1950,
    end_year: int = 1969,
    find_mean: bool = True,
    select_summer: bool = False,
    save_files: bool = False,
    verbose: bool = False,
    **kwargs,
):
    """ Makes a climatology of the specified dataset.

        Take the mean value for each month across the specified years for the specified dataset.
        If `find_mean=False`, then the sum for each month is taken instead of the mean.  

        Parameters
        ----------
        this_source_id : `str`
            The source ID of the model to analyze.
            Example: `'EC-Earth3P-HR'`.
        this_var : `str`
            The variable ID of the variable to analyze.
            Example: `'sithick'`.
        this_variant_label : `str`
            The variant label of the model to analyze.
            Example: `'r1i1p2f1'`.
        this_modification : `str`
            The modification of the data to analyze.
            Example: `'trim_CAA_'`.
        start_year : `int`, optional
            The first year of the climatology.
            Default is `1950`.
        end_year : `int`, optional
            The final year of the climatology.
            This is inclusive, meaning the year given here will be included in the climatology.
            Default is `1969`.
        find_mean : `bool`, optional
            Whether to take the mean for each month across all years or the sum.
            This value is passed directly to `sum_by_month()`.
            Default is `True`.
        select_summer : `bool`, optional
            Whether to use `select_months()` to only analyze the summer months (June-October).
            Default is `False`.
        save_files : `bool`, optional
            Whether to save the climatology data to files using `save_climatology_files()`.
            Default is `False`.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `list_variable_files()`.

        Returns
        -------
        dataset_clim : `xarray.Dataset`
            A dataset of the climatology of the specified data.
            This dataset will have a time axis of the months of the year present in the specified data, that is with a time axis of 1-12 in length.
        
        Examples
        --------
        >>> from arctichoke.analysis import make_climatology
        >>> make_climatology(
        >>>     this_source_id = 'EC-Earth3P-HR',
        >>>     this_var = 'silandfast',
        >>>     this_variant_label = 'r1i1p2f1',
        >>>     this_modification = 'trim_CAA_',
        >>> )
    """
    # Verify input arguments
    ## Note: `source_id`, `variable_id`, `variant_label`, and `with_modification` are verified by `list_variable_files()`
    if not isinstance(start_year, int):
        raise TypeError(f"(make_climatology) `start_year` must be an integer. Got type: {type(start_year)}")
    if not isinstance(end_year, int):
        raise TypeError(f"(make_climatology) `end_year` must be an integer. Got type: {type(end_year)}")
    if not isinstance(find_mean, (bool, type(None))):
        raise TypeError(f"(make_climatology) `find_mean` must be a `bool` or `None`. Got type: {type(find_mean)}")
    if not isinstance(select_summer, bool):
        raise TypeError(f"(make_climatology) `select_summer` must be a `bool`. Got type: {type(select_summer)}")
    if not isinstance(save_files, bool):
        raise TypeError(f"(make_climatology) `save_files` must be a `bool`. Got type: {type(save_files)}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(make_climatology) `verbose` must be a `bool`. Got type: {type(verbose)}")
    # Get the list of data files
    filelist = list_variable_files(
        source_id = this_source_id,
        variable_id = this_var,
        variant_label = this_variant_label,
        with_modification = this_modification,
        verbose = verbose,
        **kwargs,
    )
    # Narrow the list of datafiles to be within the specified years
    filelist = select_files_by_time(
        filelist,
        start = start_year,
        end = end_year,
        verbose = verbose,
    )
    if len(filelist) < 2:
        raise ValueError(f"(make_climatology) The length of the list of specified data files must be greater than 1. Got: {filelist}")
    # Open those files into a multi-file dataset
    if select_summer:
        dataset = select_months(
            filelist,
            verbose = verbose,
        )
    else:
        dataset = xr.open_mfdataset(
            filelist,
            data_vars = 'all'
        )
    # Get one value per month of the year, either the sum or mean
    dataset_clim = sum_by_month(
        dataset,
        find_mean = find_mean,
        verbose = verbose,
    )

    # Add marker attributes
    dataset_clim.attrs['climatology_start'] = start_year
    dataset_clim.attrs['climatology_end'] = end_year

    # Save the climatology to file, if applicable
    if save_files:
        save_climatology_files(
            dataset_clim,
            this_source_id,
            this_var,
            this_variant_label,
            this_modification,
            find_mean,
            start_year,
            end_year,
            verbose = verbose,
            **kwargs,
        )

    return dataset_clim

def save_climatology_files(
    dataset_clim: xr.DataArray,
    this_source_id: str,
    this_var: str,
    this_variant_label: str,
    this_modification: str,
    find_mean: bool,
    start_year: int,
    end_year: int,
    sithick_threshold: (int, float) = None,
    overwrite: bool = False,
    verbose: bool = False,
    **kwargs,
):
    """ Makes a climatology of the specified dataset.

        Take the mean value for each month across the specified years for the specified dataset.
        If `find_mean=False`, then the sum for each month is taken instead of the mean.  

        Parameters
        ----------
        dataset_clim : `xarray.Dataset`
            The climatology dataset to save to file.
        this_source_id : `str`
            The source ID of the model to save to file.
            Example: `'EC-Earth3P-HR'`.
        this_var : `str`
            The variable ID of the variable to save to file.
            Example: `'sithick'`.
        this_variant_label : `str`
            The variant label of the model to save to file.
            Example: `'r1i1p2f1'`.
        this_modification : `str`
            The modification of the data to save to file.
            Example: `'trim_CAA_'`.
        find_mean : `bool`
            Whether the climatology data were means or sums.
            Default is `True`.
        start_year : `int`
            The first year of the climatology.
        end_year : `int`
            The final year of the climatology.
            This is inclusive, meaning the year given here will be included in the climatology.
        sithick_threshold : `int`, `float`, `None`, optional
            The value of the threshold that the given climatology was made with a sea ice thickness mask.
            If `None` is given, assume the climatology was not made with a sea ice thickness mask.
            Default is `None`.
        overwrite : `bool`, optional
            Whether to overwrite an existing file if it exists.
            Default is `False`.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `list_variable_files()`.

        Returns
        -------
        None
        
        Examples
        --------
        >>> from arctichoke.analysis import save_climatology_files
        >>> save_climatology_files(
        >>>     this_source_id = 'EC-Earth3P-HR',
        >>>     this_var = 'silandfast',
        >>>     this_variant_label = 'r1i1p2f1',
        >>>     this_modification = 'trim_CAA_',
        >>>     save_files = True,
        >>> )
    """
    # Verify input arguments
    if not isinstance(sithick_threshold, (int, float, type(None))):
        raise TypeError(f"(save_climatology_files) `sithick_threshold` must be an integer, `float`, or `None`. Got type: {type(sithick_threshold)}")
    if not isinstance(find_mean, bool):
        raise TypeError(f"(save_climatology_files) `find_mean` must be a `bool`. Got type: {type(find_mean)}")
    if not isinstance(overwrite, bool):
        raise TypeError(f"(save_climatology_files) `overwrite` must be a `bool`. Got type: {type(overwrite)}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(save_climatology_files) `verbose` must be a `bool`. Got type: {type(verbose)}")

    # Get the list of data files
    filelist = list_variable_files(
        source_id = this_source_id,
        variable_id = this_var,
        variant_label = this_variant_label,
        with_modification = this_modification,
        verbose = verbose,
        **kwargs,
    )

    ## Assemble base filepath
    base_filepath = filelist[0]
    # Update the variable name
    if find_mean:
        var_suffix = 'month_mean'
    else:
        var_suffix = 'month_sum'
    if not isinstance(sithick_threshold, type(None)):
        var_suffix = f'si{str(sithick_threshold)}mthick_{var_suffix}'
    base_filepath = base_filepath.replace(this_var, f"{this_var}_{var_suffix}")
    # Get the base file stem, which is the filepath without the time stamp
    ## NOTE: This assumes a time stamp in the format `YYYYMM-YYYYMM.nc`
    base_filestem = base_filepath[:-16]
    # Set the time stamp to include the start and end years
    base_filepath = f"{base_filestem}{start_year}01-{end_year}12.nc"
    # Make sure the directory structure exists for this base file path
    make_file_path(base_filepath)
    if verbose:
        print(f"(save_climatology_files) The base filepath is `{base_filepath}`")

    # Check whether the file climatology file already exists
    try:
        verify_path(base_filepath)
        if overwrite == False:
            warnings.warn(f"(save_climatology_files) File `{base_filepath}` \n\texists already. To overwrite this file, set `overwrite` to `True`.", UserWarning)
        else:
            if verbose:
                print(f"\t(save_climatology_files) Overwriting file `{base_filepath}`")
            dataset_clim.to_netcdf(base_filepath)
    except (FileNotFoundError):
        if True:
            print(f"\t(save_climatology_files) Writing file `{base_filepath}`")
        dataset_clim.to_netcdf(base_filepath)

def make_sithick_masked_climatology(
    this_source_id: str,
    this_var: str,
    this_variant_label: str,
    this_modification: str,
    start_year: int = 1950,
    end_year: int = 1969,
    sithick_threshold: (int, float) = 2,
    find_mean: bool = True,
    select_summer: bool = False,
    save_files: bool = False,
    verbose: bool = False,
    **kwargs,
):
    """ Makes a climatology of the specified dataset, masking it by sea ice thickness.

        Create a mask based on sea ice thickness values on a per-month basis.
        Apply that sea ice thickness mask to the specified data.
        Take the mean value for each month across the specified years for the specified dataset.
        If `find_mean=False`, then the sum for each month is taken instead of the mean.  

        Parameters
        ----------
        this_source_id : `str`
            The source ID of the model to analyze.
            Example: `'EC-Earth3P-HR'`.
        this_var : `str`
            The variable ID of the variable to analyze.
            Example: `'sithick'`.
        this_variant_label : `str`
            The variant label of the model to analyze.
            Example: `'r1i1p2f1'`.
        this_modification : `str`
            The modification of the data to analyze.
            Example: `'trim_CAA_'`.
        start_year : `int`, optional
            The first year of the climatology.
            Default is `1950`.
        end_year : `int`, optional
            The final year of the climatology.
            This is inclusive, meaning the year given here will be included in the climatology.
            Default is `1969`.
        sithick_threshold : `int`, `float`, optional
            The threshold for the sea ice thickness mask, given in meters.
            Default is `2`.
        find_mean : `bool`, optional
            Whether to take the mean for each month across all years or the sum.
            This value is passed directly to `sum_by_month()`.
            Default is `True`.
        select_summer : `bool`, optional
            Whether to use `select_months()` to only analyze the summer months (June-October).
            Default is `False`.
        save_files : `bool`, optional
            Whether to save the climatology data to files using `save_climatology_files()`.
            Default is `False`.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `list_variable_files()`.

        Returns
        -------
        dataset_clim : `xarray.Dataset`
            A dataset of the climatology of the specified data.
            This dataset will have a time axis of the months of the year present in the specified data, that is with a time axis of 1-12 in length.
        
        Examples
        --------
        >>> from arctichoke.analysis import make_sithick_masked_climatology
        >>> make_sithick_masked_climatology(
        >>>     this_source_id = 'EC-Earth3P-HR',
        >>>     this_var = 'silandfast',
        >>>     this_variant_label = 'r1i1p2f1',
        >>>     this_modification = 'trim_CAA_',
        >>> )
    """
    # Verify input arguments
    ## Note: `source_id`, `variable_id`, `variant_label`, and `with_modification` are verified by `list_variable_files()`
    if not isinstance(start_year, int):
        raise TypeError(f"(make_sithick_masked_climatology) `start_year` must be an integer. Got type: {type(start_year)}")
    if not isinstance(end_year, int):
        raise TypeError(f"(make_sithick_masked_climatology) `end_year` must be an integer. Got type: {type(end_year)}")
    if not isinstance(sithick_threshold, (int, float)):
        raise TypeError(f"(make_sithick_masked_climatology) `sithick_threshold` must be an integer or `float`. Got type: {type(find_mean)}")
    if not isinstance(find_mean, (bool, type(None))):
        raise TypeError(f"(make_sithick_masked_climatology) `find_mean` must be a `bool` or `None`. Got type: {type(find_mean)}")
    if not isinstance(select_summer, bool):
        raise TypeError(f"(make_sithick_masked_climatology) `select_summer` must be a `bool`. Got type: {type(select_summer)}")
    if not isinstance(save_files, bool):
        raise TypeError(f"(make_sithick_masked_climatology) `save_files` must be a `bool`. Got type: {type(save_files)}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(make_sithick_masked_climatology) `verbose` must be a `bool`. Got type: {type(verbose)}")
    # Get the list of data files
    filelist = list_variable_files(
        source_id = this_source_id,
        variable_id = this_var,
        variant_label = this_variant_label,
        with_modification = this_modification,
        verbose = verbose,
        **kwargs,
    )
    # Narrow the list of datafiles to be within the specified years
    filelist = select_files_by_time(
        filelist,
        start = start_year,
        end = end_year,
        verbose = verbose,
    )
    if len(filelist) < 2:
        raise ValueError(f"(make_sithick_masked_climatology) The length of the list of specified data files must be greater than 1. Got: {filelist}")
    # Get the list of sea ice thickness data files
    sithick_filelist = list_variable_files(
        source_id = this_source_id,
        variable_id = 'sithick',
        variant_label = this_variant_label,
        with_modification = this_modification,
        verbose = verbose,
        **kwargs,
    )
    # Narrow the list of datafiles to be within the specified years
    sithick_filelist = select_files_by_time(
        sithick_filelist,
        start = start_year,
        end = end_year,
        verbose = verbose,
    )
    if len(sithick_filelist) < 2:
        raise ValueError(f"(make_sithick_masked_climatology) The length of the list of `sithick` data files must be greater than 1. Got: {sithick_filelist}")
    # Open those files into a multi-file dataset
    if select_summer:
        dataset = select_months(
            filelist,
            verbose = verbose,
        )
        sithick_dataset = select_months(
            sithick_filelist,
            verbose = verbose,
        )
    else:
        dataset = xr.open_mfdataset(
            filelist,
            data_vars = 'all'
        )
        sithick_dataset = xr.open_mfdataset(
            sithick_filelist,
            data_vars = 'all'
        )

    # Get the maximum possible integer to cover all reasonable values of `sithick`
    numpy_int32_max = np.iinfo(np.int32).max
    # Make the mask of sea ice thicker than the specified threshold
    si2mthick_var = f'si{str(sithick_threshold)}mthick'
    sithick_mask_dataset = make_mask(
        sithick_dataset,
        var = 'sithick',
        mask_var_name = si2mthick_var,
        mask_this_range = [sithick_threshold, numpy_int32_max],
        val_inside_range = 1,
        val_outside_range = np.nan,
        add_mask_attrs = True,
        verbose = verbose,
    )
    # Copy the variable attributes
    keep_these_attrs = dataset[this_var].attrs 
    # Set the new variable name
    new_masked_var = f'{this_var}_{si2mthick_var}'
    # Apply the sea ice thickness mask
    dataset[new_masked_var] = dataset[this_var] * sithick_mask_dataset[si2mthick_var]
    # Put the variable attributes back
    dataset[new_masked_var].attrs = keep_these_attrs
    # Modify the long name
    dataset[new_masked_var].attrs['long_name'] = dataset[new_masked_var].attrs['long_name'].replace('(Ocean Grid)', f'(thickness > {sithick_threshold} m)')
    if 'history' in dataset.attrs.keys():
        original_history = dataset.attrs['history']
    else:
        original_history = ''
    new_history_item = f"{get_current_datetime_str()} altered by `arctichoke`: Masked where `sithick` is greater than {sithick_threshold} meters."
    dataset.attrs['history'] = f"{new_history_item} {original_history}"
    if 'history' in dataset[new_masked_var].attrs.keys():
        original_history = dataset[new_masked_var].attrs['history']
    else:
        original_history = ''
    dataset[new_masked_var].attrs['history'] = f"{new_history_item} {original_history}"
    dataset = dataset.drop_vars(this_var)

    # Get one value per month of the year, either the sum or mean
    dataset_clim = sum_by_month(
        dataset,
        find_mean = find_mean,
        verbose = verbose,
    )

    # Add marker attributes
    dataset_clim.attrs['climatology_start'] = start_year
    dataset_clim.attrs['climatology_end'] = end_year

    # Save the climatology to file, if applicable
    if save_files:
        save_climatology_files(
            dataset_clim,
            this_source_id,
            this_var,
            this_variant_label,
            this_modification,
            find_mean,
            start_year,
            end_year,
            sithick_threshold,
            verbose = verbose,
            **kwargs,
        )

    return dataset_clim
