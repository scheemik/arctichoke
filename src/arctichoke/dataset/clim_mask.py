import numpy as np
import xarray as xr

from arctichoke.dataset.mask_dataset import make_mask
from arctichoke.dataset.select_months import select_months
from arctichoke.path import list_variable_files
from arctichoke.params import sea_ice_vars

def make_clim_mask(
    this_source_id: str,
    this_var: str,
    this_variant_label: str,
    this_modification: str,
    this_experiment: str = 'hist-1950',
    select_summer: bool = True,
    mask_var_name: str = None,
    mask_this_range: [(int, float), (int, float)] = [15, np.iinfo(np.int32).max],
    val_inside_range: (int, float) = 1,
    val_outside_range: (int, float) = np.nan,
    verbose: bool = False,
    **kwargs,
):
    """ Make a mask based on the specified climatology.

        Load the specified climatology for the given model, variant, and variable. 
        Create a mask given the specified parameters using the `make_mask()` function.

        Parameters
        ----------
        this_source_id : `str`
            The source ID of the model from which to make a mask.
            Example: `'EC-Earth3P-HR'`.
        this_var : `str`
            The variable ID of the variable from which to make a mask.
            Example: `'silandfast'`.
        this_variant_label : `str`
            The variant label of the model from which to make a mask.
            Example: `'r1i1p2f1'`.
        this_modification : `str`
            The modification of the data from which to make a mask.
            Example: `'trim_CAA_'`.
        this_experiment : `str`, optional
            The experiment of the model from which to make a mask.
            Default is `'hist-1950'`.
        select_summer : `bool`, optional
            Whether to use `select_months()` to only keep the summer months (June-October) for the mask.
            Default is `True`.
        mask_var_name : `str`, `None`, optional
            The name to give to the new mask variable.
            If `None` is given, the new name will simply append `_clim_mask` to `this_var`.
            Default is `None`.
        mask_this_range : list of `int` or `float`, `None`, optional
            The range of values to mask out.
            Must be of length 2, order does not matter.
            If an option is given here, then `mask_this_val` must be `None`.
            Default is `[15, np.iinfo(np.int32).max]`.
        val_inside_range : `int`, `float`, optional
            The value to assign to the masked out values.
            Default is `1`.
        val_outside_range : `int`, `float`, optional
            The value to assign to values that are not masked out.
            Default is `np.nan`.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `make_mask()`.

        Returns
        -------
        clim_mask_dataset : `xarray.Dataset`
            A dataset of the mask of the given climatology.
        
        Examples
        --------
    """
    # Verify input arguments
    if not isinstance(select_summer, bool):
        raise TypeError(f"(make_clim_mask) `select_summer` must be a `bool`. Got type: {type(select_summer)}")
    if not isinstance(mask_var_name, (str, type(None))):
        raise TypeError(f"(make_clim_mask) `mask_var_name` must be a string or `None`. Got type: {type(mask_var_name)}")
    if isinstance(mask_this_range, type([])):
        if len(mask_this_range) != 2:
            raise TypeError(f"(make_clim_mask) `mask_this_range` must be a list of length 2. Got length: {len(mask_this_range)}")
        else:
            for mask_range_val in mask_this_range:
                if not isinstance(mask_range_val, (int, float)):
                    raise TypeError(f"(make_clim_mask) Values of `mask_this_range` must be `int` or `float`. Got type: {type(mask_range_val)}")
    elif not isinstance(mask_this_range, (type([]), type(None))):
        raise TypeError(f"(make_clim_mask) `mask_this_range` must be a list or `None`. Got type: {type(mask_this_range)}")
    if not isinstance(val_inside_range, (int, float)):
        raise TypeError(f"(make_clim_mask) `val_inside_range` must be `int` or `float`. Got type: {type(val_inside_range)}")
    if not isinstance(val_outside_range, (int, float)):
        raise TypeError(f"(make_clim_mask) `val_outside_range` must be `int` or `float`. Got type: {type(val_outside_range)}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(make_clim_mask) `verbose` must be a `bool`. Got type: {type(verbose)}")

    # Assemble new mask variable name, if applicable
    if isinstance(mask_var_name, type(None)):
        mask_var_name = f'{this_var}_clim_mask'

    # Get the relevant file path
    sivar_clim_file = list_variable_files(
        source_id = this_source_id,
        variable_id = f'{this_var}_month_mean',
        experiment_id = this_experiment,
        variant_label = this_variant_label,
        with_modification = this_modification,
        verbose = verbose,
    )

    # Open those files into a multi-file dataset
    if select_summer:
        dataset_clim = select_months(
            sivar_clim_file,
            time_dim='month',
            verbose = verbose,
        )
    else:
        dataset_clim = xr.open_mfdataset(
            sivar_clim_file,
            data_vars = 'all',
        )

    # Determine whether this is a regular or marker variable
    if this_var in sea_ice_vars.keys():
        if sea_ice_vars[this_var]['marker_var']:
            # Take the sum across the 12 months
            dataset_clim = dataset_clim.sum(dim='month', min_count=1)
        else:
            # Take the mean across the 12 months
            dataset_clim = dataset_clim.mean(dim='month')
    else:
        raise ValueError(f"(make_clim_mask) `this_si_var={this_var}` is not in the `sea_ice_vars` dictionary. Available variables: {sea_ice_vars.keys()}")
    # Adjust the `long_name` attribute to change the colorbar label
    dataset_clim[f'{this_var}_month_mean'].attrs['long_name'] = dataset_clim[f'{this_var}_month_mean'].attrs['long_name'].replace('onthly m', '')

    # Make the mask from the climatology
    clim_mask_dataset = make_mask(
        dataset_clim,
        var = f'{this_var}_month_mean',
        mask_var_name = mask_var_name,
        mask_this_range = mask_this_range,
        val_inside_range = 1,
        val_outside_range = np.nan,
        add_mask_attrs = True,
        verbose = verbose,
        **kwargs,
    )
    return clim_mask_dataset