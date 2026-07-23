import numpy as np
import xarray as xr
import warnings

from cdo import Cdo
cdo = Cdo()
# Set path for temporary files in case of a crash
cdo = Cdo(tempdir='./cdo_tmp/')
cdo.cleanTempDir()

from arctichoke import get_current_datetime_str
from arctichoke.dataset import get_min_max, get_variable_name, trim_latlon
from arctichoke.path import make_file_path
import arctichoke.params as sps
from arctichoke.verify import verify_path

def calc_siage(
    siage_dataset: (str, [str], xr.DataArray, xr.Dataset),
    save_as: str = None,
    verbose: bool = False,
    **kwargs,
):
    """ Calculate sea ice age in years.

        Verify the dataset contains the `siage` variable, determine the units of `siage`, calculate `siage` in years if applicable, and return a new dataset.

        Parameters
        ----------
        siage_dataset : `str`, list of `str`, `xarray.DataArray`, `xarray.Dataset`
            The sea ice age dataset.
        save_as : `str`, `None`, optional
            The file name to which to save the modified dataset.
            Default is `None`, which doesn't save the dataset to a file.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments.

        Returns
        -------
        siage2_xr : `xarray.Dataset`
            A dataset of calculated sea ice age values.
        
        Examples
        --------
        >>> from arctichoke.dataset import make_example_dataset
        >>> dataset_0 = make_example_dataset(n=3, test_var_name='siage')
        >>> dataset_0['siage'].values
        array([[1., 2., 3.],
               [4., 5., 6.],
               [7., 8., 9.]])
        >>> from arctichoke.analysis import calc_siage
        >>> dataset_siage2 = calc_siage(siage_dataset=dataset_0)
        >>> dataset_siage2['siage2'].values
        array([[ 0.        , 50.        , 66.66666667],
               [75.        , 80.        , 83.33333333],
               [85.71428571, 87.5       , 88.88888889]])
    """
    # Verify input arguments
    if isinstance(siage_dataset, str):
        # Wrap that string into a list
        siage_dataset = [siage_dataset]
    if isinstance(siage_dataset, type([])):
        var_check_list = siage_dataset
        if len(siage_dataset) < 1:
            raise ValueError(f"(calc_siage) `siage_dataset` must have at least one item. Got: {siage_dataset}")
        for datafile in siage_dataset:
            if not isinstance(datafile, str):
                raise TypeError(f"(calc_siage) Each item in `siage_dataset` list must be a string. Got: {type(datafile)}")
            # Verify this is a valid path
            datafile = verify_path(datafile)
            if not datafile.endswith('.nc'):
                raise TypeError(f"(calc_siage) `datafile` must be a `.nc` filepath. Got: {datafile}")
        # Load all the files at once
        siage_dataset = xr.open_mfdataset(siage_dataset)
    elif not isinstance(siage_dataset, (str, xr.Dataset, xr.DataArray)):
        raise TypeError(f"(calc_siage) `siage_dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(siage_dataset)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(calc_siage) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.nc' in save_as:
        raise TypeError(f"(calc_siage) `save_as` must be a `.nc` filepath. Got: {save_as}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(calc_siage) `verbose` must be a `bool`. Got type: {type(verbose)}")
    
    # Information to output
    if verbose:
        print(f"(calc_siage) `save_as`: {save_as}")

    # Verify the `siage_dataset` dataset contains the `siage` variable
    if isinstance(siage_dataset, xr.Dataset):
        var_name = get_variable_name(siage_dataset)
        siage_xr = siage_dataset['siage']
    else:
        var_name = siage_dataset.name
        siage_xr = siage_dataset
    if isinstance(var_name, str):
        if not var_name == 'siage':
            raise ValueError(f"(calc_siage) `siage_dataset` must contain the variable `siage`. Available variable: {var_name}")
    elif isinstance(var_name, type([])):
        if not 'siage' in var_name:
            raise ValueError(f"(calc_siage) `siage_dataset` must contain the variable `siage`. Available variables: {var_name}")
    else:
        raise TypeError(f"(calc_siage) `get_variable_name` returned something other than a string or list: {var_name}")

    # Find minimum and maximum value
    siage_min, siage_max = get_min_max(
        siage_xr,
        'siage',
    )
    if siage_max > 1e+27:
        if verbose:
            print(f"(calc_siage) Maximum value of `siage` found to be {siage_max}. Mapping large values to `nan`.")
        # Get the maximum possible integer to cover all reasonable values of `siconc`
        numpy_float64_max = np.finfo(np.float64).max
        # Assemble the string to specify the range and the output values
        range_string = f"{1e+27},{numpy_float64_max},{np.nan}"
        if verbose:
            print(f"(calc_siage) `input_command`: cdo setrtoc,{range_string} dataset")
        # If only processing one `xr.Dataset`, the `input` argument cannot include the range string
        siage_dataset = cdo.setrtoc(
            range_string,
            input=siage_dataset, 
            returnXDataset='mask'
        )
    
    # Check the units of `siage`
    try:
        if isinstance(siage_dataset, xr.Dataset):
            siage_units = siage_dataset['siage'].attrs['units']
        else:
            siage_units = siage_dataset.attrs['units']
    except:
        warnings.warn(f"(calc_siage) `siage_dataset`'s `siage` variable has no `units` attribute. Assuming the units are seconds", UserWarning)
        siage_units = 's'

    # Convert `siage` to get units of years
    if siage_units == 's':
        seconds_to_years = 60 * 60 * 24 * 365
        if verbose:
            print(f"(calc_siage) Found units of `s`. Dividing by {seconds_to_years} to get units of years.")
        siage_dataset['siage'] = siage_dataset['siage'] / (seconds_to_years)
    else:
        raise NotImplementedError(f"(calc_siage) `siage_dataset`'s `siage` variable has `units` of {siage_units}. Calculation only implemented for units of `s`.")

    # Rename `siage` to `siage2`
    siage_dataset = siage_dataset.rename_vars({'siage':'siage2'})

    # Modify the attributes of the dataset to reflect the changes
    siage_dataset['siage2'].attrs['units'] = 'yr'
    if 'history' in siage_dataset['siage2'].attrs.keys():
        original_history = siage_dataset['siage2'].attrs['history']
    else:
        original_history = ''
    siage_dataset['siage2'].attrs['history'] = f"{get_current_datetime_str()} altered by `arctichoke`: Converted units from seconds to years. {original_history}"
    if 'history' in siage_dataset.attrs.keys():
        original_history = siage_dataset.attrs['history']
    else:
        original_history = ''
    siage_dataset.attrs['history'] = f"{get_current_datetime_str()} altered by `arctichoke`: Converted units from seconds to years. {original_history}"

    # Save the modified dataset, if applicable
    if not isinstance(save_as, type(None)):
        # Save the plot to file
        siage_dataset.to_netcdf(save_as)
    
    return siage_dataset

def make_siage_files(
    siage_files: [str],
    map_bbox: [float, float, float, float] = None,
    version_id: str = 'v20260617',
    overwrite: bool = False,
    **kwargs,
):
    """ Make sea ice age files based on the lists of files given.

        For each given pair of files, load the data, trim the datasets (if applicable), calculate the sea ice age, then save the sea ice age dataset as a new file in the same directory structure. 

        Parameters
        ----------
        siage_files : List of `str`
            A list of paths of the sea ice age data files. 
        map_bbox : Array of `float`, `None`, optional
            An array of coordinates defining the bounding box of the map in the following format:
                - [LAT_MAX, LAT_MIN, LON_MAX, LON_MIN]
                
            Default is `None`, meaning the data will not be trimmed.
        version_id : `str`, optional
            The version ID to use when making the directory structure for the sea ice age files.
            Default is `'v20260617'`.
        overwrite : `bool`, optional
            Whether to overwrite an existing file if it exists.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `trim_latlon()`, and `calc_siage()`.

        Returns
        -------
        None
        
        Examples
        --------
        >>> from arctichoke.path import list_variable_files
        >>> from arctichoke.analysis import make_siage_files
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
        >>>             variable_id = 'siage',
        >>>             experiment_id = this_experiment,
        >>>             variant_label = this_variant_label,
        >>>         )
        >>>         make_siage_files(
        >>>             siage_files = siage_list,
        >>>             map_bbox = CAA_BBOX,
        >>>             precise_trim = False,
        >>>         )
        (make_siage_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siage2/gn/v20260617/trim_CAA_siage2_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc`.
        (make_siage_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siage2/gn/v20260617/trim_CAA_siage2_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195101-195112.nc`.
        (make_siage_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siage2/gn/v20260617/trim_CAA_siage2_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195201-195212.nc`.
        ...
        (make_siage_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/siage2/gn/v20260617/trim_CAA_siage2_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201201-201212.nc`.
        (make_siage_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/siage2/gn/v20260617/trim_CAA_siage2_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201301-201312.nc`.
        (make_siage_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/siage2/gn/v20260617/trim_CAA_siage2_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201401-201412.nc`.
    """
    # Verify input arguments
    if isinstance(siage_files, str):
        siage_files = [siage_files]
    elif not isinstance(siage_files, type([])):
        raise TypeError(f"(make_siage_files) `siage_files` must be a list. Got type: {type(siage_files)}")
    for item in siage_files:
        if not isinstance(item, str):
            raise TypeError(f"(make_siage_files) `siage_files` must be a list of strings. Got type: {type(item)} for item {item}")
    if isinstance(map_bbox, type([])):
        if not len(map_bbox) == 4:
            raise ValueError(f"(make_siage_files) `map_bbox` must have a length of 4. Got length: {len(map_bbox)}")
        else: 
            for i in range(len(map_bbox)):
                if not isinstance(map_bbox[i], (int, float)):
                    raise TypeError(f"(make_siage_files) `map_bbox[{i}]` must be a number. Got type: {type(map_bbox[i])}")
    elif not isinstance(map_bbox, (type(None), type([]))):
        raise TypeError(f"(make_siage_files) `map_bbox` must be a list or `None`. Got type: {type(map_bbox)}")
    if not isinstance(version_id, str):
        raise TypeError(f"(make_siage_files) `version_id` must be a string. Got type: {type(version_id)}")
    if not isinstance(overwrite, bool):
        raise TypeError(f"(make_siage_files) `overwrite` must be a `bool`. Got type: {type(overwrite)}")

    # Loop across each file in the list
    for i in range(len(siage_files)):
        # Verify the filepaths exist
        siage_filepath = verify_path(siage_files[i])
        # Get the version ID to replace
        replace_this_version_ID = siage_filepath.split('/')[-2]
        # Assemble the sea ice concentration filename
        siage2_filepath = siage_filepath.replace(replace_this_version_ID, version_id)
        siage2_filepath = siage2_filepath.replace('siage', 'siage2')
        # Add trimming prefix, if applicable
        if not isinstance(map_bbox, type(None)):
            if map_bbox == sps.CAA_BBOX:
                trim_prefix = 'trim_CAA_'
            elif map_bbox == sps.NWP_BBOX:
                trim_prefix = 'trim_NWP_'
            else:
                trim_prefix = 'trim_'
            siage2_filename = siage2_filepath.split('/')[-1]
            siage2_filepath = siage2_filepath.replace(siage2_filename, f"{trim_prefix}{siage2_filename}")
        # Make sure the directory exists
        make_file_path(siage2_filepath)
        # Check whether the file exists
        try:
            verify_path(siage2_filepath)
            if overwrite == False:
                warnings.warn(f"(make_siage_files) File `{siage2_filepath}` exists already. To overwrite this file, set `overwrite` to `True`.", UserWarning)
                continue
            else:
                print(f"\t(make_siage_files) Overwriting file `{siage2_filepath}`.")
        except (FileNotFoundError):
            print(f"\t(make_siage_files) Writing file `{siage2_filepath}`.")
        # Load `siage` and file with `xarray`
        siage_xr = xr.open_dataset(siage_filepath)
        # Trim the `siage` and dataset, if 
        if not isinstance(map_bbox, type(None)):
            siage_xr = trim_latlon(
                dataset = siage_xr,
                map_bbox = map_bbox,
                **kwargs,
            )
        # Calculate the sea ice concentration ice and save to file
        calc_siage(
            siage_dataset = siage_xr,
            save_as = siage2_filepath,
            **kwargs,
        )

    return None

