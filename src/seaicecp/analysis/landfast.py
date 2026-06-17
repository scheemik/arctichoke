import numpy as np
import xarray as xr
from cdo import Cdo
cdo = Cdo()
# Set path for temporary files in case of a crash
cdo = Cdo(tempdir='./cdo_tmp/')
cdo.cleanTempDir()

from seaicecp.verify import verify_path
from seaicecp.dataset.get_variable import get_variable_name

def find_packed_ice(
    dataset: (str, [str], xr.DataArray, xr.Dataset),
    packed_threshold = 85, 
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
            The file name to pass to `cdo.setrtoc2(output=save_as)`.
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
            output = save_as,
        )

    # Rename `siconc` in the new dataset to `sipacked`
    return packedice_xr.rename_vars({'siconc':'sipacked'})

def find_slow_ice(
    dataset: (str, [str], xr.DataArray, xr.Dataset),
    slow_threshold = 0.01, 
    save_as: str = None,
    verbose: bool = False,
    **kwargs,
):
    """ Calculate where slow ice is from the dataset.

        Verify the dataset contains the `sispeed` variable, and adds a variable `sislow` which is 1 where `sispeed` is less than 1 cm/s (or the given threshold) and 0 elsewhere.

        Parameters
        ----------
        dataset : `str`, list of `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset of which to find the locations of slow ice.
        slow_threshold : `int`, `float`, optional
            The threshold above which to mark slow ice.
            Default is `0.01` m/s, following Laliberté et al. 2018.
        save_as : `str`, `None`, optional
            The file name to pass to `cdo.setrtoc2(output=save_as)`.
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
            output = save_as,
        )

    # Rename `sispeed` in the new dataset to `sislow`
    return slowice_xr.rename_vars({'sispeed':'sislow'})

def find_landfast_ice(
    siconc_dataset: (str, [str], xr.DataArray, xr.Dataset),
    sispeed_dataset: (str, [str], xr.DataArray, xr.Dataset),
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
        save_as : `str`, `None`, optional
            The file name to pass to `cdo.setrtoc2(output=save_as)`.
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
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(find_landfast_ice) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.nc' in save_as:
        raise TypeError(f"(find_landfast_ice) `save_as` must be a `.nc` filepath. Got: {save_as}")
    
    # Information to output
    if verbose:
        print(f"(find_landfast_ice) `save_as`: {save_as}")

    # Find the packed and slow ice
    dataset_sipacked = find_packed_ice(
        dataset=siconc_dataset,
        **kwargs,
    )
    dataset_sislow = find_slow_ice(
        dataset=sispeed_dataset,
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

    # Rename `sipacked` in the new dataset to `silandfast`
    return landfastice_xr.rename_vars({'sipacked':'silandfast'})
