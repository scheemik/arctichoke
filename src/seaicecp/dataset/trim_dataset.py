import numpy as np
import subprocess
import xarray as xr
import warnings
from cdo import Cdo, __version__
cdo = Cdo()
# Set path for temporary files in case of a crash
cdo = Cdo(tempdir='./cdo_tmp/')
cdo.cleanTempDir()

import seaicecp.params as sps
from seaicecp.verify import verify_path
from seaicecp.params.var_params import meta_vars
from seaicecp.dataset.grid_type import get_grid_type
from seaicecp.dataset.latlon_type import get_latlon_names, get_lon_type

def trim_latlon(
    dataset: (str, xr.Dataset, xr.DataArray),
    map_bbox: [float, float, float, float] = sps.NWP_BBOX,
    precise_trim: bool = False,
    save_as: str = None,
    verbose: bool = False,
):
    """ Trim the given dataset.

        Select only the data within the given bounding box of latitude and longitude coordinates from the given dataset.

        Parameters
        ----------
        dataset : `str`, `xarray.Dataset`, `xarray.DataArray`
            The dataset to plot.
        map_bbox : Array of `float`, optional
            An array of coordinates defining the bounding box of the map in the following format:
                - [LAT_MAX, LAT_MIN, LON_MAX, LON_MIN]
                
            Default is `seaicecp.params.latlon_params.NWP_BBOX`.
        precise_trim : `bool`, optional
            Whether to precisely trim an irregular grid to the bounding box, making all values outside the bounding box null.
            Default is `False`.
        save_as : `str`, `None`, optional
            The file name to which to save the modified dataset.
            Default is `None`, which doesn't save the dataset to a file.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.

        Returns
        -------
        xr_data_trimmed : `xarray.Dataset`
            The dataset trimmed to the latitude and longitude ranges provided.
        
        Examples
        --------
        >>> 
    """
    # Verify input arguments
    if not isinstance(dataset, (str, xr.Dataset, xr.DataArray)):
        raise TypeError(f"(trim_latlon) `dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(dataset)}")
    if isinstance(dataset, str):
        if not dataset.endswith('.nc'):
            raise TypeError(f"(trim_latlon) `datafile` must be a `.nc` filepath. Got: {datafile}")
        dataset = verify_path(dataset)
        xr_data = xr.open_dataset(dataset)
    else:
        xr_data = dataset
    if not isinstance(map_bbox, type([])):
        raise TypeError(f"(trim_latlon) `map_bbox` must be a list. Got type: {type(map_bbox)}")
    elif not len(map_bbox) == 4:
        raise ValueError(f"(trim_latlon) `map_bbox` must have a length of 4. Got length: {len(map_bbox)}")
    else: 
        for i in range(len(map_bbox)):
            if not isinstance(map_bbox[i], (int, float)):
                raise TypeError(f"(trim_latlon) `map_bbox[{i}]` must be a number. Got type: {type(map_bbox[i])}")
    if not isinstance(precise_trim, bool):
        raise TypeError(f"(trim_latlon) `precise_trim` must be a `bool`. Got type: {type(precise_trim)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(trim_latlon) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.nc' in save_as:
        raise TypeError(f"(trim_latlon) `save_as` must be a `.nc` filepath. Got: {save_as}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(trim_latlon) `verbose` must be a `bool`. Got type: {type(verbose)}")
    
    # Information to output
    if verbose:
        print(f"(trim_latlon) `save_as`: {save_as}")

    # Unpack the bounding box values
    box_lat_max = map_bbox[0]
    box_lat_min = map_bbox[1]
    box_lon_max = map_bbox[2]
    box_lon_min = map_bbox[3]

    # Determine the longitude type of the dataset
    lon_type = get_lon_type(xr_data)
    if verbose:
        print(f"(trim_latlon) `lon_type`: {lon_type}")
    if lon_type == 'PM_centered':
        # Check whether the longitude values are negative
        if box_lon_max < 0:
            box_lon_max += 360
        if box_lon_min < 0:
            box_lon_min += 360
    
    # cdo expects bounding box coordinates as a string in the order: 
    ## lon_min, lon_max, lat_min, lat_max
    this_bbox = f"{box_lon_min},{box_lon_max},{box_lat_min},{box_lat_max}"
    if verbose:
        print(f"(trim_latlon) `this_bbox`: {this_bbox}")

    # Use `cdo` to trim the indices which contain no data within the bounding box
    if not isinstance(dataset, str):
        # Use the Python implementation of `cdo` to directly return an `xarray` Dataset
        xr_data_trimmed = cdo.sellonlatbox(this_bbox, input=xr_data, returnXDataset='trim_latlon')
    else:
        # Set a location for the temporary file
        tmp_save_file = './cdo_tmp/tmp_sellonlatbox_file.nc'
        # Use `subprocess` to execute a `cdo` shell command
        # This can be helpful when working with very large file sizes
        cdo_command = f"cdo -O -s -f nc -sellonlatbox,{this_bbox} {dataset} {tmp_save_file}"
        if verbose:
            print(f"(trim_latlon) Using `cdo` directly, `cdo_command`: {cdo_command}")
        subprocess.run(cdo_command, shell=True)
        # Load that file in as an xarray
        xr_data_trimmed = xr.open_dataset(tmp_save_file)
    
    # Get the list of data variables
    data_vars = list(xr_data_trimmed.data_vars.keys())
    if verbose:
        print(f"(trim_latlon) `data_vars` all: {data_vars}")
    # Remove the unnecessary meta variables to avoid errors when trimming
    for meta_var in meta_vars:
        if meta_var in data_vars:
            data_vars.remove(meta_var)
    if verbose:
        print(f"(trim_latlon) `data_vars` after cleaning: {data_vars}")

    # Get the latitude and longitude coordinate names
    lat_var, lon_var = get_latlon_names(xr_data_trimmed)
    if verbose:
        print(f"(trim_latlon) `lat_var`: {lat_var}")
        print(f"(trim_latlon) `lon_var`: {lon_var}")

    # Get the grid type of the dataset
    this_grid_type = get_grid_type(xr_data_trimmed)

    # Get the minimum and maximum values
    if verbose:
        if this_grid_type == 'irregular' and precise_trim == True:
            print(f"(trim_latlon) After `cdo` trim, before precise trim.")
        elif this_grid_type == 'regular':
            print(f"(trim_latlon) After `cdo` trim.")
        for data_var in data_vars:
            this_data_array = xr_data_trimmed[data_var].values.flatten()
            this_min = np.nanmin(this_data_array)
            this_max = np.nanmax(this_data_array)
            print(f"(trim_latlon)     For variable {data_var}, `nanmin`:{this_min}, `nanmax`:{this_max}")

    if this_grid_type == 'irregular' and precise_trim == True:
        if verbose:
            print(f"(trim_latlon) Trimming grid type: {this_grid_type}")
        # Set the values of the data variables outside the bounding box to `nan`
        for var in data_vars:
            xr_data_trimmed[var] = xr_data_trimmed[var].where(
                lambda val:
                    (xr_data_trimmed[lat_var] < box_lat_max) &
                    (xr_data_trimmed[lat_var] > box_lat_min) &
                    (xr_data_trimmed[lon_var] > box_lon_min) &
                    (xr_data_trimmed[lon_var] < box_lon_max),
                lambda val: np.nan
            )
        # Get the minimum and maximum values
        if verbose:
            print(f"(trim_latlon) After precise trim.")
            for data_var in data_vars:
                this_data_array = xr_data_trimmed[data_var].values.flatten()
                this_min = np.nanmin(this_data_array)
                this_max = np.nanmax(this_data_array)
                print(f"(trim_latlon)     For variable {data_var}, `nanmin`:{this_min}, `nanmax`:{this_max}")

    # Save the trimmed dataset, if applicable
    if not isinstance(save_as, type(None)):
        # Save the plot to file
        xr_data_trimmed.to_netcdf(save_as)

    return xr_data_trimmed

def trim_files(
    files_to_trim: [str],
    name_prefix: str = 'trim_',
    use_cdo_python: bool = True,
    overwrite: bool = False,
    **kwargs,
):
    """ Trim the specified files and save them as new files.

        For each given file, load the data, trim the dataset, then save that trimmed dataset as a new file in the same location with a new filename. 

        Parameters
        ----------
        files_to_trim : List of `str`
            A list of paths of the data files to trim. 
        name_prefix : `str`, optional
            The prefix to be prepended to each file name when saving.
            Default is `trim_`.
        use_cdo_python : `bool`, optional
            Whether to tell `trim_latlon()` to use the Python implementation of `cdo` or use `subprocess` to run a shell command.
            Default is `True` which uses the Python implementation of `cdo`.
        overwrite : `bool`, optional
            Whether to overwrite an existing file if it exists.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `trim_latlon()`.

        Returns
        -------
        None
        
        Examples
        --------
        >>> from seaicecp.path.find_data import list_variable_files
        >>> list_of_files = list_variable_files('EC-Earth3P-HR', 'siage', variant_label='r3i1p2f1')
        >>> from seaicecp.dataset.trim_dataset import trim_files
        >>> trim_files(list_of_files)
        (trim_files) `name_prefix`: trim_NWP_
        (trim_latlon) `save_as`: /seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/siage/gn/v20190214/trim_NWP_siage_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_195001-195012.nc
        ...
        (trim_latlon) `save_as`: /seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/siage/gn/v20190214/trim_NWP_siage_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201401-201412.nc
    """
    # Verify input arguments
    if isinstance(files_to_trim, str):
        files_to_trim = [files_to_trim]
    elif not isinstance(files_to_trim, type([])):
        raise TypeError(f"(trim_files) `files_to_trim` must be a list. Got type: {type(files_to_trim)}")
    for item in files_to_trim:
        if not isinstance(item, str):
            raise TypeError(f"(trim_files) `files_to_trim` must be a list of strings. Got type: {type(item)} for item {item}")
    if not isinstance(name_prefix, str):
        raise TypeError(f"(trim_files) `name_prefix` must be a string. Got type: {type(name_prefix)}")
    elif not name_prefix.endswith("_"):
        # Make sure the prefix ends with an underscore
        name_prefix = f"{name_prefix}_"
    # Replace any spaces in `name_prefix` with underscores
    name_prefix = name_prefix.replace(" ", "_")
    if not isinstance(use_cdo_python, bool):
        raise TypeError(f"(trim_files) `use_cdo_python` must be a `bool`. Got type: {type(use_cdo_python)}")
    if not isinstance(overwrite, bool):
        raise TypeError(f"(trim_files) `overwrite` must be a `bool`. Got type: {type(overwrite)}")
    
    # Information to output
    print(f"(trim_files) `name_prefix`: {name_prefix}")

    # Loop across each file in the list
    for filepath in files_to_trim:
        # Verify the filepath exists
        filepath = verify_path(filepath)
        # Assemble the new file name
        filename = filepath.split('/')[-1]
        new_filename = f"{name_prefix}{filename}"
        new_filepath = filepath.replace(filename, new_filename)
        # Check whether the file exists
        try:
            verify_path(new_filepath)
            if overwrite == False:
                warnings.warn(f"(trim_files) file `{new_filepath}` exists already. To overwrite this file, set `overwrite` to `True`.", UserWarning)
                continue
            else:
                print(f"\t(trim_files) Overwriting file `{new_filepath}`.")
        except (FileNotFoundError):
            print(f"\t(trim_files) Writing file `{new_filepath}`.")
        # Load this file with `xarray`
        if use_cdo_python:
            this_xr = xr.open_dataset(filepath)
        else:
            this_xr = filepath
        # Trim the dataset and save to file
        trim_latlon(
            dataset = this_xr,
            save_as = new_filepath,
            **kwargs,
        )

    return None

