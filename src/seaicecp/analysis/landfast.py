import numpy as np
import xarray as xr
import warnings

from cdo import Cdo
cdo = Cdo()
# Set path for temporary files in case of a crash
cdo = Cdo(tempdir='./cdo_tmp/')
cdo.cleanTempDir()

from seaicecp import get_current_datetime_str
from seaicecp.dataset.get_variable import get_variable_name
from seaicecp.dataset.trim_dataset import trim_latlon
from seaicecp.path.manipulate_paths import make_file_path
import seaicecp.params as sps
from seaicecp.verify import verify_path

def find_packed_ice(
    dataset: (str, [str], xr.DataArray, xr.Dataset),
    packed_threshold: (int, float) = 85, 
    save_as: str = None,
    verbose: bool = False,
    **kwargs,
):
    """ Calculate where packed ice is from the dataset.

        Verify the dataset contains the `siconc` variable, and adds a variable `sipacked` which is 1 where `siconc` is greater than 85 percent (or the given threshold) and 0 elsewhere.

        Parameters
        ----------
        dataset : `str`, list of `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset of which to find the locations of packed ice.
        packed_threshold : `int`, `float`, optional
            The threshold above which to mark packed ice.
            Default is `85` percent, following Laliberté et al. 2018.
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
        packedice_xr : `xarray.Dataset`
            A dataset where packed ice is marked as `1` and all other values are `0`.
        
        Examples
        --------
        >>> from seaicecp.dataset.example_dataset import make_example_dataset
        >>> dataset = make_example_dataset(n=3, test_var_name='siconc')
        >>> dataset['siconc'].values
        array([[0., 1., 2.],
               [3., 4., 5.],
               [6., 7., 8.]])
        >>> from seaicecp.analysis.landfast import find_packed_ice
        >>> dataset_sipacked = find_packed_ice(dataset, packed_threshold=4)
        >>> dataset_sipacked['sipacked'].values
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
            raise ValueError(f"(find_packed_ice) `dataset` must have at least one item. Got: {dataset}")
        # Start variables to add arguments to the `cdo` input command
        input_command_prefix = "[ -setrtoc2,"
        input_command_files = " :"
        for datafile in dataset:
            if not isinstance(datafile, str):
                raise TypeError(f"(find_packed_ice) Each item in `dataset` list must be a string. Got: {type(datafile)}")
            # Verify this is a valid path
            datafile = verify_path(datafile)
            if not datafile.endswith('.nc'):
                raise TypeError(f"(plot_time_series) `datafile` must be a `.nc` filepath. Got: {datafile}")
            input_command_files = f"{input_command_files} {datafile}"
        input_command_files = f"{input_command_files} ]"
        cdo_command = cdo.mergetime
    else:
        raise TypeError(f"(find_packed_ice) `dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(dataset)}")
    if not isinstance(packed_threshold, (int, float)):
        raise TypeError(f"(find_packed_ice) `packed_threshold` must be `int` or `float`. Got type: {type(packed_threshold)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(find_packed_ice) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.nc' in save_as:
        raise TypeError(f"(find_packed_ice) `save_as` must be a `.nc` filepath. Got: {save_as}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(find_packed_ice) `verbose` must be a `bool`. Got type: {type(verbose)}")

    # Verify the dataset(s) contain(s) the `siconc` variable
    for this_dataset in var_check_list:
        var_name = get_variable_name(this_dataset)
        if isinstance(var_name, str):
            if not var_name == 'siconc':
                raise ValueError(f"(find_packed_ice) `this_dataset` must contain the variable `siconc`. Available variables: {var_name}")
        elif isinstance(var_name, type([])):
            if not 'siconc' in var_name:
                raise ValueError(f"(find_packed_ice) `this_dataset` must contain the variable `siconc`. Available variables: {var_name}")
        else:
            raise TypeError(f"(find_packed_ice) `get_variable_name` returned something other than a string or list: {var_name}")
    
    # Information to output
    if verbose:
        print(f"(find_packed_ice) `save_as`: {save_as}")

    # Get the maximum possible integer to cover all reasonable values of `siconc`
    numpy_int32_max = np.iinfo(np.int32).max

    # Assemble the string to specify the range and the output values
    range_min = packed_threshold
    range_max = numpy_int32_max
    val_inside_range = 1
    val_outside_range = 0
    range_string = f"{range_min},{range_max},{val_inside_range},{val_outside_range}"

    # Create a new dataset for `sipacked`, packed ice
    if isinstance(dataset, (xr.Dataset, xr.DataArray)):
        if verbose:
            print(f"(find_packed_ice) `input_command`: cdo setrtoc2,{range_string} dataset")
        # If only processing one `xr.Dataset`, the `input` argument cannot include the range string
        packedice_xr = cdo_command(
            range_string,
            input=dataset, 
            returnXDataset='sipacked'
        )
    else:
        # Assemble the `cdo` input command to pass to `mergetime`
        input_command = f"{input_command_prefix}{range_string}{input_command_files}"
        if verbose:
            print(f"(find_packed_ice) `input_command`: {input_command}")
        packedice_xr = cdo_command(
            input = input_command,
            returnXDataset = 'sipacked',
        )

    # Rename `siconc` in the new dataset to `sipacked`
    packedice_xr = packedice_xr.rename_vars({'siconc':'sipacked'})

    # Modify the attributes of the dataset to reflect the changes
    packedice_xr['sipacked'].attrs['standard_name'] = 'sea_ice_packed_marker'
    packedice_xr['sipacked'].attrs['long_name'] = f'Sea Ice Concentration > {packed_threshold}%'
    packedice_xr['sipacked'].attrs['units'] = '1: Yes, 0: No'
    packedice_xr['sipacked'].attrs['comment'] = f'Marker of packed ice, where sea ice concentration (`siconc`) >{packed_threshold}%'
    packedice_xr['sipacked'].attrs['original_name'] = 'sipacked'
    if 'history' in packedice_xr['sipacked'].attrs.keys():
        original_history = packedice_xr['sipacked'].attrs['history']
    else:
        original_history = ''
    packedice_xr['sipacked'].attrs['history'] = f"{get_current_datetime_str()} altered by `seaicecp`: Calculated packed ice, marking `siconc` > {packed_threshold} as 1 and 0 otherwise. {original_history}"
    if 'history' in packedice_xr.attrs.keys():
        original_history = packedice_xr.attrs['history']
    else:
        original_history = ''
    packedice_xr.attrs['history'] = f"{get_current_datetime_str()} altered by `seaicecp`: Calculated packed ice, marking `siconc` > {packed_threshold} as 1 and 0 otherwise. {original_history}"

    # Save the modified dataset, if applicable
    if not isinstance(save_as, type(None)):
        # Save the plot to file
        packedice_xr.to_netcdf(save_as)
    
    return packedice_xr

def find_slow_ice(
    dataset: (str, [str], xr.DataArray, xr.Dataset),
    slow_threshold: (int, float) = 0.01, 
    save_as: str = None,
    verbose: bool = False,
    **kwargs,
):
    """ Calculate where slow ice is from the dataset.

        Verify the dataset contains the `sispeed` variable, and adds a variable `sislow` which is 1 where `sispeed` is less than 1 cm s-1 (or the given threshold) and 0 elsewhere.

        Parameters
        ----------
        dataset : `str`, list of `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset of which to find the locations of slow ice.
        slow_threshold : `int`, `float`, optional
            The threshold above which to mark slow ice.
            Default is `0.01` m s-1, following Laliberté et al. 2018.
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
        slowice_xr : `xarray.Dataset`
            A dataset where slow ice is marked as `1` and all other values are `0`.
        
        Examples
        --------
        >>> from seaicecp.dataset.example_dataset import make_example_dataset
        >>> dataset = make_example_dataset(n=3, test_var_name='sispeed')
        >>> dataset['sispeed'].values
        array([[0., 1., 2.],
               [3., 4., 5.],
               [6., 7., 8.]])
        >>> from seaicecp.analysis.landfast import find_slow_ice
        >>> dataset_sislow = find_slow_ice(dataset, slow_threshold=4)
        >>> dataset_sislow['sislow'].values
        array([[1., 1., 1.],
               [1., 1., 0.],
               [0., 0., 0.]])
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
            raise ValueError(f"(find_slow_ice) `dataset` must have at least one item. Got: {dataset}")
        # Start variables to add arguments to the `cdo` input command
        input_command_prefix = "[ -setrtoc2,"
        input_command_files = " :"
        for datafile in dataset:
            if not isinstance(datafile, str):
                raise TypeError(f"(find_slow_ice) Each item in `dataset` list must be a string. Got: {type(datafile)}")
            # Verify this is a valid path
            datafile = verify_path(datafile)
            if not datafile.endswith('.nc'):
                raise TypeError(f"(plot_time_series) `datafile` must be a `.nc` filepath. Got: {datafile}")
            input_command_files = f"{input_command_files} {datafile}"
        input_command_files = f"{input_command_files} ]"
        cdo_command = cdo.mergetime
    else:
        raise TypeError(f"(find_slow_ice) `dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(dataset)}")
    if not isinstance(slow_threshold, (int, float)):
        raise TypeError(f"(find_slow_ice) `slow_threshold` must be `int` or `float`. Got type: {type(slow_threshold)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(find_slow_ice) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.nc' in save_as:
        raise TypeError(f"(find_slow_ice) `save_as` must be a `.nc` filepath. Got: {save_as}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(find_slow_ice) `verbose` must be a `bool`. Got type: {type(verbose)}")

    # Verify the dataset(s) contain(s) the `sispeed` variable
    for this_dataset in var_check_list:
        var_name = get_variable_name(this_dataset)
        if isinstance(var_name, str):
            if not var_name == 'sispeed':
                raise ValueError(f"(find_slow_ice) `this_dataset` must contain the variable `sispeed`. Available variables: {var_name}")
        elif isinstance(var_name, type([])):
            if not 'sispeed' in var_name:
                raise ValueError(f"(find_slow_ice) `this_dataset` must contain the variable `sispeed`. Available variables: {var_name}")
        else:
            raise TypeError(f"(find_slow_ice) `get_variable_name` returned something other than a string or list: {var_name}")
    
    # Information to output
    if verbose:
        print(f"(find_slow_ice) `save_as`: {save_as}")

    # Get the minimum possible integer to cover all reasonable values of `sispeed`
    numpy_int32_min = np.iinfo(np.int32).min

    # Assemble the string to specify the range and the output values
    range_min = numpy_int32_min
    range_max = slow_threshold
    val_inside_range = 1
    val_outside_range = 0
    range_string = f"{range_min},{range_max},{val_inside_range},{val_outside_range}"

    # Create a new dataset for `sislow`, slow ice
    if isinstance(dataset, (xr.Dataset, xr.DataArray)):
        if verbose:
            print(f"(find_slow_ice) `input_command`: cdo setrtoc2,{range_string} dataset")
        # If only processing one `xr.Dataset`, the `input` argument cannot include the range string
        slowice_xr = cdo_command(
            range_string,
            input=dataset, 
            returnXDataset='sislow'
        )
    else:
        # Assemble the `cdo` input command to pass to `mergetime`
        input_command = f"{input_command_prefix}{range_string}{input_command_files}"
        if verbose:
            print(f"(find_slow_ice) `input_command`: {input_command}")
        slowice_xr = cdo_command(
            input = input_command,
            returnXDataset = 'sislow',
        )

    # Rename `sispeed` in the new dataset to `sislow`
    slowice_xr = slowice_xr.rename_vars({'sispeed':'sislow'})

    # Modify the attributes of the dataset to reflect the changes
    slowice_xr['sislow'].attrs['standard_name'] = 'sea_ice_slow_marker'
    slowice_xr['sislow'].attrs['long_name'] = f'Speed of Ice < {slow_threshold} m s-1'
    slowice_xr['sislow'].attrs['units'] = '1: Yes, 0: No'
    slowice_xr['sislow'].attrs['comment'] = f'Marker of slow ice, where sea ice speed (`sispeed`) <{slow_threshold} m s-1'
    slowice_xr['sislow'].attrs['original_name'] = 'sislow'
    if 'history' in slowice_xr['sislow'].attrs.keys():
        original_history = slowice_xr['sislow'].attrs['history']
    else:
        original_history = ''
    slowice_xr['sislow'].attrs['history'] = f"{get_current_datetime_str()} altered by `seaicecp`: Calculated slow ice, marking `sispeed` > {slow_threshold} as 1 and 0 otherwise. {original_history}"
    if 'history' in slowice_xr.attrs.keys():
        original_history = slowice_xr.attrs['history']
    else:
        original_history = ''
    slowice_xr.attrs['history'] = f"{get_current_datetime_str()} altered by `seaicecp`: Calculated slow ice, marking `sispeed` > {slow_threshold} as 1 and 0 otherwise. {original_history}"

    # Save the modified dataset, if applicable
    if not isinstance(save_as, type(None)):
        # Save the plot to file
        slowice_xr.to_netcdf(save_as)
    
    return slowice_xr

def find_landfast_ice(
    siconc_dataset: (str, [str], xr.DataArray, xr.Dataset),
    sispeed_dataset: (str, [str], xr.DataArray, xr.Dataset),
    packed_threshold: (int, float) = 85, 
    slow_threshold: (int, float) = 0.01, 
    save_as: str = None,
    verbose: bool = False,
    **kwargs,
):
    """ Calculate where landfast ice is from the dataset(s).

        Verify the dataset(s) contains the `siconc` and `sispeed` variables, calculates `sipacked` and `sislow` using `find_packed_ice()` and `find_landfast_ice()`, then takes the overlap of these to define `silandfast`.

        Parameters
        ----------
        siconc_dataset : `str`, list of `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset of which to find the locations of landfast ice that contains `siconc`.
        sispeed_dataset : `str`, list of `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset of which to find the locations of landfast ice that contains `sispeed`.
        packed_threshold : `int`, `float`, optional
            The threshold above which to mark packed ice.
            Default is `85` percent, following Laliberté et al. 2018.
        slow_threshold : `int`, `float`, optional
            The threshold above which to mark slow ice.
            Default is `0.01` m s-1, following Laliberté et al. 2018.
        save_as : `str`, `None`, optional
            The file name to which to save the modified dataset.
            Default is `None`, which doesn't save the dataset to a file.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `find_packed_ice()`, `find_slow_ice()` and `cdo.setrtoc2()`.

        Returns
        -------
        landfastice_xr : `xarray.Dataset`
            A dataset where landfast ice is marked as `1` and all other values are `0`.
        
        Examples
        --------
        >>> from seaicecp.dataset.example_dataset import make_example_dataset
        >>> dataset_0 = make_example_dataset(n=3, test_var_name='siconc')
        >>> dataset_0['siconc'].values
        array([[0., 1., 2.],
               [3., 4., 5.],
               [6., 7., 8.]])
        >>> dataset_1 = make_example_dataset(n=3, test_var_name='sispeed')
        >>> dataset_1['sispeed'].values
        array([[0., 1., 2.],
               [3., 4., 5.],
               [6., 7., 8.]])
        >>> from seaicecp.analysis.landfast import find_landfast_ice
        >>> dataset_landfast = find_landfast_ice(siconc_dataset=dataset_0, sispeed_dataset=dataset_1, packed_threshold=4, slow_threshold=4)
        >>> dataset_landfast['silandfast'].values
        array([[0., 0., 0.],
               [0., 1., 0.],
               [0., 0., 0.]])
    """
    # Verify input arguments
    ## `siconc_dataset` and `sispeed_dataset` are verified by `find_packed_ice()` and `find_slow_ice()`, respectively
    if not isinstance(packed_threshold, (int, float)):
        raise TypeError(f"(find_landfast_ice) `packed_threshold` must be `int` or `float`. Got type: {type(packed_threshold)}")
    if not isinstance(slow_threshold, (int, float)):
        raise TypeError(f"(find_landfast_ice) `slow_threshold` must be `int` or `float`. Got type: {type(slow_threshold)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(find_landfast_ice) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.nc' in save_as:
        raise TypeError(f"(find_landfast_ice) `save_as` must be a `.nc` filepath. Got: {save_as}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(find_landfast_ice) `verbose` must be a `bool`. Got type: {type(verbose)}")
    
    # Information to output
    if verbose:
        print(f"(find_landfast_ice) `save_as`: {save_as}")

    # Find the packed and slow ice
    dataset_sipacked = find_packed_ice(
        dataset = siconc_dataset,
        packed_threshold = packed_threshold,
        **kwargs,
    )
    dataset_sislow = find_slow_ice(
        dataset = sispeed_dataset,
        slow_threshold = slow_threshold,
        **kwargs,
    )

    # Check to make sure they are the same size data set
    if dataset_sipacked.sizes != dataset_sislow.sizes:
        raise ValueError(f"(find_landfast_ice) `siconc_dataset` and `sispeed_dataset` must have the same dimension sizes.\n`siconc_dataset.sizes`: {siconc_dataset.sizes}\n`sispeed_dataset.sizes`: {sispeed_dataset.sizes}")

    # Combine these datasets
    dataset_sipacked['sipacked'] = dataset_sipacked['sipacked'] + dataset_sislow['sislow']

    # Assemble the string to specify the range and the output values
    range_min = 1.5
    range_max = 2.5
    val_inside_range = 1
    val_outside_range = 0
    range_string = f"{range_min},{range_max},{val_inside_range},{val_outside_range}"

    # Create a new dataset for `silandfast`, landfast ice
    if verbose:
        print(f"(find_landfast_ice) `input_command`: cdo setrtoc2,{range_string} dataset")
    # If only processing one `xr.Dataset`, the `input` argument cannot include the range string
    landfastice_xr = cdo.setrtoc2(
        range_string,
        input=dataset_sipacked, 
        returnXDataset='silandfast'
    )
    # # Set 0 as the missing value
    # landfastice_xr = cdo.setmissval(
    #     '0',
    #     input=landfastice_xr, 
    #     returnXDataset='silandfast'
    # )

    # Rename `sipacked` in the new dataset to `silandfast`
    landfastice_xr = landfastice_xr.rename_vars({'sipacked':'silandfast'})

    # Modify the attributes of the dataset to reflect the changes
    landfastice_xr['silandfast'].attrs['standard_name'] = 'sea_ice_landfast_marker'
    landfastice_xr['silandfast'].attrs['long_name'] = f'Landfast Ice (>{packed_threshold}%, <{slow_threshold}m s-1)'
    landfastice_xr['silandfast'].attrs['units'] = '1: Yes, 0: No'
    landfastice_xr['silandfast'].attrs['comment'] = f'Marker of landfast ice, where sea ice concentration (`siconc`) > {packed_threshold}% and sea ice speed (`sispeed`) < {slow_threshold} m s-1'
    landfastice_xr['silandfast'].attrs['original_name'] = 'silandfast'
    if 'history' in landfastice_xr['silandfast'].attrs.keys():
        original_history = landfastice_xr['silandfast'].attrs['history']
    else:
        original_history = ''
    landfastice_xr['silandfast'].attrs['history'] = f"{get_current_datetime_str()} altered by `seaicecp`: Calculated landfast ice, marking where both `siconc` > {packed_threshold} and `sispeed` > {slow_threshold} as 1 and 0 otherwise. {original_history}"
    if 'history' in landfastice_xr.attrs.keys():
        original_history = landfastice_xr.attrs['history']
    else:
        original_history = ''
    landfastice_xr.attrs['history'] = f"{get_current_datetime_str()} altered by `seaicecp`: Calculated landfast ice, marking where both `siconc` > {packed_threshold} and `sispeed` > {slow_threshold} as 1 and 0 otherwise. {original_history}"

    # Save the modified dataset, if applicable
    if not isinstance(save_as, type(None)):
        # Save the plot to file
        landfastice_xr.to_netcdf(save_as)
    
    return landfastice_xr

def make_landfast_files(
    siconc_files: [str],
    sispeed_files: [str],
    map_bbox: [float, float, float, float] = None,
    version_id: str = 'v20260617',
    overwrite: bool = False,
    **kwargs,
):
    """ Make landfast files based on the lists of files given.

        For each given pair of files, load the data, trim the datasets (if applicable), calculate the landfast ice, then save the landfast ice dataset as a new file in the same directory structure. 

        Parameters
        ----------
        siconc_files : List of `str`
            A list of paths of the sea ice concentration data files. 
        sispeed_files : List of `str`
            A list of paths of the sea ice speed data files. 
        map_bbox : Array of `float`, `None`, optional
            An array of coordinates defining the bounding box of the map in the following format:
                - [LAT_MAX, LAT_MIN, LON_MAX, LON_MIN]
                
            Default is `None`, meaning the data will not be trimmed.
        version_id : `str`, optional
            The version ID to use when making the directory structure for the landfast ice files.
            Default is `'v20260617'`.
        overwrite : `bool`, optional
            Whether to overwrite an existing file if it exists.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `trim_latlon()`, and `find_landfast_ice()`.

        Returns
        -------
        None
        
        Examples
        --------
        >>> from seaicecp.path import list_variable_files
        >>> from seaicecp.analysis.landfast import make_landfast_files
        >>> from seaicecp.params import CAA_BBOX
        >>> this_model = 'EC-Earth3P-HR'
        >>> for this_variant_label in [
        >>>     'r1i1p2f1', 
        >>>     'r2i1p2f1', 
        >>>     'r3i1p2f1',
        >>> ]:
        >>>     for this_experiment in ['hist-1950']:#, 'highres-future']:
        >>>         siconc_list = list_variable_files(
        >>>             source_id = this_model,
        >>>             variable_id = 'siconc',
        >>>             experiment_id = this_experiment,
        >>>             variant_label = this_variant_label,
        >>>         )
        >>>         sispeed_list = list_variable_files(
        >>>             source_id = this_model,
        >>>             variable_id = 'sispeed',
        >>>             experiment_id = this_experiment,
        >>>             variant_label = this_variant_label,
        >>>         )
        >>>         make_landfast_files(
        >>>             siconc_files = siconc_list,
        >>>             sispeed_files = sispeed_list,
        >>>             map_bbox = CAA_BBOX,
        >>>             precise_trim = False,
        >>>         )
        (make_landfast_files) Writing file `/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/silandfast/gn/v20260617/trim_CAA_silandfast_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc`.
        (make_landfast_files) Writing file `/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/silandfast/gn/v20260617/trim_CAA_silandfast_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195101-195112.nc`.
        (make_landfast_files) Writing file `/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/silandfast/gn/v20260617/trim_CAA_silandfast_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195201-195212.nc`.
        ...
        (make_landfast_files) Writing file `/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/silandfast/gn/v20260617/trim_CAA_silandfast_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201201-201212.nc`.
        (make_landfast_files) Writing file `/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/silandfast/gn/v20260617/trim_CAA_silandfast_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201301-201312.nc`.
        (make_landfast_files) Writing file `/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/silandfast/gn/v20260617/trim_CAA_silandfast_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201401-201412.nc`.
    """
    # Verify input arguments
    if isinstance(siconc_files, str):
        siconc_files = [siconc_files]
    elif not isinstance(siconc_files, type([])):
        raise TypeError(f"(make_landfast_files) `siconc_files` must be a list. Got type: {type(siconc_files)}")
    for item in siconc_files:
        if not isinstance(item, str):
            raise TypeError(f"(make_landfast_files) `siconc_files` must be a list of strings. Got type: {type(item)} for item {item}")
    if isinstance(sispeed_files, str):
        sispeed_files = [sispeed_files]
    elif not isinstance(sispeed_files, type([])):
        raise TypeError(f"(make_landfast_files) `sispeed_files` must be a list. Got type: {type(sispeed_files)}")
    for item in sispeed_files:
        if not isinstance(item, str):
            raise TypeError(f"(make_landfast_files) `sispeed_files` must be a list of strings. Got type: {type(item)} for item {item}")
    if len(siconc_files) != len(sispeed_files):
        raise ValueError(f"(make_landfast_files) `siconc_files` and `sispeed_files` must be the same length. Got `len(siconc_files)`: {len(siconc_files)}, `len(sispeed_files)`: {len(sispeed_files)}")
    if isinstance(map_bbox, type([])):
        if not len(map_bbox) == 4:
            raise ValueError(f"(make_landfast_files) `map_bbox` must have a length of 4. Got length: {len(map_bbox)}")
        else: 
            for i in range(len(map_bbox)):
                if not isinstance(map_bbox[i], (int, float)):
                    raise TypeError(f"(make_landfast_files) `map_bbox[{i}]` must be a number. Got type: {type(map_bbox[i])}")
    elif not isinstance(map_bbox, (type(None), type([]))):
        raise TypeError(f"(make_landfast_files) `map_bbox` must be a list or `None`. Got type: {type(map_bbox)}")
    if not isinstance(version_id, str):
        raise TypeError(f"(make_landfast_files) `version_id` must be a string. Got type: {type(version_id)}")
    if not isinstance(overwrite, bool):
        raise TypeError(f"(make_landfast_files) `overwrite` must be a `bool`. Got type: {type(overwrite)}")

    # Loop across each file in the list
    for i in range(len(siconc_files)):
        # Verify the filepaths exist
        siconc_filepath = verify_path(siconc_files[i])
        sispeed_filepath = verify_path(sispeed_files[i])
        # Verify the filepaths are for the same model run
        siconc_filestem = siconc_filepath.replace('siconc', '')
        sispeed_filestem = sispeed_filepath.replace('sispeed', '')
        if siconc_filestem != sispeed_filestem:
            raise ValueError(f"(make_landfast_files) `siconc` and `sispeed` files for index i={i} are not from the same run\n`siconc_filepath`: {siconc_filepath}\n`sispeed_filepath`:{sispeed_filepath}")
        # Get the version ID to replace
        replace_this_version_ID = siconc_filepath.split('/')[-2]
        # Assemble the landfast filename
        landfast_filepath = siconc_filepath.replace(replace_this_version_ID, version_id)
        landfast_filepath = landfast_filepath.replace('siconc', 'silandfast')
        # Add trimming prefix, if applicable
        if not isinstance(map_bbox, type(None)):
            if map_bbox == sps.CAA_BBOX:
                trim_prefix = 'trim_CAA_'
            elif map_bbox == sps.NWP_BBOX:
                trim_prefix = 'trim_NWP_'
            else:
                trim_prefix = 'trim_'
            landfast_filename = landfast_filepath.split('/')[-1]
            landfast_filepath = landfast_filepath.replace(landfast_filename, f"{trim_prefix}{landfast_filename}")
        # Make sure the directory exists
        make_file_path(landfast_filepath)
        # Check whether the file exists
        try:
            verify_path(landfast_filepath)
            if overwrite == False:
                warnings.warn(f"(make_landfast_files) File `{landfast_filepath}` exists already. To overwrite this file, set `overwrite` to `True`.", UserWarning)
                continue
            else:
                print(f"\t(make_landfast_files) Overwriting file `{landfast_filepath}`.")
        except (FileNotFoundError):
            print(f"\t(make_landfast_files) Writing file `{landfast_filepath}`.")
        # Load `siconc` and `sispeed` files with `xarray`
        siconc_xr = xr.open_dataset(siconc_filepath)
        sispeed_xr = xr.open_dataset(sispeed_filepath)
        # Trim the `siconc` and `sispeed` datasets, if 
        if not isinstance(map_bbox, type(None)):
            siconc_xr = trim_latlon(
                xr_data = siconc_xr,
                map_bbox = map_bbox,
                **kwargs,
            )
            sispeed_xr = trim_latlon(
                xr_data = sispeed_xr,
                map_bbox = map_bbox,
                **kwargs,
            )
        # Calculate the landfast ice and save to file
        find_landfast_ice(
            siconc_dataset = siconc_xr,
            sispeed_dataset = sispeed_xr,
            save_as = landfast_filepath,
            **kwargs,
        )

    return None

