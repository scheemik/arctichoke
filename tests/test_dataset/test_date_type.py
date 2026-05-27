import xarray as xr

from seaicecp.dataset import date_type
from seaicecp.dataset.example_dataset import make_example_dataset

def test_get_date_type():
    """Test the `get_date_type` function."""
    # Define test cases
    test_cases = [
        {
            'dataset': make_example_dataset(time_axis=True),
            'expected_date_type': 'datetime64[ns]',
        },
        {
            'dataset': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201401-201412.nc',
            'expected_date_type': 'datetime64[ns]',
        },
        {
            'dataset': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/NERC/HadGEM3-GC31-HH/hist-1950/r1i1p1f1/SImon/siconc/gn/v20210416/siconc_SImon_HadGEM3-GC31-HH_hist-1950_r1i1p1f1_gn_201401-201412.nc',
            'expected_date_type': 'cftime.Datetime360Day',
        },
        {
            'dataset': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-HM/hist-1950/r1i1p1f1/SImon/sithick/gn/v20180730/sithick_SImon_HadGEM3-GC31-HM_hist-1950_r1i1p1f1_gn_201401-201412.nc',
            'expected_date_type': 'cftime.Datetime360Day',
        },
        {
            'dataset': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/sithick/gn/v20170928/sithick_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_201401-201412.nc',
            'expected_date_type': 'cftime.Datetime360Day',
        },
    ]
    for test_case in test_cases:
        actual = date_type.get_date_type(
            dataset = test_case['dataset']
        )
        assert actual == test_case['expected_date_type'], f"`get_date_type` failed on test case: {test_case}.\nExpected: {test_case['expected_date_type']}\nActual: {actual}"

    # Define invalid test cases
    invalid_example_dataset = make_example_dataset()
    invalid_example_dataset['test_var2'] = invalid_example_dataset['test_var']
    invalid_test_cases = [
        {
            'dataset': 'invalid_dataset',
        },
        {
            'dataset': 'invalid_dataset.nc',
        },
        {
            'dataset': make_example_dataset(),
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = date_type.get_date_type(
                dataset = invalid_test_case['dataset'],
            )
        except (FileNotFoundError, TypeError, ValueError) as e:
            assert True, f"`get_date_type` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`get_date_type` did not raise an exception on invalid test case {invalid_test_case}"
    
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
            actual = date_type.get_date_type(
                dataset = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`get_date_type` raised an exception on invalid `dataset`: {e}"
        else:
            assert False, f"`get_date_type` did not raise an exception on invalid `dataset` {invalid_string}"
