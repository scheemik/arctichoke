import numpy as np 
import xarray as xr

from arctichoke import analysis
from arctichoke.dataset.example_dataset import make_example_dataset
from arctichoke.path.manipulate_paths import remove_non_empty_directory, make_file_path
from arctichoke.verify import verify_path

def test_calc_siage():
    """Test the `calc_siage` function."""
    # Define constant to go from years to seconds
    yr_to_s = 365 * 24 * 60 * 60
    # Create multiple example test files
    test_file_dir = 'tests/test_analysis/example_datasets'
    make_file_path(test_file_dir)
    test_file_names = [
        f"{test_file_dir}/example_siage_dataset_0.nc",
        f"{test_file_dir}/example_siage_dataset_1.nc",
        f"{test_file_dir}/example_siage_dataset_2.nc",
    ]
    for i in range(len(test_file_names)):
        make_example_dataset(
            n=3,
            test_var_name='siage',
            offset=i,
            multiplier=yr_to_s,
            time_dim='time',
            time_len=1,
            start_year=(2000+i),
            save_as=test_file_names[i]
        )
    # Define test cases
    test_cases = [
        {
            'siage_dataset': make_example_dataset(
                n=3, 
                test_var_name='siage',
                multiplier=yr_to_s,
            ),
            'save_as': None,
            'expected_array': make_example_dataset(
                n=3, 
                test_var_name='siage2',
            )['siage2'].values,
        },
        {
            'siage_dataset': make_example_dataset(
                n=3, 
                test_var_name='siage',
                multiplier=yr_to_s,
            ),
            'save_as': f"{test_file_dir}/example_siage2_0.nc",
            'expected_array': make_example_dataset(
                n=3, 
                test_var_name='siage2',
            )['siage2'].values,
        },
        {
            'siage_dataset': test_file_names,
            'save_as': f"{test_file_dir}/example_siage2_1.nc",
            'expected_array': np.array(
              [[[ 0.,  1.,  2.],
                [ 3.,  4.,  5.],
                [ 6.,  7.,  8.]],
               [[ 1.,  2.,  3.],
                [ 4.,  5.,  6.],
                [ 7.,  8.,  9.]],
               [[ 2.,  3.,  4.],
                [ 5.,  6.,  7.],
                [ 8.,  9., 10.]]]
            ),
        },
    ]
    for test_case in test_cases:
        actual_dataset = analysis.calc_siage(
            siage_dataset = test_case['siage_dataset'],
            save_as = test_case['save_as'],
        )
        # Check the result versus the expectation
        if 'time' in list(actual_dataset.dims.keys()):
            for i in range(actual_dataset['time'].size):
                actual_array = actual_dataset['siage2'].isel(time=i).values
                assert np.allclose(actual_array, test_case['expected_array'][i], equal_nan=True), f"`calc_siage` created a dataset with the array: {actual_array} at time index [{i}].\nExpected array: {test_case['expected_array']}"
        else:
            actual_array = actual_dataset['siage2'].values
            assert np.allclose(actual_array, test_case['expected_array'], equal_nan=True), f"`calc_siage` created a dataset with the array: {actual_array}.\nExpected array: {test_case['expected_array']}"

    # Define invalid test cases
    invalid_test_cases = [
        {
            'siage_dataset': 'invalid_var',
        },
        {
            'siage_dataset': make_example_dataset(
                n=3, 
                test_var_name='invalid_var',
                time_dim='time',
                time_len=2,
            ),
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = analysis.calc_siage(
                siage_dataset = invalid_test_case['siage_dataset'],
            )
        except (FileNotFoundError, KeyError) as e:
            assert True, f"`calc_siage` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`calc_siage` did not raise an exception on invalid test case {invalid_test_case}"
    
    # Define a list of invalid inputs
    invalid_strings = [
        1234,
        3.14,
        None,
        [],
        {}
    ]
    for invalid_string in invalid_strings:
        # Test with `siage_dataset`
        try:
            actual = analysis.calc_siage(
                siage_dataset = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`calc_siage` raised an exception on invalid `siage_dataset`: {e}"
        else:
            assert False, f"`calc_siage` did not raise an exception on invalid `siage_dataset` {invalid_string}"
        # Test with `save_as`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.calc_siage(
                    siage_dataset = test_file_names['siage'][0],
                    save_as = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`calc_siage` raised an exception on invalid `save_as`: {e}"
            else:
                assert False, f"`calc_siage` did not raise an exception on invalid `save_as` {invalid_string}"
        # Test with `verbose`
        try:
            actual = analysis.calc_siage(
                verbose = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`calc_siage` raised an exception on invalid `verbose`: {e}"
        else:
            assert False, f"`calc_siage` did not raise an exception on invalid `verbose` {invalid_string}"
    # Clean up test files that were created
    remove_non_empty_directory(test_file_dir)

def test_make_siage_files():
    """Test the `make_siage_files` function."""
    # Define constant to go from years to seconds
    yr_to_s = 365 * 24 * 60 * 60
    # Create multiple example test files
    test_file_dir = 'tests/test_analysis/example_datasets'
    version_id = 'v20260618'
    make_file_path(test_file_dir)
    make_file_path(f"{test_file_dir}/siage/{version_id}")
    test_file_names = { 'siage': [
        f"{test_file_dir}/siage/{version_id}/example_siage_dataset_0.nc",
        f"{test_file_dir}/siage/{version_id}/example_siage_dataset_1.nc",
        f"{test_file_dir}/siage/{version_id}/example_siage_dataset_2.nc",
    ]}
    for i in range(len(test_file_names['siage'])):
        make_example_dataset(
            n=3,
            test_var_name='siage',
            offset=i,
            multiplier=yr_to_s,
            time_dim='time',
            time_len=1,
            start_year=(2000+i),
            save_as=test_file_names['siage'][i]
        )
    # Create the expected array
    ex_arr = np.array(
      [[[ 0.,  1.,  2.],
        [ 3.,  4.,  5.],
        [ 6.,  7.,  8.]],
       [[ 1.,  2.,  3.],
        [ 4.,  5.,  6.],
        [ 7.,  8.,  9.]],
       [[ 2.,  3.,  4.],
        [ 5.,  6.,  7.],
        [ 8.,  9., 10.]]]
    )
    # Define test cases
    test_cases = [
        {
            'siage_files': test_file_names['siage'][0],
            'version_id': 'v20260618',
            'expected_array': [ex_arr[0]],
        },
        {
            'siage_files': test_file_names['siage'],
            'version_id': 'v20260618',
            'expected_array': ex_arr,
        },
    ]
    for test_case in test_cases:
        analysis.make_siage_files(
            siage_files = test_case['siage_files'],
            version_id = test_case['version_id'],
            overwrite = True,
        )
        # Assemble expected filepath
        if not isinstance(test_case['siage_files'], type([])):
            test_case['siage_files'] = [test_case['siage_files']]
        original_version_id = test_case['siage_files'][0].split('/')[-2]
        for i in range(len(test_case['siage_files'])):
            expected_filepath = test_case['siage_files'][i].replace('siage', 'siage2').replace(original_version_id, test_case['version_id'])
            # Verify the filepath exists
            try:
                actual_filepath = verify_path(expected_filepath)
            except (FileNotFoundError) as e:
                assert True, f"`make_siage_files` raised an exception: {e}\nExpected save file at {expected_filepath}"
            # Check that the sum of the `siage2` variable is as expected
            actual_dataset = xr.open_dataset(actual_filepath)
            # Check the result versus the expectation
            actual_array = actual_dataset['siage2'].values
            assert np.allclose(actual_array, test_case['expected_array'][i], equal_nan=True), f"`calc_siage` created a dataset with the array: {actual_array}.\nExpected array: {test_case['expected_array']}"
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
        {   # Passing a multi-file dataset with the incorrect variable
            'siage_files': test_file_names['invalid_var'],
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = analysis.make_siage_files(
                siage_files = invalid_test_case['siage_files'],
            )
        except (FileNotFoundError, KeyError) as e:
            assert True, f"`make_siage_files` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`make_siage_files` did not raise an exception on invalid test case {invalid_test_case}"
    
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
                actual = analysis.make_siage_files(
                    siage_files = invalid_string,
                )
            except (TypeError, ValueError) as e:
                assert True, f"`make_siage_files` raised an exception on invalid `siage_files`: {e}"
            else:
                assert False, f"`make_siage_files` did not raise an exception on invalid `siage_files` {invalid_string}"
        # Test with `version_id`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.make_siage_files(
                    siage_files = test_file_names['siage'][0],
                    version_id = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`make_siage_files` raised an exception on invalid `version_id`: {e}"
            else:
                assert False, f"`make_siage_files` did not raise an exception on invalid `version_id` {invalid_string}"
        # Test with `overwrite`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.make_siage_files(
                    siage_files = test_file_names['siage'][0],
                    overwrite = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`make_siage_files` raised an exception on invalid `overwrite`: {e}"
            else:
                assert False, f"`make_siage_files` did not raise an exception on invalid `overwrite` {invalid_string}"
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
            actual = analysis.make_siage_files(
                siage_files = invalid_string,
                map_bbox = invalid_map_bbox,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_siage_files` raised an exception on invalid `map_bbox`: {e}"
        else:
            assert False, f"`make_siage_files` did not raise an exception on invalid `map_bbox` {invalid_string}"
    # Clean up test files that were created
    remove_non_empty_directory(test_file_dir)
