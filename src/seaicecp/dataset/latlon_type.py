import xarray as xr 

from seaicecp.verify import verify_path
from seaicecp.dataset.get_variable import get_variable_name

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
