import numpy as np
import xarray as xr

from arctichoke.dataset import date_type
from arctichoke.dataset.example_dataset import make_example_dataset

def test_get_date_type():
    """Test the `get_date_type` function."""
    # Define test cases
    test_cases = [
        {
            'dataset': make_example_dataset(
                time_dim='time',
                time_len=2,
            ),
            'expected_date_type': 'datetime64[ns]',
        },
        {
            'dataset': '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201401-201412.nc',
            'expected_date_type': 'datetime64[ns]',
        },
        {
            'dataset': '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/NERC/HadGEM3-GC31-HH/hist-1950/r1i1p1f1/SImon/siconc/gn/v20210416/siconc_SImon_HadGEM3-GC31-HH_hist-1950_r1i1p1f1_gn_201401-201412.nc',
            'expected_date_type': 'cftime.Datetime360Day',
        },
        {
            'dataset': '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-HM/hist-1950/r1i1p1f1/SImon/sithick/gn/v20180730/sithick_SImon_HadGEM3-GC31-HM_hist-1950_r1i1p1f1_gn_201401-201412.nc',
            'expected_date_type': 'cftime.Datetime360Day',
        },
        {
            'dataset': '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/sithick/gn/v20170928/sithick_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_201401-201412.nc',
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

def test_get_epoch_times():
    """Test the `get_epoch_times` function."""
    # Define test cases
    test_cases = [
        {
            'dataset': make_example_dataset(
                time_dim='time',
                time_len=2,
            ),
            'expected_epoch_times': [np.float64(56.07945205479452), np.float64(56.16438356164384)],
        },
        {
            'dataset': '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201401-201412.nc',
            'expected_epoch_times': [
                np.float64(44.07260273972603),
                np.float64(44.153424657534245),
                np.float64(44.23424657534247),
                np.float64(44.31780821917808),
                np.float64(44.4013698630137),
                np.float64(44.484931506849314),
                np.float64(44.56849315068493),
                np.float64(44.653424657534245),
                np.float64(44.73698630136986),
                np.float64(44.820547945205476),
                np.float64(44.9041095890411),
                np.float64(44.987671232876714)
            ],
        },
        {
            'dataset': '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/NERC/HadGEM3-GC31-HH/hist-1950/r1i1p1f1/SImon/siconc/gn/v20210416/siconc_SImon_HadGEM3-GC31-HH_hist-1950_r1i1p1f1_gn_201401-201412.nc',
            'expected_epoch_times': [
                43.43835616438356,
                43.52054794520548,
                43.602739726027394,
                43.68493150684932,
                43.76712328767123,
                43.84931506849315,
                43.93150684931507,
                44.013698630136986,
                44.0958904109589,
                44.178082191780824,
                44.26027397260274,
                44.342465753424655
            ],
        },
        {
            'dataset': '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-HM/hist-1950/r1i1p1f1/SImon/sithick/gn/v20180730/sithick_SImon_HadGEM3-GC31-HM_hist-1950_r1i1p1f1_gn_201401-201412.nc',
            'expected_epoch_times': [
                43.43835616438356,
                43.52054794520548,
                43.602739726027394,
                43.68493150684932,
                43.76712328767123,
                43.84931506849315,
                43.93150684931507,
                44.013698630136986,
                44.0958904109589,
                44.178082191780824,
                44.26027397260274,
                44.342465753424655
            ],
        },
    ]
    for test_case in test_cases:
        actual = date_type.get_epoch_times(
            dataset = test_case['dataset']
        )
        assert actual == test_case['expected_epoch_times'], f"`get_epoch_times` failed on test case: {test_case}.\nExpected: {test_case['expected_epoch_times']}\nActual: {actual}"

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
            actual = date_type.get_epoch_times(
                dataset = invalid_test_case['dataset'],
            )
        except (FileNotFoundError, TypeError, ValueError) as e:
            assert True, f"`get_epoch_times` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`get_epoch_times` did not raise an exception on invalid test case {invalid_test_case}"
    
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
            actual = date_type.get_epoch_times(
                dataset = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`get_epoch_times` raised an exception on invalid `dataset`: {e}"
        else:
            assert False, f"`get_epoch_times` did not raise an exception on invalid `dataset` {invalid_string}"
        # Test with `time_dim`
        try:
            actual = date_type.get_epoch_times(
                dataset = test_cases[0]['dataset'],
                time_dim = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`get_epoch_times` raised an exception on invalid `time_dim`: {e}"
        else:
            assert False, f"`get_epoch_times` did not raise an exception on invalid `time_dim` {invalid_string}"

