import numpy as np
import xarray as xr
import warnings

# from cdo import Cdo
# cdo = Cdo()
# # Set path for temporary files in case of a crash
# cdo = Cdo(tempdir='./cdo_tmp/')
# cdo.cleanTempDir()

from seaicecp import get_current_datetime_str
from seaicecp.dataset.get_variable import get_variable_name
from seaicecp.dataset.trim_dataset import trim_latlon
from seaicecp.path.manipulate_paths import make_file_path
import seaicecp.params as sps
from seaicecp.verify import verify_path

def calc_siconc(
    sithick_dataset: (str, [str], xr.DataArray, xr.Dataset),
    sivol_dataset: (str, [str], xr.DataArray, xr.Dataset),
    save_as: str = None,
    verbose: bool = False,
    **kwargs,
):
    """ Calculate sea ice concentration from sea ice thickness and volume.

        Verify the dataset(s) contains the `sithick` and `sivol` variables, calculate `siconc` based on those variables, and return a new dataset.

        Parameters
        ----------
        sithick_dataset : `str`, list of `str`, `xarray.DataArray`, `xarray.Dataset`
            The sea ice thickness dataset.
            Must have the same source ID, experiment ID, variant label, and dimensions sizes as `sivol_dataset`.
        sivol_dataset : `str`, list of `str`, `xarray.DataArray`, `xarray.Dataset`
            The sea ice volume dataset.
            Must have the same source ID, experiment ID, variant label, and dimensions sizes as `sithick_dataset`.
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
        siconc2_xr : `xarray.Dataset`
            A dataset of calculated sea ice concentration values.
        
        Examples
        --------
        >>> from seaicecp.dataset.example_dataset import make_example_dataset
        >>> dataset_0 = make_example_dataset(n=3, test_var_name='sithick')
        >>> dataset_0['sithick'].values
        array([[1., 2., 3.],
               [4., 5., 6.],
               [7., 8., 9.]])
        >>> dataset_1 = make_example_dataset(n=3, test_var_name='sivol')
        >>> dataset_1['sivol'].values
        array([[0., 1., 2.],
               [3., 4., 5.],
               [6., 7., 8.]])
        >>> from seaicecp.analysis import calc_siconc
        >>> dataset_siconc2 = calc_siconc(sithick_dataset=dataset_0, sivol_dataset=dataset_1)
        >>> dataset_siconc2['siconc2'].values
        array([[ 0.        , 50.        , 66.66666667],
               [75.        , 80.        , 83.33333333],
               [85.71428571, 87.5       , 88.88888889]])
    """
    # Verify input arguments
    if isinstance(sithick_dataset, str):
        # Wrap that string into a list
        sithick_dataset = [sithick_dataset]
    if isinstance(sithick_dataset, type([])):
        var_check_list = sithick_dataset
        if len(sithick_dataset) < 1:
            raise ValueError(f"(calc_siconc) `sithick_dataset` must have at least one item. Got: {sithick_dataset}")
        for datafile in sithick_dataset:
            if not isinstance(datafile, str):
                raise TypeError(f"(calc_siconc) Each item in `sithick_dataset` list must be a string. Got: {type(datafile)}")
            # Verify this is a valid path
            datafile = verify_path(datafile)
            if not datafile.endswith('.nc'):
                raise TypeError(f"(calc_siconc) `datafile` must be a `.nc` filepath. Got: {datafile}")
        # Load all the files at once
        sithick_dataset = xr.open_mfdataset(sithick_dataset)
    elif not isinstance(sithick_dataset, (str, xr.Dataset, xr.DataArray)):
        raise TypeError(f"(calc_siconc) `sithick_dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(sithick_dataset)}")
    if isinstance(sivol_dataset, str):
        # Wrap that string into a list
        sivol_dataset = [sivol_dataset]
    if isinstance(sivol_dataset, type([])):
        var_check_list = sivol_dataset
        if len(sivol_dataset) < 1:
            raise ValueError(f"(calc_siconc) `sivol_dataset` must have at least one item. Got: {sivol_dataset}")
        for datafile in sivol_dataset:
            if not isinstance(datafile, str):
                raise TypeError(f"(calc_siconc) Each item in `sivol_dataset` list must be a string. Got: {type(datafile)}")
            # Verify this is a valid path
            datafile = verify_path(datafile)
            if not datafile.endswith('.nc'):
                raise TypeError(f"(calc_siconc) `datafile` must be a `.nc` filepath. Got: {datafile}")
        # Load all the files at once
        sivol_dataset = xr.open_mfdataset(sivol_dataset)
    elif not isinstance(sivol_dataset, (str, xr.Dataset, xr.DataArray)):
        raise TypeError(f"(calc_siconc) `sivol_dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(sivol_dataset)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(calc_siconc) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.nc' in save_as:
        raise TypeError(f"(calc_siconc) `save_as` must be a `.nc` filepath. Got: {save_as}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(calc_siconc) `verbose` must be a `bool`. Got type: {type(verbose)}")
    
    # Information to output
    if verbose:
        print(f"(calc_siconc) `save_as`: {save_as}")

    # Verify the `sithick_dataset` dataset contains the `sithick` variable
    # and that the `sivol_dataset` contains the `sivol` variable
    si_datasets = [sithick_dataset, sivol_dataset]
    si_vars = ['sithick', 'sivol']
    for i in range(len(si_datasets)):
        this_dataset = si_datasets[i]
        this_var = si_vars[i]
        if isinstance(this_dataset, xr.Dataset):
            var_name = get_variable_name(this_dataset)
        else:
            var_name = this_dataset.name
        if isinstance(var_name, str):
            if not var_name == this_var:
                raise ValueError(f"(calc_siconc) `{this_var}_dataset` must contain the variable `{this_var}`. Available variable: {var_name}")
        elif isinstance(var_name, type([])):
            if not this_var in var_name:
                raise ValueError(f"(calc_siconc) `{this_var}_dataset` must contain the variable `{this_var}`. Available variables: {var_name}")
        else:
            raise TypeError(f"(calc_siconc) `get_variable_name` returned something other than a string or list: {var_name}")

    # Check to make sure they are the same size data set
    if sithick_dataset.sizes != sivol_dataset.sizes:
        raise ValueError(f"(calc_siconc) `sithick_dataset` and `sivol_dataset` must have the same dimension sizes.\n`sithick_dataset.sizes`: {sithick_dataset.sizes}\n`sivol_dataset.sizes`: {sivol_dataset.sizes}")

    # Create a duplicate dataset to copy attributes
    siconc2_dataset = sithick_dataset.copy()

    # Rename `sithick` in the new dataset to `siconc2`
    siconc2_dataset = siconc2_dataset.rename_vars({'sithick':'siconc2'})

    # Combine the `sithick` and `sivol` datasets to get `siconc2`
    siconc2_dataset['siconc2'] = sivol_dataset['sivol'] / sithick_dataset['sithick'] * 100

    # Modify the attributes of the dataset to reflect the changes
    siconc2_dataset['siconc2'].attrs['standard_name'] = 'sea_ice_area_fraction'
    siconc2_dataset['siconc2'].attrs['long_name'] = f'Recalculated Sea Ice Area Fraction (Ocean Grid)'
    siconc2_dataset['siconc2'].attrs['units'] = '%'
    siconc2_dataset['siconc2'].attrs['comment'] = f'Area fraction of grid cell covered by sea ice calculated by `sivol` / `sithick` * 100'
    siconc2_dataset['siconc2'].attrs['original_name'] = 'siconc2'
    if 'history' in siconc2_dataset['siconc2'].attrs.keys():
        original_history = siconc2_dataset['siconc2'].attrs['history']
    else:
        original_history = ''
    siconc2_dataset['siconc2'].attrs['history'] = f"{get_current_datetime_str()} altered by `seaicecp`: Calculated sea ice concentration by `sivol` / `sithick` * 100. {original_history}"
    if 'history' in siconc2_dataset.attrs.keys():
        original_history = siconc2_dataset.attrs['history']
    else:
        original_history = ''
    siconc2_dataset.attrs['history'] = f"{get_current_datetime_str()} altered by `seaicecp`: Calculated sea ice concentration by `sivol` / `sithick` * 100. {original_history}"

    # Save the modified dataset, if applicable
    if not isinstance(save_as, type(None)):
        # Save the plot to file
        siconc2_dataset.to_netcdf(save_as)
    
    return siconc2_dataset

def make_siconc_files(
    sithick_files: [str],
    sivol_files: [str],
    map_bbox: [float, float, float, float] = None,
    version_id: str = 'v20260617',
    overwrite: bool = False,
    **kwargs,
):
    """ Make sea ice concentration files based on the lists of files given.

        For each given pair of files, load the data, trim the datasets (if applicable), calculate the sea ice concentration, then save the sea ice concentration dataset as a new file in the same directory structure. 

        Parameters
        ----------
        sithick_files : List of `str`
            A list of paths of the sea ice thickness data files. 
        sivol_files : List of `str`
            A list of paths of the sea ice volume data files. 
        map_bbox : Array of `float`, `None`, optional
            An array of coordinates defining the bounding box of the map in the following format:
                - [LAT_MAX, LAT_MIN, LON_MAX, LON_MIN]
                
            Default is `None`, meaning the data will not be trimmed.
        version_id : `str`, optional
            The version ID to use when making the directory structure for the sea ice concentration files.
            Default is `'v20260617'`.
        overwrite : `bool`, optional
            Whether to overwrite an existing file if it exists.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `trim_latlon()`, and `calc_siconc()`.

        Returns
        -------
        None
        
        Examples
        --------
        >>> from seaicecp.path import list_variable_files
        >>> from seaicecp.analysis import make_siconc_files
        >>> from seaicecp.params import CAA_BBOX
        >>> this_model = 'EC-Earth3P-HR'
        >>> for this_variant_label in [
        >>>     'r1i1p2f1', 
        >>>     'r2i1p2f1', 
        >>>     'r3i1p2f1',
        >>> ]:
        >>>     for this_experiment in ['hist-1950']:#, 'highres-future']:
        >>>         sithick_list = list_variable_files(
        >>>             source_id = this_model,
        >>>             variable_id = 'sithick',
        >>>             experiment_id = this_experiment,
        >>>             variant_label = this_variant_label,
        >>>         )
        >>>         sivol_list = list_variable_files(
        >>>             source_id = this_model,
        >>>             variable_id = 'sivol',
        >>>             experiment_id = this_experiment,
        >>>             variant_label = this_variant_label,
        >>>         )
        >>>         make_siconc_files(
        >>>             sithick_files = sithick_list,
        >>>             sivol_files = sivol_list,
        >>>             map_bbox = CAA_BBOX,
        >>>             precise_trim = False,
        >>>         )
        (make_siconc_files) Writing file `/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc2/gn/v20260617/trim_CAA_siconc2_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc`.
        (make_siconc_files) Writing file `/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc2/gn/v20260617/trim_CAA_siconc2_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195101-195112.nc`.
        (make_siconc_files) Writing file `/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc2/gn/v20260617/trim_CAA_siconc2_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195201-195212.nc`.
        ...
        (make_siconc_files) Writing file `/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/siconc2/gn/v20260617/trim_CAA_siconc2_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201201-201212.nc`.
        (make_siconc_files) Writing file `/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/siconc2/gn/v20260617/trim_CAA_siconc2_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201301-201312.nc`.
        (make_siconc_files) Writing file `/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/siconc2/gn/v20260617/trim_CAA_siconc2_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201401-201412.nc`.
    """
    # Verify input arguments
    if isinstance(sithick_files, str):
        sithick_files = [sithick_files]
    elif not isinstance(sithick_files, type([])):
        raise TypeError(f"(make_siconc_files) `sithick_files` must be a list. Got type: {type(sithick_files)}")
    for item in sithick_files:
        if not isinstance(item, str):
            raise TypeError(f"(make_siconc_files) `sithick_files` must be a list of strings. Got type: {type(item)} for item {item}")
    if isinstance(sivol_files, str):
        sivol_files = [sivol_files]
    elif not isinstance(sivol_files, type([])):
        raise TypeError(f"(make_siconc_files) `sivol_files` must be a list. Got type: {type(sivol_files)}")
    for item in sivol_files:
        if not isinstance(item, str):
            raise TypeError(f"(make_siconc_files) `sivol_files` must be a list of strings. Got type: {type(item)} for item {item}")
    if len(sithick_files) != len(sivol_files):
        raise ValueError(f"(make_siconc_files) `sithick_files` and `sivol_files` must be the same length. Got `len(sithick_files)`: {len(sithick_files)}, `len(sivol_files)`: {len(sivol_files)}")
    if isinstance(map_bbox, type([])):
        if not len(map_bbox) == 4:
            raise ValueError(f"(make_siconc_files) `map_bbox` must have a length of 4. Got length: {len(map_bbox)}")
        else: 
            for i in range(len(map_bbox)):
                if not isinstance(map_bbox[i], (int, float)):
                    raise TypeError(f"(make_siconc_files) `map_bbox[{i}]` must be a number. Got type: {type(map_bbox[i])}")
    elif not isinstance(map_bbox, (type(None), type([]))):
        raise TypeError(f"(make_siconc_files) `map_bbox` must be a list or `None`. Got type: {type(map_bbox)}")
    if not isinstance(version_id, str):
        raise TypeError(f"(make_siconc_files) `version_id` must be a string. Got type: {type(version_id)}")
    if not isinstance(overwrite, bool):
        raise TypeError(f"(make_siconc_files) `overwrite` must be a `bool`. Got type: {type(overwrite)}")

    # Loop across each file in the list
    for i in range(len(sithick_files)):
        # Verify the filepaths exist
        sithick_filepath = verify_path(sithick_files[i])
        sivol_filepath = verify_path(sivol_files[i])
        # Verify the filepaths are for the same model run
        sithick_filestem = sithick_filepath.replace('sithick', '')
        sivol_filestem = sivol_filepath.replace('sivol', '')
        if sithick_filestem != sivol_filestem:
            raise ValueError(f"(make_siconc_files) `sithick` and `sivol` files for index i={i} are not from the same run\n`sithick_filepath`: {sithick_filepath}\n`sivol_filepath`:{sivol_filepath}")
        # Get the version ID to replace
        replace_this_version_ID = sithick_filepath.split('/')[-2]
        # Assemble the sea ice concentration filename
        siconc2_filepath = sithick_filepath.replace(replace_this_version_ID, version_id)
        siconc2_filepath = siconc2_filepath.replace('sithick', 'siconc2')
        # Add trimming prefix, if applicable
        if not isinstance(map_bbox, type(None)):
            if map_bbox == sps.CAA_BBOX:
                trim_prefix = 'trim_CAA_'
            elif map_bbox == sps.NWP_BBOX:
                trim_prefix = 'trim_NWP_'
            else:
                trim_prefix = 'trim_'
            siconc2_filename = siconc2_filepath.split('/')[-1]
            siconc2_filepath = siconc2_filepath.replace(siconc2_filename, f"{trim_prefix}{siconc2_filename}")
        # Make sure the directory exists
        make_file_path(siconc2_filepath)
        # Check whether the file exists
        try:
            verify_path(siconc2_filepath)
            if overwrite == False:
                warnings.warn(f"(make_siconc_files) File `{siconc2_filepath}` exists already. To overwrite this file, set `overwrite` to `True`.", UserWarning)
                continue
            else:
                print(f"\t(make_siconc_files) Overwriting file `{siconc2_filepath}`.")
        except (FileNotFoundError):
            print(f"\t(make_siconc_files) Writing file `{siconc2_filepath}`.")
        # Load `sithick` and `sivol` files with `xarray`
        sithick_xr = xr.open_dataset(sithick_filepath)
        sivol_xr = xr.open_dataset(sivol_filepath)
        # Trim the `sithick` and `sivol` datasets, if 
        if not isinstance(map_bbox, type(None)):
            sithick_xr = trim_latlon(
                xr_data = sithick_xr,
                map_bbox = map_bbox,
                **kwargs,
            )
            sivol_xr = trim_latlon(
                xr_data = sivol_xr,
                map_bbox = map_bbox,
                **kwargs,
            )
        # Calculate the sea ice concentration ice and save to file
        calc_siconc(
            sithick_dataset = sithick_xr,
            sivol_dataset = sivol_xr,
            save_as = siconc2_filepath,
            **kwargs,
        )

    return None

