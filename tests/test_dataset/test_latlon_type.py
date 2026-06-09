import xarray as xr

from seaicecp.dataset import latlon_type
from seaicecp.dataset.example_dataset import make_example_dataset
from seaicecp.path import list_variable_files

def test_get_latlon_names():
    """Test the `get_latlon_names` function."""
    # Define test cases
    modified_example_dataset = make_example_dataset()
    modified_example_dataset = modified_example_dataset.isel(i=0)
    test_cases = [
        {
            'dataset': make_example_dataset(),
            'expected_latlon_names': ('latitude','longitude'),
        },
        {
            'dataset': modified_example_dataset,
            'expected_latlon_names': ('latitude','longitude'),
        },
        {
            'dataset': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201401-201412.nc',
            'expected_latlon_names': ('latitude','longitude'),
        },
        {
            'dataset': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/Ofx/areacello/gn/v20190301/areacello_Ofx_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn.nc',
            'expected_latlon_names': ('latitude','longitude'),
        },
        {
            'dataset': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/sithick/gn/v20170928/sithick_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_201401-201412.nc',
            'expected_latlon_names': ('latitude','longitude'),
        },
        {
            'dataset': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/siconc/gn/v20170928/siconc_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_201401-201412.nc',
            'expected_latlon_names': ('lat','lon'),
        },
        {
            'dataset': xr.open_dataset('/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/Ofx/areacello/gn/v20190301/areacello_Ofx_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn.nc'),
            'expected_latlon_names': ('latitude','longitude'),
        },
        {
            'dataset': xr.open_dataset('/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/sithick/gn/v20170928/sithick_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_201401-201412.nc'),
            'expected_latlon_names': ('latitude','longitude'),
        },
        {
            'dataset': xr.open_dataset('/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/siconc/gn/v20170928/siconc_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_201401-201412.nc'),
            'expected_latlon_names': ('lat','lon'),
        },
    ]
    for test_case in test_cases:
        actual = latlon_type.get_latlon_names(
            dataset = test_case['dataset']
        )
        assert actual == test_case['expected_latlon_names'], f"`get_latlon_names` failed on test case: {test_case}.\nExpected: {test_case['expected_latlon_names']}\nActual: {actual}"

    # Define invalid test cases
    invalid_example_dataset = make_example_dataset()
    invalid_example_dataset = invalid_example_dataset.drop_vars('latitude')
    invalid_test_cases = [
        {
            'dataset': 'invalid_dataset',
        },
        {
            'dataset': 'invalid_dataset.nc',
        },
        {
            'dataset': invalid_example_dataset,
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = latlon_type.get_latlon_names(
                dataset = invalid_test_case['dataset'],
            )
        except (FileNotFoundError, TypeError, ValueError) as e:
            assert True, f"`get_latlon_names` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`get_latlon_names` did not raise an exception on invalid test case {invalid_test_case}"
    
    # Define a list of invalid datasets
    invalid_strings = [
        1234,
        3.14,
        None,
        [],
        {}
    ]
    for invalid_string in invalid_strings:
        # Test with `dataset`
        try:
            actual = latlon_type.get_latlon_names(
                dataset = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`get_latlon_names` raised an exception on invalid `dataset`: {e}"
        else:
            assert False, f"`get_latlon_names` did not raise an exception on invalid `dataset` {invalid_string}"


def test_determine_lon_type():
    """Test the `determine_lon_type` function."""
    # Define test cases
    test_cases = [
        {
            'lon_min': 0,
            'lon_max': 0,
            'expected_lon_type': 'other',
        },
        {
            'lon_min': 3.14,
            'lon_max': 3.14,
            'expected_lon_type': 'other',
        },
        {
            'lon_min': 0,
            'lon_max': 360,
            'expected_lon_type': 'PM_centered',
        },
        {
            'lon_min': -180,
            'lon_max': 180,
            'expected_lon_type': 'IDL_centered',
        },
    ]
    for test_case in test_cases:
        actual = latlon_type.determine_lon_type(
            lon_min = test_case['lon_min'],
            lon_max = test_case['lon_max']
        )
        assert actual == test_case['expected_lon_type'], f"`determine_lon_type` failed on test case: {test_case}.\nExpected: {test_case['expected_lon_type']}\nActual: {actual}"
    
    # Define a list of invalid longitudes
    invalid_lons = [
        '180',
        '0',
        1234,
        361,
        -181,
        None,
        [],
        {}
    ]
    for invalid_lon in invalid_lons:
        # Test with `lon_min`
        try:
            actual = latlon_type.determine_lon_type(
                lon_min = invalid_lon,
                lon_max = 0,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`determine_lon_type` raised an exception on invalid `lon_min`: {e}"
        else:
            assert False, f"`determine_lon_type` did not raise an exception on invalid `lon_min` {invalid_lon}"
        # Test with `lon_max`
        try:
            actual = latlon_type.determine_lon_type(
                lon_min = 0,
                lon_max = invalid_lon,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`determine_lon_type` raised an exception on invalid `lon_max`: {e}"
        else:
            assert False, f"`determine_lon_type` did not raise an exception on invalid `lon_max` {invalid_lon}"

