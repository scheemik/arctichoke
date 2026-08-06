import numpy as np 
import xarray as xr

from arctichoke import analysis
from arctichoke.dataset.example_dataset import make_example_dataset
from arctichoke.path.manipulate_paths import remove_non_empty_directory, make_file_path
from arctichoke.verify import verify_path

def test_sum_by_month():
    """Test the `sum_by_month` function."""
    # Create multiple example test files
    test_file_dir = 'tests/test_analysis/example_datasets'
    make_file_path(test_file_dir)
    test_file_names = [
        f"{test_file_dir}/example_dataset_0.nc",
        f"{test_file_dir}/example_dataset_1.nc",
        f"{test_file_dir}/example_dataset_2.nc",
    ]
    for i in range(len(test_file_names)):
        make_example_dataset(
            n=2,
            test_var_name='test_var',
            time_dim='time',
            time_len=12,
            start_year=(2000+i),
            offset=i,
            save_as=test_file_names[i],
        )
    # Create test case with `nan` values
    test_nan_dataset = xr.open_mfdataset(test_file_names)
    test_nan_dataset['test_var'] = test_nan_dataset['test_var'].where(
        lambda val:
            (test_nan_dataset['test_var'] < 3),
        lambda val: np.nan
    )
    # Create multiple example test files with differing numbers of months
    test_file_names_diff = [
        f"{test_file_dir}/example_dataset_a.nc",
        f"{test_file_dir}/example_dataset_b.nc",
        f"{test_file_dir}/example_dataset_c.nc",
    ]
    for i in range(len(test_file_names_diff)):
        make_example_dataset(
            n=2,
            test_var_name='test_var',
            time_dim='time',
            time_len=i+2,
            start_year=(2000+i),
            offset=i,
            save_as=test_file_names_diff[i],
        )
    # Create test case with `nan` values for differing values of months
    test_nan_dataset_diff = xr.open_mfdataset(test_file_names_diff)
    test_nan_dataset_diff['test_var'] = test_nan_dataset_diff['test_var'].where(
        lambda val:
            (test_nan_dataset_diff['test_var'] < 3),
        lambda val: np.nan
    )
    # Define test cases
    test_cases = [
        {
            'dataset': make_example_dataset(
                n=2, 
                test_var_name='test_var',
                time_dim='time',
                time_len=2,
            ),
            'find_mean': False,
            'save_as': None,
            'unique_months': [1,2],
            'expected_values': [
               [[0, 1,],
                [2, 3,],]
            ],
        },
        {
            'dataset': make_example_dataset(
                n=2, 
                test_var_name='test_var',
                time_dim='time',
                time_len=2,
            ),
            'find_mean': False,
            'save_as': f"{test_file_dir}/example_new_0.nc",
            'unique_months': [1,2],
            'expected_values': [
               [[0, 1,],
                [2, 3,],]
            ],
        },
        {
            'dataset': test_file_names,
            'find_mean': False,
            'save_as': None,
            'unique_months': [1,2,3,4,5,6,7,8,9,10,11,12],
            'expected_values': [
               [[3, 6,],
                [9, 12,],]
            ],
        },
        {
            'dataset': test_file_names,
            'find_mean': True,
            'save_as': None,
            'unique_months': [1,2,3,4,5,6,7,8,9,10,11,12],
            'expected_values': [
               [[1, 2,],
                [3, 4,],]
            ],
        },
        {
            'dataset': test_nan_dataset,
            'find_mean': False,
            'save_as': None,
            'unique_months': [1,2,3,4,5,6,7,8,9,10,11,12],
            'expected_values': [
               [[3, 3,],
                [2, np.nan,],]
            ],
        },
        {
            'dataset': test_nan_dataset,
            'find_mean': True,
            'save_as': None,
            'unique_months': [1,2,3,4,5,6,7,8,9,10,11,12],
            'expected_values': [
               [[1, 1.5,],
                [2, np.nan,],],
            ],
        },
        {
            'dataset': test_file_names_diff,
            'find_mean': False,
            'save_as': None,
            'unique_months': [1,2,3,4],
            'expected_values': [
               [[3, 6,],
                [9, 12,],],
               [[3, 5,],
                [7, 9,],],
               [[2, 3,],
                [4, 5,],],
            ],
        },
        {
            'dataset': test_file_names_diff,
            'find_mean': True,
            'save_as': None,
            'unique_months': [1,2,3,4],
            'expected_values': [
               [[1, 2,],
                [3, 4,],],
               [[1.5, 2.5,],
                [3.5, 4.5,],],
               [[2, 3,],
                [4, 5,],],
            ],
        },
        {
            'dataset': test_nan_dataset_diff,
            'find_mean': False,
            'save_as': None,
            'unique_months': [1,2,3,4],
            'expected_values': [
               [[3,      3,],
                [2,      np.nan,],],
               [[3,      2,],
                [np.nan, np.nan,],],
               [[2,      np.nan,],
                [np.nan, np.nan,],],
            ],
        },
        {
            'dataset': test_nan_dataset_diff,
            'find_mean': True,
            'save_as': None,
            'unique_months': [1,2,3,4],
            'expected_values': [
               [[1,      1.5,],
                [2,      np.nan,],],
               [[1.5,    2,],
                [np.nan, np.nan,],],
               [[2,      np.nan,],
                [np.nan, np.nan,],],
            ],
        },
    ]
    for test_case in test_cases:
        actual_dataset = analysis.sum_by_month(
            dataset = test_case['dataset'],
            find_mean = test_case['find_mean'],
            save_as = test_case['save_as'],
        )
        # Check the months present on the time axis
        actual_months = list(np.unique(actual_dataset['month'].values))
        assert actual_months == test_case['unique_months'], f"`sum_by_month` created a dataset with the unique months: {actual_months}.\nExpected unique months: {test_case['unique_months']}"
        # Get the name of the new variable
        if test_case['find_mean']:
            new_var = 'test_var_month_mean'
        else:
            new_var = 'test_var_month_sum'
        # Check each month
        for i in range(len(actual_months)):
            actual_values = actual_dataset[new_var].sel(month=actual_months[i]).values
            match_found = False
            j = 0
            while match_found == False and j < len(test_case['expected_values']):
                if np.array_equal(actual_values, test_case['expected_values'][j], equal_nan=True):
                    match_found = True
                j += 1
            assert match_found, f"`sum_by_month` failed on test case: {test_case}.\nExpected values: \n{test_case['expected_values']}\nActual values {i}: \n{actual_values}"
        if not isinstance(test_case['save_as'], type(None)):
            try:
                actual_save_as = verify_path(test_case['save_as'])
            except (FileNotFoundError) as e:
                assert True, f"`sum_by_month` raised an exception: {e}\nExpected save file at {test_case['save_as']}"

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
            actual = analysis.sum_by_month(
                dataset = invalid_test_case['dataset'],
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`sum_by_month` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`sum_by_month` did not raise an exception on invalid test case {invalid_test_case}"
    
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
            actual = analysis.sum_by_month(
                dataset = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`sum_by_month` raised an exception on invalid `dataset`: {e}"
        else:
            assert False, f"`sum_by_month` did not raise an exception on invalid `dataset` {invalid_string}"
        # Test with `attr_long_name`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.sum_by_month(
                    dataset = test_cases[0]['dataset'],
                    attr_long_name = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`sum_by_month` raised an exception on invalid `attr_long_name`: {e}"
            else:
                assert False, f"`sum_by_month` did not raise an exception on invalid `attr_long_name` {invalid_string}"
        # Test with `attr_units`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.sum_by_month(
                    dataset = test_cases[0]['dataset'],
                    attr_units = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`sum_by_month` raised an exception on invalid `attr_units`: {e}"
            else:
                assert False, f"`sum_by_month` did not raise an exception on invalid `attr_units` {invalid_string}"
        # Test with `save_as`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.sum_by_month(
                    dataset = test_cases[0]['dataset'],
                    save_as = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`sum_by_month` raised an exception on invalid `save_as`: {e}"
            else:
                assert False, f"`sum_by_month` did not raise an exception on invalid `save_as` {invalid_string}"
        # Test with `find_mean`
        try:
            actual = analysis.sum_by_month(
                dataset = test_cases[0]['dataset'],
                find_mean = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`sum_by_month` raised an exception on invalid `find_mean`: {e}"
        else:
            assert False, f"`sum_by_month` did not raise an exception on invalid `find_mean` {invalid_string}"
        # Test with `verbose`
        try:
            actual = analysis.sum_by_month(
                dataset = test_cases[0]['dataset'],
                verbose = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`sum_by_month` raised an exception on invalid `verbose`: {e}"
        else:
            assert False, f"`sum_by_month` did not raise an exception on invalid `verbose` {invalid_string}"
    # Clean up test files that were created
    remove_non_empty_directory(test_file_dir)
