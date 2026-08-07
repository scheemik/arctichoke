import os
import xarray as xr

# Need to specify the sub-module when pulling from the same parent module
from arctichoke.analysis.sum_by_month import sum_by_month
from arctichoke.dataset import select_months
from arctichoke.path import list_variable_files, make_file_path, select_files_by_time

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
        >>> from arctichoke.plot import make_climatology
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
        >>> from arctichoke.plot import make_climatology
        >>> make_climatology(
        >>>     this_source_id = 'EC-Earth3P-HR',
        >>>     this_var = 'silandfast',
        >>>     this_variant_label = 'r1i1p2f1',
        >>>     this_modification = 'trim_CAA_',
        >>>     save_files = True,
        >>> )
    """
    # Verify input arguments
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

    ## Assemble base filepath
    base_filepath = filelist[0]
    # Update the variable name
    base_filepath = base_filepath.replace(this_var, f"{this_var}_clim")
    # Get the base file stem, which is the filepath without the time stamp
    ## NOTE: This assumes a time stamp in the format `YYYYMM-YYYYMM.nc`
    base_filestem = base_filepath[:-16]
    # Verify that this is the file path for the year 1950
    if not base_filepath.endswith('195001-195012.nc'):
        base_filepath = f"{base_filestem}195001-195012.nc"
    # Make sure the directory structure exists for this base file path
    make_file_path(base_filepath)

    # Save the climatology dataset to the base filepath
    if verbose:
        print(f"(save_climatology_files) Saving dataset to base file path:\n\t{base_filepath}")
    dataset_clim.to_netcdf(base_filepath)
