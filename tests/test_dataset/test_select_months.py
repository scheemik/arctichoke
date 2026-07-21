import numpy as np 
import xarray as xr

from arctichoke import dataset
from arctichoke.analysis import sum_by_year
from arctichoke.dataset import make_example_dataset
from arctichoke.verify import verify_path

def test_select_months():
    """Test the `select_months` function."""
    # Create test case with many months from which to select seasons
    this_year = 2026
    n_years = 3
    test_seasons = make_example_dataset(
        n = 2,
        time_dim = 'time',
        time_len = 12*n_years,
        start_year = this_year,
    )
    # Define test cases
    test_cases = [
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='test_var',
                time_dim='time',
                time_len=2,
            ),
            'months': [1,2,3,4,5,6,7,8,9,10,11,12],
            'expected_length': 2,
        },
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='test_var',
                time_dim='time',
                time_len=2,
            ),
            'months': [1],
            'expected_length': 1,
        },
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='test_var',
                time_dim='time',
                time_len=2,
            ),
            'months': [3],
            'expected_length': 0,
        },
        {
            'dataset': test_seasons,
            'months': [1,2,3,4,5,6,7,8,9,10,11,12],
            'expected_length': 12*n_years,
        },
        {
            'dataset': test_seasons,
            'months': [6,7,8,9,10],
            'expected_length': 5*n_years,
        },
    ]
    for test_case in test_cases:
        actual_dataset = dataset.select_months(
            dataset = test_case['dataset'],
            months = test_case['months'],
        )
        # Check the length of the time axis
        actual_length = actual_dataset['time'].size
        assert actual_length == test_case['expected_length'], f"`select_months` created a dataset with a `time` axis of length: {actual_length}.\nExpected length: {test_case['expected_length']}"

    # Create an example dataset without a `time` axis
    invaild_ds_no_time = make_example_dataset(
        n=2,
        test_var_name='test_var',
        time_dim=None,
    )
    # Take the sum by year of the example dataset
    invalid_ds_year = sum_by_year(test_seasons)
    # Define invalid test cases
    invalid_test_cases = [
        {   # Passing a file that does not exist
            'dataset': 'invalid_dataset.nc',
        },
        {   # Passing a string that isn't a file path
            'dataset': 'invalid_dataset',
        },
        {   # Passing a dataset without a `time` dimension
            'dataset': invaild_ds_no_time,
        },
        {   # Passing a dataset with a `year` dimension
            'dataset': invalid_ds_year,
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = dataset.select_months(
                dataset = invalid_test_case['dataset'],
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`select_months` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`select_months` did not raise an exception on invalid test case {invalid_test_case}"
    
    # Define a list of invalid inputs
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
            actual = dataset.select_months(
                dataset = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`select_months` raised an exception on invalid `dataset`: {e}"
        else:
            assert False, f"`select_months` did not raise an exception on invalid `dataset` {invalid_string}"
        # Test with `months`
        if not isinstance(invalid_string, int):
            try:
                actual = dataset.select_months(
                    dataset = test_cases[0]['dataset'],
                    months = invalid_string,
                )
            except (TypeError, ValueError) as e:
                assert True, f"`select_months` raised an exception on invalid `months`: {e}"
            else:
                assert False, f"`select_months` did not raise an exception on invalid `months` {invalid_string}"
        # Test with `verbose`
        try:
            actual = dataset.select_months(
                dataset = test_cases[0]['dataset'],
                var = 'test_var',
                time_dim = 'time',
                verbose = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`select_months` raised an exception on invalid `verbose`: {e}"
        else:
            assert False, f"`select_months` did not raise an exception on invalid `verbose` {invalid_string}"
