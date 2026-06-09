import numpy as np
import xarray as xr 

from seaicecp.verify import verify_path

def get_latlon_names(
    dataset: (str, xr.DataArray, xr.Dataset),
):
    """ Get the latitude and longitude variable names of the dataset.

        Opens the given dataset, checks the coordinates, and determines the name of the latitude and longitude variables.
        This will be either `lat`/`lon` or `latitude`/`longitude`.

        Parameters
        ----------
        dataset : `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset for which to determine the latitude and longitude names.

        Returns
        -------
        lat_var : `str`
            The name of latitude variable in the dataset.
            This will be either `lat` or `latitude`.
        lon_var : `str`
            The name of longitude variable in the dataset.
            This will be either `lon` or `longitude`.
        
        Examples
        --------
        >>> from seaicecp.dataset.grid_type import get_latlon_names
        >>> get_latlon_names('/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/siconc/gn/v20170928/siconc_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_201401-201412.nc')
        ('lat', 'lon')
        >>> get_latlon_names('/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/sithick/gn/v20170928/sithick_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_201401-201412.nc')
        ('latitude', 'longitude')
    """
    # Verify input arguments
    if not isinstance(dataset, (str, xr.Dataset, xr.DataArray)):
        raise TypeError(f"(get_latlon_names) `dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(dataset)}")
    if isinstance(dataset, str):
        # Verify this is a valid path
        dataset = verify_path(dataset)
        if not dataset.endswith('.nc'):
            raise TypeError(f"(get_latlon_names) `dataset` must be a `.nc` filepath. Got: {dataset}")
        # Open the dataset
        dataset = xr.open_dataset(dataset)
    
    # Get the latitude and longitude coordinate names
    xr_coords = list(dataset.coords)

    # Check for the latitude variable name
    if 'latitude' in xr_coords:
        lat_var = 'latitude'
    elif 'lat' in xr_coords:
        lat_var = 'lat'
    else:
        raise ValueError(f"(quadmesh_map) `xr_data` must have a latitude coordinate. Got coordinates: {xr_coords}")
    # Check for the longitude variable name
    if 'longitude' in xr_coords:
        lon_var = 'longitude'
    elif 'lon' in xr_coords:
        lon_var = 'lon'
    else:
        raise ValueError(f"(quadmesh_map) `xr_data` must have a longitude coordinate. Got coordinates: {xr_coords}")
    
    return lat_var, lon_var

def determine_lon_type(
    lon_min: (int, float),
    lon_max: (int, float),
):
    """ Determine the longitude type based on the minimum and maximum values.

        Given the minimum and maximum longitude values of a dataset, tries to determines the type of longitude: Prime Meridian centered (0 to 360), International Date Line centered (-180 to 180), or other.

        Parameters
        ----------
        lon_min : `int`, `float`
            The minimum longitude value.
        lon_max : `int`, `float`
            The maximum longitude value.

        Returns
        -------
        lon_type : `str`
            The type of longitude that the dataset has which will be `'PM_centered'`, `'IDL_centered'`, or `'other'`.
        
        Examples
        --------
        >>> from seaicecp.dataset.grid_type import determine_lon_type
        >>> determine_lon_type(lon_min = 0, lon_max = 360)
        PM_centered
        >>> determine_lon_type(lon_min = -180, lon_max = 180)
        IDL_centered
    """
    # Verify input arguments
    if not isinstance(lon_min, (int, float, np.float32)):
        raise TypeError(f"(determine_lon_type) `lon_min` must be `int` or `float`. Got type: {type(lon_min)}")
    if not isinstance(lon_max, (int, float, np.float32)):
        raise TypeError(f"(determine_lon_type) `lon_max` must be `int` or `float`. Got type: {type(lon_max)}")
    if lon_min > lon_max:
        raise ValueError(f"(determine_lon_type) `lon_min` must be less than `lon_max`. Got `lon_min`: {lon_min}, `lon_max`: {lon_max}")
    if lon_min < -180 or lon_max < -180:
        raise ValueError(f"(determine_lon_type) `lon_min` and `lon_max` cannot be less than -180. Got `lon_min`: {lon_min}, `lon_max`: {lon_max}")
    if lon_min > 360 or lon_max > 360:
        raise ValueError(f"(determine_lon_type) `lon_min` and `lon_max` cannot be greater than 360. Got `lon_min`: {lon_min}, `lon_max`: {lon_max}")
    
    if lon_min == lon_max:
        lon_type = 'other'
    elif lon_min == 0 or lon_max == 0:
        if lon_min < 0:
            lon_type = 'IDL_centered'
        elif lon_max > 180:
            lon_type = 'PM_centered'
        else:
            lon_type = 'other'
    elif lon_min <= 0:
        if lon_max <= 180:
            lon_type = 'IDL_centered'
        else:
            lon_type = 'other'
    elif lon_min > 0:
        if lon_max > 180:
            lon_type = 'PM_centered'
        else:
            lon_type = 'other'
    else:
        lon_type = 'other'
    return lon_type

def get_lon_type(
    dataset: (str, xr.DataArray, xr.Dataset),
):
    """ Get the longitude type of the dataset.

        Opens the given dataset, checks the coordinates, and determines the type of longitude: Prime Meridian centered (0 to 360), International Date Line centered (-180 to 180), or other.

        Parameters
        ----------
        dataset : `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset for which to determine the longitude type.

        Returns
        -------
        lon_type : `str`
            The type of longitude that the dataset has which will be `'PM_centered'`, `'IDL_centered'`, or `'other'`.
        
        Examples
        --------
        >>> from seaicecp.dataset.grid_type import get_lon_type
        >>> get_lon_type('/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201401-201412.nc')
        IDL_centered
    """
    # Verify input arguments
    if not isinstance(dataset, (str, xr.Dataset, xr.DataArray)):
        raise TypeError(f"(get_lon_type) `dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(dataset)}")
    if isinstance(dataset, str):
        # Verify this is a valid path
        dataset = verify_path(dataset)
        if not dataset.endswith('.nc'):
            raise TypeError(f"(get_lon_type) `dataset` must be a `.nc` filepath. Got: {dataset}")
        # Open the dataset
        dataset = xr.open_dataset(dataset)
    
    # Get the latitude and longitude coordinate names
    lat_var, lon_var = get_latlon_names(dataset)
    
    # Get the longitude values of this dataset
    lon_vals = dataset[lon_var].values.flatten()
    # Get the maximum and minimum longitude values
    lon_max = max(lon_vals)
    lon_min = min(lon_vals)

    # Determine the type of longitude values the dataset has
    lon_type = determine_lon_type(
        lon_min,
        lon_max,
    )
    return lon_type
