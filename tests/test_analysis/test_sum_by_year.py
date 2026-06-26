import numpy as np 
import xarray as xr

from seaicecp import analysis
from seaicecp.dataset.example_dataset import make_example_dataset
from seaicecp.path.manipulate_paths import remove_non_empty_directory, make_file_path
from seaicecp.verify import verify_path

def test_sum_by_year():
    """Test the `sum_by_year` function."""
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
            n=3,
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
            'save_as': None,
            'unique_years': [2026],
            'expected_sum': 72,
        },
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='test_var',
                time_axis=True,
            ),
            'save_as': f"{test_file_dir}/example_new_0.nc",
            'unique_years': [2026],
            'expected_sum': 72,
        },
        {
            'dataset': test_file_names,
            'save_as': None,
            'unique_years': [2000, 2001, 2002],
            'expected_sum': 72,
        },
        {
            'dataset': test_file_names,
            'save_as': f"{test_file_dir}/example_new_0.nc",
            'unique_years': [2000, 2001, 2002],
            'expected_sum': 72,
        },
        {
            'dataset': test_nan_dataset,
            'save_as': None,
            'unique_years': [2000, 2001, 2002],
            'expected_sum': 42,
        },
    ]
    for test_case in test_cases:
        actual_dataset = analysis.sum_by_year(
            dataset = test_case['dataset'],
            save_as = test_case['save_as'],
        )
        # Check the years present on the time axis
        actual_years = list(np.unique(actual_dataset['year'].values))
        assert actual_years == test_case['unique_years'], f"`sum_by_year` created a dataset with the unique years: {actual_years}.\nExpected unique years: {test_case['unique_years']}"
        # Check each year
        for year in actual_years:
            actual_sum = actual_dataset['test_var_year_sum'].sel(year=year).sum(skipna=True).values
            assert actual_sum == test_case['expected_sum'], f"`sum_by_year` failed on test case: {test_case}.\nExpected: {test_case['expected_sum']}\nActual: {actual_sum}"
        if not isinstance(test_case['save_as'], type(None)):
            try:
                actual_save_as = verify_path(test_case['save_as'])
            except (FileNotFoundError) as e:
                assert True, f"`sum_by_year` raised an exception: {e}\nExpected save file at {test_case['save_as']}"

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
            actual = analysis.sum_by_year(
                dataset = invalid_test_case['dataset'],
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`sum_by_year` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`sum_by_year` did not raise an exception on invalid test case {invalid_test_case}"
    
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
            actual = analysis.sum_by_year(
                dataset = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`sum_by_year` raised an exception on invalid `dataset`: {e}"
        else:
            assert False, f"`sum_by_year` did not raise an exception on invalid `dataset` {invalid_string}"
        # Test with `attr_long_name`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.sum_by_year(
                    dataset = test_cases[0]['dataset'],
                    attr_long_name = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`sum_by_year` raised an exception on invalid `attr_long_name`: {e}"
            else:
                assert False, f"`sum_by_year` did not raise an exception on invalid `attr_long_name` {invalid_string}"
        # Test with `attr_units`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.sum_by_year(
                    dataset = test_cases[0]['dataset'],
                    attr_units = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`sum_by_year` raised an exception on invalid `attr_units`: {e}"
            else:
                assert False, f"`sum_by_year` did not raise an exception on invalid `attr_units` {invalid_string}"
        # Test with `save_as`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.sum_by_year(
                    dataset = test_cases[0]['dataset'],
                    save_as = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`sum_by_year` raised an exception on invalid `save_as`: {e}"
            else:
                assert False, f"`sum_by_year` did not raise an exception on invalid `save_as` {invalid_string}"
        # Test with `verbose`
        try:
            actual = analysis.sum_by_year(
                dataset = test_cases[0]['dataset'],
                verbose = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`sum_by_year` raised an exception on invalid `verbose`: {e}"
        else:
            assert False, f"`sum_by_year` did not raise an exception on invalid `verbose` {invalid_string}"
    # Clean up test files that were created
    remove_non_empty_directory(test_file_dir)
