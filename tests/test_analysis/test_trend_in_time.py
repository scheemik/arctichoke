import numpy as np 
import xarray as xr

from seaicecp import analysis
from seaicecp.dataset.example_dataset import make_example_dataset
from seaicecp.path.manipulate_paths import remove_non_empty_directory, make_file_path
from seaicecp.verify import verify_path

def test_trend_in_time():
    """Test the `trend_in_time` function."""
    # Create multiple example test files
    test_file_dir = 'tests/test_analysis/example_datasets'
    make_file_path(test_file_dir)
    test_file_names = [
        f"{test_file_dir}/example_dataset_0.nc",
        f"{test_file_dir}/example_dataset_1.nc",
        f"{test_file_dir}/example_dataset_2.nc",
    ]
    offsets = [0, 1, 3]
    for i in range(len(test_file_names)):
        make_example_dataset(
            n=3,
            offset=offsets[i],
            test_var_name='test_var',
            time_axis=(2000+i),
            save_as=test_file_names[i],
        )
    # Create test case with `nan` values
    test_nan_dataset = xr.open_mfdataset(test_file_names)
    test_nan_dataset['test_var'] = test_nan_dataset['test_var'].where(
        lambda val:
            (test_nan_dataset['test_var'] < 7),
        lambda val: np.nan
    )
    # Define test cases
    test_cases = [
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='test_var',
                time_axis=True,
            ),
            'var': 'test_var',
            'time_dim': 'time',
            'save_as': None,
            'atol': 1e-12,
            'expected_trends': [0],
        },
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='test_var',
                time_axis=True,
            ),
            'var': 'test_var',
            'time_dim': 'time',
            'save_as': f"{test_file_dir}/example_new_0.nc",
            'atol': 1e-12,
            'expected_trends': [0],
        },
        {
            'dataset': test_file_names,
            'var': 'test_var',
            'time_dim': 'time',
            'save_as': None,
            'atol': 1e-4,
            'expected_trends': [1.49368],
        },
        {
            'dataset': test_file_names,
            'var': 'test_var',
            'time_dim': 'time',
            'atol': 1e-4,
            'save_as': f"{test_file_dir}/example_new_1.nc",
            'expected_trends': [1.49368],
        },
        {
            'dataset': test_nan_dataset,
            'var': 'test_var',
            'time_dim': 'time',
            'atol': 1e-4,
            'save_as': None,
            'expected_trends': [1.49368, np.nan],
        },
    ]
    for test_case in test_cases:
        actual_dataset = analysis.trend_in_time(
            dataset = test_case['dataset'],
            var = test_case['var'],
            time_dim = test_case['time_dim'],
            save_as = test_case['save_as'],
        )
        # Check the trends present on the time axis
        actual_trends = list(np.unique(actual_dataset[f'{test_case['var']}_trends'].values))
        for actual_trend in actual_trends:
            isclose = False
            for expected_trend in test_case['expected_trends']:
                if np.isclose(actual_trend, expected_trend, atol=test_case['atol'], equal_nan=True):
                    isclose = True
            if isclose == False:
                assert False, f"`trend_in_time` created a dataset with the unique trends: {actual_trends}.\nExpected unique trends: {test_case['expected_trends']}"
        if not isinstance(test_case['save_as'], type(None)):
            try:
                actual_save_as = verify_path(test_case['save_as'])
            except (FileNotFoundError) as e:
                assert True, f"`trend_in_time` raised an exception: {e}\nExpected save file at {test_case['save_as']}"

    # Create differently sized example file
    odd_size_example = f"{test_file_dir}/example_dataset_3.nc"
    make_example_dataset(
        n=6,
        test_var_name='test_var',
        time_axis=1999,
        save_as=odd_size_example,
    )
    # Define invalid test cases
    invalid_test_cases = [
        {   # Passing a file that does not exist
            'dataset': 'invalid_dataset.nc',
        },
        {   # Passing a string that isn't a file path
            'dataset': 'invalid_dataset',
        },
        # {   # Passing a list of files that don't have the same dimensions
        #     'dataset': test_file_names + [odd_size_example],
        # },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = analysis.trend_in_time(
                dataset = invalid_test_case['dataset'],
                var = 'test_var',
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`trend_in_time` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`trend_in_time` did not raise an exception on invalid test case {invalid_test_case}"
    
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
            actual = analysis.trend_in_time(
                dataset = invalid_string,
                var = 'test_var',
            )
        except (TypeError, ValueError) as e:
            assert True, f"`trend_in_time` raised an exception on invalid `dataset`: {e}"
        else:
            assert False, f"`trend_in_time` did not raise an exception on invalid `dataset` {invalid_string}"
        # Test with `var`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.trend_in_time(
                    dataset = test_file_names,
                    var = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`trend_in_time` raised an exception on invalid `var`: {e}"
            else:
                assert False, f"`trend_in_time` did not raise an exception on invalid `var` {invalid_string}"
        # Test with `time_dim`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.trend_in_time(
                    dataset = test_file_names,
                    var = 'test_var',
                    time_dim = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`trend_in_time` raised an exception on invalid `time_dim`: {e}"
            else:
                assert False, f"`trend_in_time` did not raise an exception on invalid `time_dim` {invalid_string}"
        # Test with `save_as`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.trend_in_time(
                    dataset = test_file_names,
                    var = 'test_var',
                    save_as = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`trend_in_time` raised an exception on invalid `save_as`: {e}"
            else:
                assert False, f"`trend_in_time` did not raise an exception on invalid `save_as` {invalid_string}"
        # Test with `verbose`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.trend_in_time(
                    dataset = test_file_names,
                    var = 'test_var',
                    verbose = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`trend_in_time` raised an exception on invalid `verbose`: {e}"
            else:
                assert False, f"`trend_in_time` did not raise an exception on invalid `verbose` {invalid_string}"
    # Clean up test files that were created
    remove_non_empty_directory(test_file_dir)
