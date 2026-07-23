import numpy as np
import xarray as xr
import warnings

from cdo import Cdo
cdo = Cdo()
# Set path for temporary files in case of a crash
cdo = Cdo(tempdir='./cdo_tmp/')
cdo.cleanTempDir()

from arctichoke import get_current_datetime_str
from arctichoke.dataset import get_variable_name, make_mask, trim_latlon
from arctichoke.path import make_file_path
import arctichoke.params as sps
from arctichoke.verify import verify_path

def find_multiyear_ice(
    dataset: (str, [str], xr.DataArray, xr.Dataset),
    multiyear_threshold: (int, float) = 2, 
    siage_var: str = 'siage2',
    save_as: str = None,
    verbose: bool = False,
    **kwargs,
):
    """ Calculate where multi-year ice is from the dataset.

        Verify the dataset contains the `siage` variable, and adds a variable `simultiyear` which is 1 where `siage` is greater than 2 years (or the given threshold) and 0 elsewhere.

        Parameters
        ----------
        dataset : `str`, list of `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset of which to find the locations of multi-year ice.
        multiyear_threshold : `int`, `float`, optional
            The threshold above which to mark multi-year ice.
            Default is `2` years.
        siage_var : `str`, optional
            The name of the variable to use from the provided dataset.
            Must be either `siage` or `siage2`.
            Default is `siage2`.
        save_as : `str`, `None`, optional
            The file name to which to save the modified dataset.
            Default is `None`, which doesn't save the dataset to a file.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `cdo.setrtoc2()`.

        Returns
        -------
        multiyearice_xr : `xarray.Dataset`
            A dataset where multi-year ice is marked as `1` and all other values are `0`.
        
        Examples
        --------
        >>> from arctichoke.dataset import make_example_dataset
        >>> dataset = make_example_dataset(n=3, test_var_name='siage')
        >>> dataset['siage'].values
        array([[0., 1., 2.],
               [3., 4., 5.],
               [6., 7., 8.]])
        >>> from arctichoke.analysis import find_multiyear_ice
        >>> dataset_simultiyear = find_multiyear_ice(dataset, multiyear_threshold=4)
        >>> dataset_simultiyear['simultiyear'].values
        array([[0., 0., 0.],
               [0., 1., 1.],
               [1., 1., 1.]])
    """
    # Verify input arguments
    if isinstance(dataset, str):
        # Wrap that string into a list
        dataset = [dataset]
        var_check_list = dataset
    if isinstance(dataset, (xr.Dataset, xr.DataArray)):
        input_command_prefix = ""
        input_command_files = dataset
        cdo_command = cdo.setrtoc2
        var_check_list = [dataset]
    elif isinstance(dataset, type([])):
        var_check_list = dataset
        if len(dataset) < 1:
            raise ValueError(f"(find_multiyear_ice) `dataset` must have at least one item. Got: {dataset}")
        # Start variables to add arguments to the `cdo` input command
        input_command_prefix = "[ -setrtoc2,"
        input_command_files = " :"
        for datafile in dataset:
            if not isinstance(datafile, str):
                raise TypeError(f"(find_multiyear_ice) Each item in `dataset` list must be a string. Got: {type(datafile)}")
            # Verify this is a valid path
            datafile = verify_path(datafile)
            if not datafile.endswith('.nc'):
                raise TypeError(f"(find_multiyear_ice) `datafile` must be a `.nc` filepath. Got: {datafile}")
            input_command_files = f"{input_command_files} {datafile}"
        input_command_files = f"{input_command_files} ]"
        cdo_command = cdo.mergetime
    else:
        raise TypeError(f"(find_multiyear_ice) `dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(dataset)}")
    if not isinstance(multiyear_threshold, (int, float)):
        raise TypeError(f"(find_multiyear_ice) `multiyear_threshold` must be `int` or `float`. Got type: {type(multiyear_threshold)}")
    if not isinstance(siage_var, str):
        raise TypeError(f"(find_multiyear_ice) `siage_var` must be a string. Got type: {type(siage_var)}")
    elif not siage_var in ['siage', 'siage2']:
        raise ValueError(f"(find_multiyear_ice) `siage_var` must be either `siage` or `siage2`. Got: {siage_var}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(find_multiyear_ice) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.nc' in save_as:
        raise TypeError(f"(find_multiyear_ice) `save_as` must be a `.nc` filepath. Got: {save_as}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(find_multiyear_ice) `verbose` must be a `bool`. Got type: {type(verbose)}")
    
    # Information to output
    if verbose:
        print(f"(find_multiyear_ice) `save_as`: {save_as}")

    # Get the maximum possible integer to cover all reasonable values of `siage`
    numpy_int32_max = np.iinfo(np.int32).max

    # Mask out `siage` below the threshold
    multiyearice_xr = make_mask(
        dataset,
        var = siage_var,
        mask_var_name = 'simultiyear',
        mask_this_range = [multiyear_threshold, numpy_int32_max],
        val_inside_range = 1,
        val_outside_range = 0,
        add_mask_attrs = False,
        verbose = verbose,
    )

    # Rename `siage` in the new dataset to `simultiyear`
    multiyearice_xr = multiyearice_xr.rename_vars({siage_var:'simultiyear'})

    # Modify the attributes of the dataset to reflect the changes
    multiyearice_xr['simultiyear'].attrs['standard_name'] = 'sea_ice_multiyear_marker'
    multiyearice_xr['simultiyear'].attrs['long_name'] = f'Sea Ice Age > {multiyear_threshold}%'
    multiyearice_xr['simultiyear'].attrs['units'] = '1: Yes, 0: No'
    multiyearice_xr['simultiyear'].attrs['comment'] = f'Marker of multi-year ice, where sea ice age (`{siage_var}`) >{multiyear_threshold}%'
    multiyearice_xr['simultiyear'].attrs['original_name'] = 'simultiyear'
    if 'history' in multiyearice_xr['simultiyear'].attrs.keys():
        original_history = multiyearice_xr['simultiyear'].attrs['history']
    else:
        original_history = ''
    multiyearice_xr['simultiyear'].attrs['history'] = f"{get_current_datetime_str()} altered by `arctichoke`: Calculated multi-year ice, marking `{siage_var}` > {multiyear_threshold} as 1 and 0 otherwise. {original_history}"
    if 'history' in multiyearice_xr.attrs.keys():
        original_history = multiyearice_xr.attrs['history']
    else:
        original_history = ''
    multiyearice_xr.attrs['history'] = f"{get_current_datetime_str()} altered by `arctichoke`: Calculated multi-year ice, marking `{siage_var}` > {multiyear_threshold} as 1 and 0 otherwise. {original_history}"

    # Save the modified dataset, if applicable
    if not isinstance(save_as, type(None)):
        # Save the plot to file
        multiyearice_xr.to_netcdf(save_as)
    
    return multiyearice_xr


def make_multiyear_files(
    siage_files: [str],
    map_bbox: [float, float, float, float] = None,
    version_id: str = 'v20260617',
    siage_var: str = 'siage2',
    overwrite: bool = False,
    **kwargs,
):
    """ Make multi-year files based on the lists of files given.

        For each given pair of files, load the data, trim the datasets (if applicable), calculate the multi-year ice, then save the multi-year ice dataset as a new file in the same directory structure. 

        Parameters
        ----------
        siage_files : List of `str`
            A list of paths of the sea ice concentration data files. 
        map_bbox : Array of `float`, `None`, optional
            An array of coordinates defining the bounding box of the map in the following format:
                - [LAT_MAX, LAT_MIN, LON_MAX, LON_MIN]
                
            Default is `None`, meaning the data will not be trimmed.
        version_id : `str`, optional
            The version ID to use when making the directory structure for the multi-year ice files.
            Default is `'v20260617'`.
        siage_var : `str`, optional
            The name of the variable to use from the provided sea ice concentration dataset.
            Must be either `siage` or `siage2`.
            Default is `siage2`.
        overwrite : `bool`, optional
            Whether to overwrite an existing file if it exists.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `trim_latlon()`, and `find_multiyear_ice()`.

        Returns
        -------
        None
        
        Examples
        --------
        >>> from arctichoke.path import list_variable_files
        >>> from arctichoke.analysis import make_multiyear_files
        >>> from arctichoke.params import CAA_BBOX
        >>> this_model = 'EC-Earth3P-HR'
        >>> for this_variant_label in [
        >>>     'r1i1p2f1', 
        >>>     'r2i1p2f1', 
        >>>     'r3i1p2f1',
        >>> ]:
        >>>     for this_experiment in ['hist-1950']:#, 'highres-future']:
        >>>         siage_list = list_variable_files(
        >>>             source_id = this_model,
        >>>             variable_id = 'siage2',
        >>>             experiment_id = this_experiment,
        >>>             variant_label = this_variant_label,
        >>>         )
        >>>         make_multiyear_files(
        >>>             siage_files = siage_list,
        >>>             map_bbox = CAA_BBOX,
        >>>             precise_trim = False,
        >>>         )
        (make_multiyear_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/simultiyear/gn/v20260617/trim_CAA_simultiyear_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc`.
        (make_multiyear_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/simultiyear/gn/v20260617/trim_CAA_simultiyear_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195101-195112.nc`.
        (make_multiyear_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/simultiyear/gn/v20260617/trim_CAA_simultiyear_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195201-195212.nc`.
        ...
        (make_multiyear_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/simultiyear/gn/v20260617/trim_CAA_simultiyear_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201201-201212.nc`.
        (make_multiyear_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/simultiyear/gn/v20260617/trim_CAA_simultiyear_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201301-201312.nc`.
        (make_multiyear_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/simultiyear/gn/v20260617/trim_CAA_simultiyear_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201401-201412.nc`.
    """
    # Verify input arguments
    if isinstance(siage_files, str):
        siage_files = [siage_files]
    elif not isinstance(siage_files, type([])):
        raise TypeError(f"(make_multiyear_files) `siage_files` must be a list. Got type: {type(siage_files)}")
    for item in siage_files:
        if not isinstance(item, str):
            raise TypeError(f"(make_multiyear_files) `siage_files` must be a list of strings. Got type: {type(item)} for item {item}")
    if isinstance(map_bbox, type([])):
        if not len(map_bbox) == 4:
            raise ValueError(f"(make_multiyear_files) `map_bbox` must have a length of 4. Got length: {len(map_bbox)}")
        else: 
            for i in range(len(map_bbox)):
                if not isinstance(map_bbox[i], (int, float)):
                    raise TypeError(f"(make_multiyear_files) `map_bbox[{i}]` must be a number. Got type: {type(map_bbox[i])}")
    elif not isinstance(map_bbox, (type(None), type([]))):
        raise TypeError(f"(make_multiyear_files) `map_bbox` must be a list or `None`. Got type: {type(map_bbox)}")
    if not isinstance(version_id, str):
        raise TypeError(f"(make_multiyear_files) `version_id` must be a string. Got type: {type(version_id)}")
    if not isinstance(siage_var, str):
        raise TypeError(f"(make_multiyear_files) `siage_var` must be a string. Got type: {type(siage_var)}")
    elif not siage_var in ['siage', 'siage2']:
        raise ValueError(f"(make_multiyear_files) `siage_var` must be either `siage` or `siage2`. Got: {siage_var}")
    if not isinstance(overwrite, bool):
        raise TypeError(f"(make_multiyear_files) `overwrite` must be a `bool`. Got type: {type(overwrite)}")

    # Loop across each file in the list
    for i in range(len(siage_files)):
        # Verify the filepaths exist
        siage_filepath = verify_path(siage_files[i])
        # Verify the filepaths are for the same model run
        siage_filestem = siage_filepath.replace(siage_var, '')
        # Get the version ID to replace
        replace_this_version_ID = siage_filepath.split('/')[-2]
        # Assemble the multiyear filename
        multiyear_filepath = siage_filepath.replace(replace_this_version_ID, version_id)
        multiyear_filepath = multiyear_filepath.replace(siage_var, 'simultiyear')
        # Add trimming prefix, if applicable
        if not isinstance(map_bbox, type(None)):
            if map_bbox == sps.CAA_BBOX:
                name_prefix = 'trim_CAA_'
            elif map_bbox == sps.NWP_BBOX:
                name_prefix = 'trim_NWP_'
            else:
                name_prefix = 'trim_'
            if verbose:
                print(f"(make_multiyear_files) Adding prefix to file names: {name_prefix}")
            multiyear_filename = multiyear_filepath.split('/')[-1]
            multiyear_filepath = multiyear_filepath.replace(multiyear_filename, f"{name_prefix}{multiyear_filename}")
        # Make sure the directory exists
        make_file_path(multiyear_filepath)
        # Check whether the file exists
        try:
            verify_path(multiyear_filepath)
            if overwrite == False:
                warnings.warn(f"(make_multiyear_files) File `{multiyear_filepath}` exists already. To overwrite this file, set `overwrite` to `True`.", UserWarning)
                continue
            else:
                print(f"\t(make_multiyear_files) Overwriting file `{multiyear_filepath}`.")
        except (FileNotFoundError):
            print(f"\t(make_multiyear_files) Writing file `{multiyear_filepath}`.")
        # Load `siage` file with `xarray`
        siage_xr = xr.open_dataset(siage_filepath)
        # Trim the `siage` dataset, if applicable
        if not isinstance(map_bbox, type(None)):
            siage_xr = trim_latlon(
                dataset = siage_xr,
                map_bbox = map_bbox,
                **kwargs,
            )
        # Calculate the multiyear ice and save to file
        find_multiyear_ice(
            dataset = siage_xr,
            siage_var = siage_var,
            save_as = multiyear_filepath,
            **kwargs,
        )

    return None
