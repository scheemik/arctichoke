import os
import subprocess
import xarray as xr

from cdo import Cdo, __version__
cdo = Cdo()
# Set path for temporary files in case of a crash
cdo = Cdo(tempdir='./cdo_tmp/')
cdo.cleanTempDir()

from arctichoke.verify import verify_path
from arctichoke.params.var_params import meta_vars
from arctichoke.dataset.grid_type import get_grid_type
from arctichoke.dataset.trim_dataset import trim_latlon

def interp_to_reg_grid(
    dataset: (str, xr.Dataset, xr.DataArray),
    targetgrid: str = 'data/target_grid_0-25_deg.nc',
    trim_to_bbox: [float, float, float, float] = False,
    save_as: str = None,
    verbose: bool = False,
    **kwargs,
):
    """ Interpolate the given dataset onto the specified regular grid.

        Use the CDO `remapbil` function to regrid by interpolation the given dataset onto the specified target grid.

        Parameters
        ----------
        dataset : `str`, `xarray.Dataset`, `xarray.DataArray`
            The dataset to interpolate.
        targetgrid : `str`
            The target grid on which to interpolate the dataset.
            This must either be a specified string such as `F32`, `F64`, etc. or a filepath to a dataset with latitude and longitude dimensions with the following attributes:
                - `standard_name`, Ex: 'latitude'
                - `long_name`, Ex: `latitude`
                - `units`, Ex: `degrees_north`
                - `axis`, Ex: `Y`
                
            Default is `data/target_grid_0-25_deg.nc`.
        trim_to_bbox : `bool`, Array of `float`, optional
            An array of coordinates defining the bounding box to which to trim in the following format:
                - [LAT_MAX, LAT_MIN, LON_MAX, LON_MIN]
                
            A value of `True` trims the interpolated dataset to the bounds of the original dataset
            Default is `False` which does not trim the interpolated dataset.
        save_as : `str`, `None`, optional
            The file name to which to save the modified dataset.
            Default is `None`, which doesn't save the dataset to a file.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `trim_latlon()`.

        Returns
        -------
        dataset_interp : `xarray.Dataset`
            The dataset interpolated onto the grid provided.
        
        Examples
        --------
        >>> 
    """
    # Verify input arguments
    if not isinstance(dataset, (str, xr.Dataset, xr.DataArray)):
        raise TypeError(f"(interp_to_reg_grid) `dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(dataset)}")
    if isinstance(dataset, str):
        if not dataset.endswith('.nc'):
            raise TypeError(f"(interp_to_reg_grid) `datafile` must be a `.nc` filepath. Got: {datafile}")
        dataset = verify_path(dataset)
        xr_data = xr.open_dataset(dataset)
    else:
        xr_data = dataset
    if not isinstance(targetgrid, str):
        raise TypeError(f"(interp_to_reg_grid) `targetgrid` must be a string. Got type: {type(targetgrid)}")
    else:
        if targetgrid in ['F32', 'F64']:
            target_grid = targetgrid
        elif targetgrid.endswith('.nc'):
            target_grid = verify_path(targetgrid)
        else:
            raise TypeError(f"(interp_to_reg_grid) `targetgrid` must be a `.nc` filepath, or one of the following: 'F32', 'F64'. Got: {targetgrid}")
    if isinstance(trim_to_bbox, type([])):
        if len(trim_to_bbox) != 4:
            raise ValueError(f"(interp_to_reg_grid) `trim_to_bbox` must be a list with exactly 4 values. Got length: {len(trim_to_bbox)}")
        for i in range(len(trim_to_bbox)):
            trim_bbox_val = trim_to_bbox[i]
            if not isinstance(trim_bbox_val, (int, float)):
                raise TypeError(f"(interp_to_reg_grid) Each value of `trim_to_bbox` must be an integer or `float`. For value [{i}], got type: {type(trim_bbox_val)}")
    elif not isinstance(trim_to_bbox, bool):
        raise TypeError(f"(interp_to_reg_grid) `trim_to_bbox` must be an array or `bool`. Got type: {type(trim_to_bbox)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(interp_to_reg_grid) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.nc' in save_as:
        raise TypeError(f"(interp_to_reg_grid) `save_as` must be a `.nc` filepath. Got: {save_as}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(interp_to_reg_grid) `verbose` must be a `bool`. Got type: {type(verbose)}")

    # Information to output
    if verbose:
        print(f"(interp_to_reg_grid) `save_as`: {save_as}")

    # Use `cdo` to trim the indices which contain no data within the bounding box
    if not isinstance(dataset, str):
        # Use the Python implementation of `cdo` to directly return an `xarray` Dataset
        dataset_interp = cdo.remapbil(targetgrid, input=xr_data, returnXDataset='interp_to_reg_grid')
        # Set a dummy value for the `tmp_save_file` variable
        tmp_save_file = None
    else:
        # Set a location for the temporary file
        tmp_save_file = './cdo_tmp/tmp_remapbil_file.nc'
        # Use `subprocess` to execute a `cdo` shell command
        # This can be helpful when working with very large file sizes
        cdo_command = f"cdo remapbil,{targetgrid} {dataset} {tmp_save_file}"
        if verbose:
            print(f"(interp_to_reg_grid) Using `cdo` directly, `cdo_command`: {cdo_command}")
        subprocess.run(cdo_command, shell=True)
        # Load that file in as an xarray
        tmp_save_file = verify_path(tmp_save_file)
        dataset_interp = xr.open_dataset(tmp_save_file)
    
    # Get the list of data variables
    data_vars = list(dataset_interp.data_vars.keys())
    if verbose:
        print(f"(interp_to_reg_grid) `data_vars` all: {data_vars}")
    # Remove the unnecessary meta variables to avoid errors when trimming
    for meta_var in meta_vars:
        if meta_var in data_vars:
            data_vars.remove(meta_var)
    if verbose:
        print(f"(interp_to_reg_grid) `data_vars` after cleaning: {data_vars}")
    
    # Check whether to trim interpolated dataset
    if trim_to_bbox:
        # Check whether a bounding box was given
        if not isinstance(trim_to_bbox, type([])):
            # If none given, find the minimum and maximum values of latitude and longitude from the original dataset
            print(f"(interp_to_reg_grid) Automatically trimming to the original dataset's lat-lon bounds not implemented yet.")
        else:
            # Trim to the given bounds
            dataset_interp = trim_latlon(
                dataset_interp,
                trim_to_bbox,
                save_as = None,
                verbose = verbose,
                **kwargs,
            )

    # Get the grid type of the dataset
    this_grid_type = get_grid_type(dataset_interp)
    if this_grid_type != 'regular':
        raise ValueError(f"(interp_to_reg_grid) Interpolated dataset's grid type is not 'regular'. Got grid type: {this_grid_type}")

    # Save the interpolated dataset, if applicable
    if not isinstance(save_as, type(None)):
        # Save the plot to file
        dataset_interp.to_netcdf(save_as)
    
    # Clean up the `tmp_save_file` file if necessary
    if not isinstance(tmp_save_file, type(None)):
        os.remove(tmp_save_file)

    return dataset_interp