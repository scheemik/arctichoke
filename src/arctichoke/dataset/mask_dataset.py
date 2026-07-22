import numpy as np
import xarray as xr
import warnings

from cdo import Cdo
cdo = Cdo()
# Set path for temporary files in case of a crash
cdo = Cdo(tempdir='./cdo_tmp/')
cdo.cleanTempDir()

from arctichoke import get_current_datetime_str
from arctichoke.dataset.get_variable import get_variable_name
from arctichoke.dataset.trim_dataset import trim_latlon
from arctichoke.path.manipulate_paths import make_file_path
import arctichoke.params as sps
from arctichoke.verify import verify_path

def make_mask(
    dataset: (str, [str], xr.DataArray, xr.Dataset),
    var: str = None,
    mask_var_name: str = None,
    mask_this_val: (int, float) = None,
    mask_this_range: [(int, float), (int, float)] = None,
    val_inside_range: (int, float) = 0,
    val_outside_range: (int, float) = 1,
    add_mask_attrs: bool = True,
    save_as: str = None,
    verbose: bool = False,
    **kwargs,
):
    """ Make a mask based on the given dataset and parameters.

        Verify the dataset contains the specified variable and creates a mask. 
        This masks out the specified value or range of values, setting them equal to `val_inside_range` and every other value to `val_outside_range`.

        Parameters
        ----------
        dataset : `str`, list of `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset from which to create a mask.
        var : `str`, `None`, optional
            The name of the variable from which to create a mask.
            Default is `None`.
        mask_var_name : `str`, `None`, optional
            The name to give to the new mask variable.
            If `None` is given, the new name will simply append `_mask` to `var`.
            Default is `None`.
        mask_this_val : `int`, `float`, `None`, optional
            The value to mask out.
            If an option is given here, then `mask_this_range` must be `None`.
            Default is `None`.
        mask_this_range : list of `int` or `float`, `None`, optional
            The range of values to mask out.
            Must be of length 2, order does not matter.
            If an option is given here, then `mask_this_val` must be `None`.
            Default is `None`.
        val_inside_range : `int`, `float`, optional
            The value to assign to the masked out values.
            Default is `0`.
        val_outside_range : `int`, `float`, optional
            The value to assign to values that are not masked out.
            Default is `1`.
        add_mask_attrs : `bool`, optional
            Whether to call `add_mask_attributes()` to modify the attributes of the dataset to reflect the fact a mask has been made.
            Default is `True`.
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
        mask_xr : `xarray.Dataset`
            A dataset where mask values are marked as `val_inside_range` and all other values are `val_outside_range`.
        
        Examples
        --------
        >>> from arctichoke.dataset import make_example_dataset
        >>> dataset = make_example_dataset(n=3)
        >>> dataset['test_var'].values
        array([[0., 1., 2.],
               [3., 4., 5.],
               [6., 7., 8.]])
        >>> from arctichoke.dataset import make_mask
        >>> dataset_masked = make_mask(dataset, var='test_var', mask_this_range=[0,4])
        >>> dataset_masked['test_var_mask'].values
        array([[0., 0., 0.],
               [0., 0., 1.],
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
            raise ValueError(f"(make_mask) `dataset` must have at least one item. Got: {dataset}")
        # Start variables to add arguments to the `cdo` input command
        input_command_prefix = "[ -setrtoc2,"
        input_command_files = " :"
        for datafile in dataset:
            if not isinstance(datafile, str):
                raise TypeError(f"(make_mask) Each item in `dataset` list must be a string. Got: {type(datafile)}")
            # Verify this is a valid path
            datafile = verify_path(datafile)
            if not datafile.endswith('.nc'):
                raise TypeError(f"(make_mask) `datafile` must be a `.nc` filepath. Got: {datafile}")
            input_command_files = f"{input_command_files} {datafile}"
        input_command_files = f"{input_command_files} ]"
        cdo_command = cdo.mergetime
    else:
        raise TypeError(f"(make_mask) `dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(dataset)}")
    if not isinstance(var, (str, type(None))):
        raise TypeError(f"(make_mask) `var` must be a string or `None`. Got type: {type(var)}")
    if not isinstance(mask_var_name, (str, type(None))):
        raise TypeError(f"(make_mask) `mask_var_name` must be a string or `None`. Got type: {type(mask_var_name)}")
    if not isinstance(mask_this_val, (int, float, type(None))):
        raise TypeError(f"(make_mask) `mask_this_val` must be `int`, `float`, or `None`. Got type: {type(mask_this_val)}")
    if isinstance(mask_this_range, type([])):
        if len(mask_this_range) != 2:
            raise TypeError(f"(make_mask) `mask_this_range` must be a list of length 2. Got length: {len(mask_this_range)}")
        else:
            for mask_range_val in mask_this_range:
                if not isinstance(mask_range_val, (int, float)):
                    raise TypeError(f"(make_mask) Values of `mask_this_range` must be `int` or `float`. Got type: {type(mask_range_val)}")
    elif not isinstance(mask_this_range, (type([]), type(None))):
        raise TypeError(f"(make_mask) `mask_this_range` must be a list or `None`. Got type: {type(mask_this_range)}")
    if not isinstance(val_inside_range, (int, float)):
        raise TypeError(f"(make_mask) `val_inside_range` must be `int` or `float`. Got type: {type(val_inside_range)}")
    if not isinstance(val_outside_range, (int, float)):
        raise TypeError(f"(make_mask) `val_outside_range` must be `int` or `float`. Got type: {type(val_outside_range)}")
    if not isinstance(add_mask_attrs, bool):
        raise TypeError(f"(make_mask) `add_mask_attrs` must be a `bool`. Got type: {type(add_mask_attrs)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(make_mask) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.nc' in save_as:
        raise TypeError(f"(make_mask) `save_as` must be a `.nc` filepath. Got: {save_as}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(make_mask) `verbose` must be a `bool`. Got type: {type(verbose)}")

    # Verify the dataset(s) contain(s) the specified variable
    for this_dataset in var_check_list:
        var_name = get_variable_name(this_dataset)
        if isinstance(var_name, str):
            if not var_name == var:
                raise ValueError(f"(make_mask) `this_dataset` must contain the variable `{var}`. Available variables: {var_name}")
        elif isinstance(var_name, type([])):
            if not siconc_var in var_name:
                raise ValueError(f"(make_mask) `this_dataset` must contain the variable `{var}`. Available variables: {var_name}")
        else:
            raise TypeError(f"(make_mask) `get_variable_name` returned something other than a string or list: {var_name}")
    
    # Assemble new mask variable name, if applicable
    if isinstance(mask_var_name, type(None)):
        mask_var_name = f'{var}_mask'
    
    # Information to output
    if verbose:
        print(f"(make_mask) `save_as`: {save_as}")

    
    # See whether to mask a value or range
    if isinstance(mask_this_val, type(None)):
        val_mask = False
    else:
        val_mask = True 
    if isinstance(mask_this_range, type(None)):
        range_mask = False 
    else:
        range_mask = True 
    if val_mask == range_mask:
        raise ValueError(f"(make_mask) One and only one of `mask_this_val` ({mask_this_val}) and `mask_this_range` ({mask_this_range}) must be specified at a time.")
    elif val_mask:
        # Get the smallest possible float to cover a range that basically only encompasses the value of `mask_this_val`
        numpy_float64_epsilon = np.finfo(np.float64).eps
        range_min = mask_this_val - numpy_float64_epsilon
        range_max = mask_this_val + numpy_float64_epsilon
    elif range_mask:
        range_min = min(mask_this_range)
        range_max = max(mask_this_range)

    # Assemble the string to specify the range and the output values
    range_string = f"{range_min},{range_max},{val_inside_range},{val_outside_range}"

    # Create a new dataset for the mask
    if isinstance(dataset, (xr.Dataset, xr.DataArray)):
        if verbose:
            print(f"(make_mask) `input_command`: cdo setrtoc2,{range_string} dataset")
        # If only processing one `xr.Dataset`, the `input` argument cannot include the range string
        mask_xr = cdo_command(
            range_string,
            input=dataset, 
            returnXDataset='mask'
        )
    else: 
        # Assemble the `cdo` input command to pass to `mergetime`
        input_command = f"{input_command_prefix}{range_string}{input_command_files}"
        if verbose:
            print(f"(make_mask) `input_command`: {input_command}")
        mask_xr = cdo_command(
            input = input_command,
            returnXDataset = 'mask',
        )
    # Get the long name of the original dataset, if available
    try:
        old_long_name = dataset[var].attrs['long_name']
    except:
        old_long_name = mask_var_name
    # Modify the attributes of the dataset to reflect the changes, if applicable
    if add_mask_attrs:
        mask_xr = add_mask_attributes(
            mask_xr,
            var,
            mask_var_name,
            old_long_name,
            mask_this_val,
            mask_this_range,
            val_mask,
            val_inside_range,
            val_outside_range,
            verbose,
        )

    # Save the modified dataset, if applicable
    if not isinstance(save_as, type(None)):
        # Save the plot to file
        mask_xr.to_netcdf(save_as)
    
    return mask_xr

def add_mask_attributes(
    mask_xr: xr.Dataset,
    var: str,
    mask_var_name: str,
    old_long_name: str,
    mask_this_val: (int, float, None),
    mask_this_range: ([(int, float), (int, float)], None),
    val_mask: bool,
    val_inside_range: (int, float),
    val_outside_range: (int, float),
    verbose: bool,
):
    """ Add mask-related attributes to the given dataset.

        A helper function for `make_mask()` to add attributes that specify the changes to the dataset when making a mask.

        Parameters
        ----------
        mask_xr : `xarray.Dataset`
            The dataset to which to add mask attributes.
        var : `str`
            The name of the variable from which a mask was created.
        mask_var_name : `str`
            The name given to the new mask variable.
        old_long_name : `str`
            The long name from the original dataset from which the mask was created.
        mask_this_val : `int`, `float`, `None`
            The value masked out.
            If an option is given here, then `mask_this_range` must be `None`.
        mask_this_range : list of `int` or `float`, `None`
            The range of values masked out.
            Must be of length 2, order does not matter.
            If an option is given here, then `mask_this_val` must be `None`.
        val_mask : `bool`
            Whether or not a value for `mask_this_val` was given.
        val_inside_range : `int`, `float`
            The value assigned to the masked out values.
        val_outside_range : `int`, `float`
            The value assigned to values that are not masked out.
        verbose : `bool`
            Whether to verbosely output information as the function executes.

        Returns
        -------
        mask_xr : `xarray.Dataset`
            A dataset where mask-related attributes have been added.
        
        Examples
        --------
        >>> from arctichoke.dataset import make_example_dataset
        >>> dataset = make_example_dataset(n=3)
        >>> dataset['test_var'].values
        array([[0., 1., 2.],
               [3., 4., 5.],
               [6., 7., 8.]])
        >>> from arctichoke.dataset import make_mask
        >>> dataset_masked = make_mask(dataset, var='test_var', mask_this_range=[0,4])
        >>> dataset_masked['test_var_mask'].attrs
        {'standard_name': 'test_var_mask',
        'long_name': 'Mask of test_var_mask',
        'units': '0: Masked, 1: Not masked',
        'comment': 'Masked range [0, 4] with 0: Masked, 1: Not masked',
        'original_name': 'test_var',
        'history': '2026-07-22T17:58:00Z altered by `arctichoke`: Masked range [0, 4] with 0: Masked, 1: Not masked. '}
    """
    # Verify input arguments
    if not isinstance(mask_xr, xr.Dataset):
        raise TypeError(f"(add_mask_attributes) `mask_xr` must be a`xr.Dataset`. Got type: {type(mask_xr)}")
    if not isinstance(var, str):
        raise TypeError(f"(add_mask_attributes) `var` must be a string. Got type: {type(var)}")
    if not isinstance(mask_var_name, str):
        raise TypeError(f"(add_mask_attributes) `mask_var_name` must be a string. Got type: {type(mask_var_name)}")
    if not isinstance(old_long_name, str):
        raise TypeError(f"(add_mask_attributes) `old_long_name` must be a string. Got type: {type(old_long_name)}")
    if not isinstance(mask_this_val, (int, float, type(None))):
        raise TypeError(f"(add_mask_attributes) `mask_this_val` must be `int`, `float`, or `None`. Got type: {type(mask_this_val)}")
    if isinstance(mask_this_range, type([])):
        if len(mask_this_range) != 2:
            raise TypeError(f"(add_mask_attributes) `mask_this_range` must be a list of length 2. Got length: {len(mask_this_range)}")
        else:
            for mask_range_val in mask_this_range:
                if not isinstance(mask_range_val, (int, float)):
                    raise TypeError(f"(add_mask_attributes) Values of `mask_this_range` must be `int` or `float`. Got type: {type(mask_range_val)}")
    elif not isinstance(mask_this_range, (type([]), type(None))):
        raise TypeError(f"(add_mask_attributes) `mask_this_range` must be a list or `None`. Got type: {type(mask_this_range)}")
    if not isinstance(val_mask, bool):
        raise TypeError(f"(add_mask_attributes) `val_mask` must be a `bool`. Got type: {type(val_mask)}")
    if not isinstance(val_inside_range, (int, float)):
        raise TypeError(f"(add_mask_attributes) `val_inside_range` must be `int` or `float`. Got type: {type(val_inside_range)}")
    if not isinstance(val_outside_range, (int, float)):
        raise TypeError(f"(add_mask_attributes) `val_outside_range` must be `int` or `float`. Got type: {type(val_outside_range)}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(add_mask_attributes) `verbose` must be a `bool`. Got type: {type(verbose)}")

    if verbose:
        print(f"(add_mask_attributes) Adding mask-related attributes to the dataset.")
    # Rename `var` in the new dataset to append `_mask`
    mask_xr = mask_xr.rename_vars({var:mask_var_name})
    # Modify the attributes of the dataset to reflect the changes
    mask_xr[mask_var_name].attrs['standard_name'] = mask_var_name
    mask_xr[mask_var_name].attrs['long_name'] = f'Mask of {old_long_name}'
    mask_xr[mask_var_name].attrs['units'] = f'{val_inside_range}: Masked, {val_outside_range}: Not masked'
    if val_mask:
        mask_xr[mask_var_name].attrs['comment'] = f'Masked value {mask_this_val} with {val_inside_range}: Masked, {val_outside_range}: Not masked'
    else:
        mask_xr[mask_var_name].attrs['comment'] = f'Masked range {mask_this_range} with {val_inside_range}: Masked, {val_outside_range}: Not masked'
    mask_xr[mask_var_name].attrs['original_name'] = var
    if 'history' in mask_xr[mask_var_name].attrs.keys():
        original_history = mask_xr[mask_var_name].attrs['history']
    else:
        original_history = ''
    mask_xr[mask_var_name].attrs['history'] = f"{get_current_datetime_str()} altered by `arctichoke`: {mask_xr[mask_var_name].attrs['comment']}. {original_history}"
    if 'history' in mask_xr.attrs.keys():
        original_history = mask_xr.attrs['history']
    else:
        original_history = ''
    mask_xr.attrs['history'] = f"{get_current_datetime_str()} altered by `arctichoke`: {mask_xr[mask_var_name].attrs['comment']}. {original_history}"

    return mask_xr