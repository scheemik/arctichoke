import numpy as np 
import xarray as xr

from seaicecp import analysis
from seaicecp.dataset.example_dataset import make_example_dataset
from seaicecp.path.manipulate_paths import remove_non_empty_directory, make_file_path
from seaicecp.verify import verify_path

def test_calc_sithick():
    """Test the `calc_sithick` function."""
    # Create multiple example test files
    test_file_dir = 'tests/test_analysis/example_datasets'
    make_file_path(test_file_dir)
    test_file_names = {
        'sivol': None,
        'sithick': None,
    }
    for i in range(len(test_file_names.keys())):
        si_var = list(test_file_names.keys())[i]
        test_file_names[si_var] = [
            f"{test_file_dir}/example_{si_var}_dataset_0.nc",
            f"{test_file_dir}/example_{si_var}_dataset_1.nc",
            f"{test_file_dir}/example_{si_var}_dataset_2.nc",
        ]
        for j in range(len(test_file_names[si_var])):
            make_example_dataset(
                n=3,
                test_var_name=si_var,
                time_axis=(2000+j),
                offset=i,
                save_as=test_file_names[si_var][j]
            )
    # Create the expected array
    ex_arr = np.array(
       [[    0,  100/2,  200/3],
        [300/4,  400/5,  500/6],
        [600/7,  700/8,  800/9]],
    )
    # Define test cases
    test_cases = [
        {
            'sithick_dataset': make_example_dataset(
                n=3, 
                test_var_name='sithick',
                offset=1,
            ),
            'sivol_dataset': make_example_dataset(
                n=3, 
                test_var_name='sivol',
                offset=0,
            ),
            'save_as': None,
        },
        {
            'sithick_dataset': make_example_dataset(
                n=3, 
                test_var_name='sithick',
                offset=1,
            ),
            'sivol_dataset': make_example_dataset(
                n=3, 
                test_var_name='sivol',
                offset=0,
            ),
            'save_as': f"{test_file_dir}/example_landfast_0.nc",
        },
        {
            'sithick_dataset': test_file_names['sithick'],
            'sivol_dataset': test_file_names['sivol'],
            'save_as': None,
        },
        {
            'sithick_dataset': test_file_names['sithick'],
            'sivol_dataset': test_file_names['sivol'],
            'save_as': f"{test_file_dir}/example_landfast_1.nc",
        },
    ]
    for test_case in test_cases:
        actual_dataset = analysis.calc_siconc(
            sithick_dataset = test_case['sithick_dataset'],
            sivol_dataset = test_case['sivol_dataset'],
            save_as = test_case['save_as'],
        )
        # Check the result versus the expectation
        if 'time' in list(actual_dataset.dims.keys()):
            for i in range(actual_dataset['time'].size):
                actual_array = actual_dataset['siconc2'].isel(time=i).values
                assert np.allclose(actual_array, ex_arr, equal_nan=True), f"`calc_siconc` created a dataset with the array: {actual_array} at time index [{i}].\nExpected array: {ex_arr}"
        else:
            actual_array = actual_dataset['siconc2'].values
            assert np.allclose(actual_array, ex_arr, equal_nan=True), f"`calc_siconc` created a dataset with the array: {actual_array}.\nExpected array: {ex_arr}"

    # Define invalid test cases
    invalid_test_cases = [
        {
            'sithick_dataset': 'invalid_var',
            'sivol_dataset': test_file_names['sivol'][0],
        },
        {
            'sithick_dataset': test_file_names['sithick'][0],
            'sivol_dataset': 'invalid_var',
        },
        {
            'sithick_dataset': make_example_dataset(
                n=3, 
                test_var_name='invalid_var',
                time_axis=True,
            ),
            'sivol_dataset': test_file_names['sivol'][0],
        },
        {
            'sithick_dataset': test_file_names['sithick'][0],
            'sivol_dataset': make_example_dataset(
                n=3, 
                test_var_name='invalid_var',
                time_axis=True,
            ),
        },
        {
            'sithick_dataset': make_example_dataset(
                n=4, 
                test_var_name='sithick',
            ),
            'sivol_dataset': make_example_dataset(
                n=3, 
                test_var_name='sivol',
            ),
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = analysis.calc_siconc(
                sithick_dataset = invalid_test_case['sithick_dataset'],
                sivol_dataset = invalid_test_case['sivol_dataset'],
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`calc_sithick` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`calc_sithick` did not raise an exception on invalid test case {invalid_test_case}"
    
    # Define a list of invalid inputs
    invalid_strings = [
        1234,
        3.14,
        None,
        [],
        {}
    ]
    for invalid_string in invalid_strings:
        # Test with `sithick_dataset`
        try:
            actual = analysis.calc_siconc(
                sithick_dataset = invalid_string,
                sivol_dataset = test_file_names['sivol'][0],
            )
        except (TypeError, ValueError) as e:
            assert True, f"`calc_sithick` raised an exception on invalid `sithick_dataset`: {e}"
        else:
            assert False, f"`calc_sithick` did not raise an exception on invalid `sithick_dataset` {invalid_string}"
        # Test with `sivol_dataset`
        try:
            actual = analysis.calc_siconc(
                sithick_dataset = test_file_names['sithick'][0],
                sivol_dataset = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`calc_sithick` raised an exception on invalid `sivol_dataset`: {e}"
        else:
            assert False, f"`calc_sithick` did not raise an exception on invalid `sivol_dataset` {invalid_string}"
        # Test with `save_as`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.calc_siconc(
                    sithick_dataset = test_file_names['sithick'][0],
                    sivol_dataset = test_file_names['sivol'][0],
                    save_as = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`calc_sithick` raised an exception on invalid `save_as`: {e}"
            else:
                assert False, f"`calc_sithick` did not raise an exception on invalid `save_as` {invalid_string}"
    # Clean up test files that were created
    remove_non_empty_directory(test_file_dir)

def test_make_siconc_files():
    """Test the `make_siconc_files` function."""
    # Create multiple example test files
    test_file_dir = 'tests/test_analysis/example_datasets'
    version_id = 'v20260618'
    make_file_path(test_file_dir)
    test_file_names = {
        'sivol': None,
        'sithick': None,
    }
    for i in range(len(test_file_names.keys())):
        si_var = list(test_file_names.keys())[i]
        make_file_path(f"{test_file_dir}/{si_var}/{version_id}")
        test_file_names[si_var] = [
            f"{test_file_dir}/{si_var}/{version_id}/example_{si_var}_dataset_0.nc",
            f"{test_file_dir}/{si_var}/{version_id}/example_{si_var}_dataset_1.nc",
            f"{test_file_dir}/{si_var}/{version_id}/example_{si_var}_dataset_2.nc",
        ]
        for j in range(len(test_file_names[si_var])):
            make_example_dataset(
                n=3,
                test_var_name=si_var,
                time_axis=(2000+j),
                offset=i,
                save_as=test_file_names[si_var][j]
            )
    # Create the expected array
    ex_arr = np.array(
       [[    0,  100/2,  200/3],
        [300/4,  400/5,  500/6],
        [600/7,  700/8,  800/9]],
    )
    # Define test cases
    test_cases = [
        {
            'sithick_files': test_file_names['sithick'][0],
            'sivol_files': test_file_names['sivol'][0],
            'version_id': 'v20260618',
        },
        {
            'sithick_files': test_file_names['sithick'],
            'sivol_files': test_file_names['sivol'],
            'version_id': 'v20260618',
        },
    ]
    for test_case in test_cases:
        analysis.make_siconc_files(
            sithick_files = test_case['sithick_files'],
            sivol_files = test_case['sivol_files'],
            version_id = test_case['version_id'],
            overwrite = True,
        )
        # Assemble expected filepath
        if not isinstance(test_case['sithick_files'], type([])):
            test_case['sithick_files'] = [test_case['sithick_files']]
        if not isinstance(test_case['sivol_files'], type([])):
            test_case['sivol_files'] = [test_case['sivol_files']]
        original_version_id = test_case['sithick_files'][0].split('/')[-2]
        for i in range(len(test_case['sithick_files'])):
            expected_filepath = test_case['sithick_files'][i].replace('sithick', 'siconc2').replace(original_version_id, test_case['version_id'])
            # Verify the filepath exists
            try:
                actual_filepath = verify_path(expected_filepath)
            except (FileNotFoundError) as e:
                assert True, f"`find_packed_ice` raised an exception: {e}\nExpected save file at {expected_filepath}"
            # Check that the sum of the `siconc2` variable is as expected
            actual_dataset = xr.open_dataset(actual_filepath)
            # Check the result versus the expectation
            if 'time' in list(actual_dataset.dims.keys()):
                for i in range(actual_dataset['time'].size):
                    actual_array = actual_dataset['siconc2'].isel(time=i).values
                    assert np.allclose(actual_array, ex_arr, equal_nan=True), f"`calc_siconc` created a dataset with the array: {actual_array} at time index [{i}].\nExpected array: {ex_arr}"
            else:
                actual_array = actual_dataset['siconc2'].values
                assert np.allclose(actual_array, ex_arr, equal_nan=True), f"`calc_siconc` created a dataset with the array: {actual_array}.\nExpected array: {ex_arr}"
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
            time_axis=True,
            save_as=test_file,
        )
    # Define invalid test cases
    invalid_test_cases = [
        {   # Different numbers of files for the two variables
            'sithick_files': test_file_names['sithick'],
            'sivol_files': test_file_names['sivol'][0],
        },
        {   # Passing a string that isn't a file path
            'sithick_files': 'invalid_var',
            'sivol_files': test_file_names['sivol'][0],
        },
        {   # Passing a file that does not exist
            'sithick_files': test_file_names['sithick'][0],
            'sivol_files': 'invalid_var.nc',
        },
        {   # Passing a dataset with the incorrect variable
            'sithick_files': test_file_names['invalid_var'][0],
            'sivol_files': test_file_names['sivol'][0],
        },
        {   # Passing a dataset with the incorrect variable
            'sithick_files': test_file_names['sithick'][0],
            'sivol_files': test_file_names['invalid_var'][0],
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = analysis.make_siconc_files(
                sithick_files = invalid_test_case['sithick_files'],
                sivol_files = invalid_test_case['sivol_files'],
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`make_siconc_files` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`make_siconc_files` did not raise an exception on invalid test case {invalid_test_case}"
    
    # Define a list of invalid inputs
    invalid_strings = [
        1234,
        3.14,
        None,
        [],
        {}
    ]
    for invalid_string in invalid_strings:
        # Test with `sithick_files`
        try:
            actual = analysis.make_siconc_files(
                sithick_files = invalid_string,
                sivol_files = test_file_names['sivol'][0],
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_siconc_files` raised an exception on invalid `sithick_files`: {e}"
        else:
            assert False, f"`make_siconc_files` did not raise an exception on invalid `sithick_files` {invalid_string}"
        # Test with `sivol_files`
        try:
            actual = analysis.make_siconc_files(
                sithick_files = test_file_names['sithick'][0],
                sivol_files = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_siconc_files` raised an exception on invalid `sivol_files`: {e}"
        else:
            assert False, f"`make_siconc_files` did not raise an exception on invalid `sivol_files` {invalid_string}"
        # Test with `version_id`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.make_siconc_files(
                    sithick_files = test_file_names['sithick'][0],
                    sivol_files = test_file_names['sivol'][0],
                    version_id = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`make_siconc_files` raised an exception on invalid `version_id`: {e}"
            else:
                assert False, f"`make_siconc_files` did not raise an exception on invalid `version_id` {invalid_string}"
        # Test with `overwrite`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.make_siconc_files(
                    sithick_files = test_file_names['sithick'][0],
                    sivol_files = test_file_names['sivol'][0],
                    overwrite = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`make_siconc_files` raised an exception on invalid `overwrite`: {e}"
            else:
                assert False, f"`make_siconc_files` did not raise an exception on invalid `overwrite` {invalid_string}"
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
            actual = analysis.make_siconc_files(
                sithick_files = invalid_string,
                sivol_files = test_file_names['sivol'][0],
                map_bbox = invalid_map_bbox,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_siconc_files` raised an exception on invalid `map_bbox`: {e}"
        else:
            assert False, f"`make_siconc_files` did not raise an exception on invalid `map_bbox` {invalid_string}"
    # Clean up test files that were created
    remove_non_empty_directory(test_file_dir)
