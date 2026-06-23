import numpy as np 
import xarray as xr

from seaicecp import dataset
from seaicecp.dataset.example_dataset import make_example_dataset
from seaicecp.path.manipulate_paths import remove_non_empty_directory, make_file_path
from seaicecp.verify import verify_path

def test_get_min_max():
    """Test the `get_min_max` function."""
    # Create multiple example test files
    test_file_dir = 'tests/test_dataset/example_datasets'
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
            'expected_min': 0,
            'expected_max': 8,
        },
        {
            'dataset': xr.open_mfdataset(test_file_names),
            'var': 'test_var',
            'expected_min': 0,
            'expected_max': 11,
        },
        {
            'dataset': test_nan_dataset,
            'var': 'test_var',
            'expected_min': 0,
            'expected_max': 6,
        },
    ]
    for test_case in test_cases:
        actual_min, actual_max = dataset.get_min_max(
            dataset = test_case['dataset'],
            var = test_case['var'],
        )
        # Check the minimum and maximum values
        assert actual_min == test_case['expected_min'], f"`get_min_max` failed on test case: {test_case}.\nExpected min: {test_case['expected_min']}\nActual min: {actual_min}"
        assert actual_max == test_case['expected_max'], f"`get_max_max` failed on test case: {test_case}.\nExpected max: {test_case['expected_max']}\nActual max: {actual_min}"

    # Define invalid test cases
    invalid_test_cases = [
        {   # Passing a file that does not exist
            'dataset': 'invalid_dataset.nc',
        },
        {   # Passing a string that isn't a file path
            'dataset': 'invalid_dataset',
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = dataset.get_min_max(
                dataset = invalid_test_case['dataset'],
                var = 'test_var',
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`get_min_max` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`get_min_max` did not raise an exception on invalid test case {invalid_test_case}"
    
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
            actual = dataset.get_min_max(
                dataset = invalid_string,
                var = 'test_var',
            )
        except (TypeError, ValueError) as e:
            assert True, f"`get_min_max` raised an exception on invalid `dataset`: {e}"
        else:
            assert False, f"`get_min_max` did not raise an exception on invalid `dataset` {invalid_string}"
        # Test with `var`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = dataset.get_min_max(
                    dataset = test_file_names,
                    var = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`get_min_max` raised an exception on invalid `var`: {e}"
            else:
                assert False, f"`get_min_max` did not raise an exception on invalid `var` {invalid_string}"
    # Clean up test files that were created
    remove_non_empty_directory(test_file_dir)
