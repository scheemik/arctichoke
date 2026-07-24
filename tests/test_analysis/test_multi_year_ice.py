import numpy as np 
import xarray as xr

from arctichoke import analysis
from arctichoke.dataset.example_dataset import make_example_dataset
from arctichoke.path.manipulate_paths import remove_non_empty_directory, make_file_path
from arctichoke.verify import verify_path

def test_find_multiyear_ice():
    """Test the `find_multiyear_ice` function."""
    # Create multiple example test files
    test_file_dir = 'tests/test_analysis/example_datasets'
    make_file_path(test_file_dir)
    test_file_names = [
        f"{test_file_dir}/example_dataset_0.nc",
        f"{test_file_dir}/example_dataset_1.nc",
        f"{test_file_dir}/example_dataset_2.nc",
    ]
    for test_file in test_file_names:
        make_example_dataset(
            n=3,
            test_var_name='siage',
            time_dim='time',
            time_len=2,
            save_as=test_file,
        )
    # Define test cases
    test_cases = [
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='siage',
            ),
            'multiyear_threshold': 3,
            'siage_var': 'siage',
            'save_as': None,
            'expected_sum': 6,
        },
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='siage',
            ),
            'multiyear_threshold': 3,
            'siage_var': 'siage',
            'save_as': f"{test_file_dir}/example_multiyear_0.nc",
            'expected_sum': 6,
        },
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='siage2',
            ),
            'multiyear_threshold': 3,
            'siage_var': 'siage2',
            'save_as': None,
            'expected_sum': 6,
        },
        {
            'dataset': test_file_names,
            'multiyear_threshold': 3,
            'siage_var': 'siage',
            'save_as': None,
            'expected_sum': 36,
        },
        {
            'dataset': test_file_names,
            'multiyear_threshold': 3,
            'siage_var': 'siage',
            'save_as': f"{test_file_dir}/example_multiyear_1.nc",
            'expected_sum': 36,
        },
    ]
    for test_case in test_cases:
        actual_dataset = analysis.find_multiyear_ice(
            dataset = test_case['dataset'],
            multiyear_threshold = test_case['multiyear_threshold'],
            siage_var = test_case['siage_var'],
            save_as = test_case['save_as'],
        )
        actual_sum = actual_dataset['simultiyear'].sum(skipna=True).values
        assert actual_sum == test_case['expected_sum'], f"`find_multiyear_ice` failed on test case: {test_case}.\nExpected: {test_case['expected_sum']}\nActual: {actual_sum}"
        if not isinstance(test_case['save_as'], type(None)):
            try:
                actual_save_as = verify_path(test_case['save_as'])
            except (FileNotFoundError) as e:
                assert True, f"`find_multiyear_ice` raised an exception: {e}\nExpected save file at {test_case['save_as']}"
    # Clean up test files that were created
    remove_non_empty_directory(test_file_dir)

    # Define invalid test cases
    invalid_test_cases = [
        {
            'dataset': 'invalid_dataset',
        },
        {
            'dataset': make_example_dataset(
                test_var_name='invalid_var',
            ),
        }
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = analysis.find_multiyear_ice(
                dataset = invalid_test_case['dataset'],
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`find_multiyear_ice` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`find_multiyear_ice` did not raise an exception on invalid test case {invalid_test_case}"
    
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
            actual = analysis.find_multiyear_ice(
                dataset = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`find_multiyear_ice` raised an exception on invalid `dataset`: {e}"
        else:
            assert False, f"`find_multiyear_ice` did not raise an exception on invalid `dataset` {invalid_string}"
        # Test with `siage_var`
        try:
            actual = analysis.find_multiyear_ice(
                dataset = test_cases[0]['dataset'],
                siage_var = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`find_multiyear_ice` raised an exception on invalid `siage_var`: {e}"
        else:
            assert False, f"`find_multiyear_ice` did not raise an exception on invalid `siage_var` {invalid_string}"
        # Test with `save_as`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.find_multiyear_ice(
                    dataset = test_cases[0]['dataset'],
                    save_as = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`find_multiyear_ice` raised an exception on invalid `save_as`: {e}"
            else:
                assert False, f"`find_multiyear_ice` did not raise an exception on invalid `save_as` {invalid_string}"
    # Define a list of invalid thresholds
    invalid_thresholds = [
        '1234',
        '3.14',
        None,
        [],
        {}
    ]
    for invalid_threshold in invalid_thresholds:
        # Test with `multiyear_threshold`
        try:
            actual = analysis.find_multiyear_ice(
                dataset = test_cases[0]['dataset'],
                multiyear_threshold = invalid_threshold
            )
        except (TypeError, ValueError) as e:
            assert True, f"`find_multiyear_ice` raised an exception on invalid `multiyear_threshold`: {e}"
        else:
            assert False, f"`find_multiyear_ice` did not raise an exception on invalid `multiyear_threshold` {invalid_threshold}"

def test_make_multiyear_files():
    """Test the `make_multiyear_files` function."""
    # Create multiple example test files
    test_file_dir = 'tests/test_analysis/example_datasets'
    version_id = 'v20260618'
    make_file_path(test_file_dir)
    test_file_names = {
        'siage': None,
        'siage2': None,
    }
    for si_var in test_file_names.keys():
        make_file_path(f"{test_file_dir}/{si_var}/{version_id}")
        test_file_names[si_var] = [
            f"{test_file_dir}/{si_var}/{version_id}/example_{si_var}_dataset_0.nc",
            f"{test_file_dir}/{si_var}/{version_id}/example_{si_var}_dataset_1.nc",
            f"{test_file_dir}/{si_var}/{version_id}/example_{si_var}_dataset_2.nc",
        ]
        for test_file in test_file_names[si_var]:
            make_example_dataset(
                n=4,
                test_var_name=si_var,
                time_dim='time',
                time_len=2,
                save_as=test_file,
            )
    # Define test cases
    test_cases = [
        {
            'siage_files': test_file_names['siage'][0],
            'multiyear_threshold': 4,
            'siage_var': 'siage',
            'version_id': 'v20260618',
            'expected_sum': 24,
        },
        {
            'siage_files': test_file_names['siage2'][0],
            'multiyear_threshold': 4,
            'siage_var': 'siage2',
            'version_id': 'v20260618',
            'expected_sum': 24,
        },
        {
            'siage_files': test_file_names['siage'][0],
            'multiyear_threshold': 8,
            'siage_var': 'siage',
            'version_id': 'v20260618',
            'expected_sum': 16,
        },
        {
            'siage_files': test_file_names['siage'],
            'multiyear_threshold': 4,
            'siage_var': 'siage',
            'version_id': 'v20260618',
            'expected_sum': 24,
        },
    ]
    for test_case in test_cases:
        analysis.make_multiyear_files(
            siage_files = test_case['siage_files'],
            multiyear_threshold = test_case['multiyear_threshold'],
            siage_var = test_case['siage_var'],
            version_id = test_case['version_id'],
            overwrite = True,
        )
        # Assemble expected filepath
        if not isinstance(test_case['siage_files'], type([])):
            test_case['siage_files'] = [test_case['siage_files']]
        original_version_id = test_case['siage_files'][0].split('/')[-2]
        for i in range(len(test_case['siage_files'])):
            expected_filepath = test_case['siage_files'][i].replace('siage', 'simultiyear').replace(original_version_id, test_case['version_id'])
            # Verify the filepath exists
            try:
                actual_filepath = verify_path(expected_filepath)
            except (FileNotFoundError) as e:
                assert True, f"`make_multiyear_files` raised an exception: {e}\nExpected save file at {expected_filepath}"
            # Check that the sum of the `simultiyear` variable is as expected
            actual_dataset = xr.open_dataset(actual_filepath)
            actual_sum = actual_dataset['simultiyear'].sum(skipna=True).values
            assert actual_sum == test_case['expected_sum'], f"`make_multiyear_files` failed on test case: {test_case}.\nExpected: {test_case['expected_sum']}\nActual: {actual_sum}"
            # Close the dataset so that it can be overwritten on the next loop
            actual_dataset.close()

    # Create invalid test files
    invalid_si_var = 'invalid_var'
    make_file_path(f"{test_file_dir}/{invalid_si_var}/{version_id}")
    test_file_names[invalid_si_var] = [
        f"{test_file_dir}/{invalid_si_var}/{version_id}/example_{invalid_si_var}_dataset_0.nc",
        f"{test_file_dir}/{invalid_si_var}/{version_id}/example_{invalid_si_var}_dataset_1.nc",
        f"{test_file_dir}/{invalid_si_var}/{version_id}/example_{invalid_si_var}_dataset_2.nc",
    ]
    for test_file in test_file_names[invalid_si_var]:
        make_example_dataset(
            n=4,
            test_var_name=invalid_si_var,
            time_dim='time',
            time_len=2,
            save_as=test_file,
        )
    # Define invalid test cases
    invalid_test_cases = [
        {   # Passing a string that isn't a file path
            'siage_files': 'invalid_var',
        },
        {   # Passing a file that does not exist
            'siage_files': 'invalid_var.nc',
        },
        {   # Passing a dataset with the incorrect variable
            'siage_files': test_file_names['invalid_var'][0],
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = analysis.make_multiyear_files(
                siage_files = invalid_test_case['siage_files'],
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`make_multiyear_files` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`make_multiyear_files` did not raise an exception on invalid test case {invalid_test_case}"
    
    # Define a list of invalid inputs
    invalid_strings = [
        1234,
        3.14,
        None,
        [],
        {}
    ]
    for invalid_string in invalid_strings:
        # Test with `siage_files`
        if not isinstance(invalid_string, type([])):
            try:
                actual = analysis.make_multiyear_files(
                    siage_files = invalid_string,
                )
            except (TypeError, ValueError) as e:
                assert True, f"`make_multiyear_files` raised an exception on invalid `siage_files`: {e}"
            else:
                assert False, f"`make_multiyear_files` did not raise an exception on invalid `siage_files` {invalid_string}"
        # Test with `siage_var`
        try:
            actual = analysis.make_multiyear_files(
                siage_files = test_file_names['siage'][0],
                siage_var = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_multiyear_files` raised an exception on invalid `siage_var`: {e}"
        else:
            assert False, f"`make_multiyear_files` did not raise an exception on invalid `siage_var` {invalid_string}"
        # Test with `version_id`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.make_multiyear_files(
                    siage_files = test_file_names['siage'][0],
                    version_id = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`make_multiyear_files` raised an exception on invalid `version_id`: {e}"
            else:
                assert False, f"`make_multiyear_files` did not raise an exception on invalid `version_id` {invalid_string}"
        # Test with `overwrite`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.make_multiyear_files(
                    siage_files = test_file_names['siage'][0],
                    overwrite = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`make_multiyear_files` raised an exception on invalid `overwrite`: {e}"
            else:
                assert False, f"`make_multiyear_files` did not raise an exception on invalid `overwrite` {invalid_string}"
    # Define a list of invalid `map_bbox` values
    invalid_map_bboxes = [
        'invalid',
        1234,
        3.14,
        None,
        [],
        [1],
        [1,2],
        [1,2,3],
        [1,2,3,'4'],
        [1,2,3,4,5],
        {}
    ]
    for invalid_map_bbox in invalid_map_bboxes:
        try:
            actual = analysis.make_multiyear_files(
                siage_files = invalid_string,
                map_bbox = invalid_map_bbox,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_multiyear_files` raised an exception on invalid `map_bbox`: {e}"
        else:
            assert False, f"`make_multiyear_files` did not raise an exception on invalid `map_bbox` {invalid_string}"
    # Clean up test files that were created
    remove_non_empty_directory(test_file_dir)
