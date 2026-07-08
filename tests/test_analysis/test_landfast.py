import numpy as np 
import xarray as xr

from seaicecp import analysis
from seaicecp.dataset.example_dataset import make_example_dataset
from seaicecp.path.manipulate_paths import remove_non_empty_directory, make_file_path
from seaicecp.verify import verify_path

def test_find_packed_ice():
    """Test the `find_packed_ice` function."""
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
            test_var_name='siconc',
            time_axis=True,
            save_as=test_file,
        )
    # Define test cases
    test_cases = [
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='siconc',
            ),
            'packed_threshold': 3,
            'siconc_var': 'siconc',
            'save_as': None,
            'expected_sum': 6,
        },
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='siconc',
            ),
            'packed_threshold': 3,
            'siconc_var': 'siconc',
            'save_as': f"{test_file_dir}/example_landfast_0.nc",
            'expected_sum': 6,
        },
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='siconc2',
            ),
            'packed_threshold': 3,
            'siconc_var': 'siconc2',
            'save_as': None,
            'expected_sum': 6,
        },
        {
            'dataset': test_file_names,
            'packed_threshold': 3,
            'siconc_var': 'siconc',
            'save_as': None,
            'expected_sum': 36,
        },
        {
            'dataset': test_file_names,
            'packed_threshold': 3,
            'siconc_var': 'siconc',
            'save_as': f"{test_file_dir}/example_landfast_1.nc",
            'expected_sum': 36,
        },
    ]
    for test_case in test_cases:
        actual_dataset = analysis.find_packed_ice(
            dataset = test_case['dataset'],
            packed_threshold = test_case['packed_threshold'],
            siconc_var = test_case['siconc_var'],
            save_as = test_case['save_as'],
        )
        actual_sum = actual_dataset['sipacked'].sum(skipna=True).values
        assert actual_sum == test_case['expected_sum'], f"`find_packed_ice` failed on test case: {test_case}.\nExpected: {test_case['expected_sum']}\nActual: {actual_sum}"
        if not isinstance(test_case['save_as'], type(None)):
            try:
                actual_save_as = verify_path(test_case['save_as'])
            except (FileNotFoundError) as e:
                assert True, f"`find_packed_ice` raised an exception: {e}\nExpected save file at {test_case['save_as']}"
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
            actual = analysis.find_packed_ice(
                dataset = invalid_test_case['dataset'],
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`find_packed_ice` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`find_packed_ice` did not raise an exception on invalid test case {invalid_test_case}"
    
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
            actual = analysis.find_packed_ice(
                dataset = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`find_packed_ice` raised an exception on invalid `dataset`: {e}"
        else:
            assert False, f"`find_packed_ice` did not raise an exception on invalid `dataset` {invalid_string}"
        # Test with `siconc_var`
        try:
            actual = analysis.find_packed_ice(
                dataset = test_cases[0]['dataset'],
                siconc_var = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`find_packed_ice` raised an exception on invalid `siconc_var`: {e}"
        else:
            assert False, f"`find_packed_ice` did not raise an exception on invalid `siconc_var` {invalid_string}"
        # Test with `save_as`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.find_packed_ice(
                    dataset = test_cases[0]['dataset'],
                    save_as = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`find_packed_ice` raised an exception on invalid `save_as`: {e}"
            else:
                assert False, f"`find_packed_ice` did not raise an exception on invalid `save_as` {invalid_string}"
    # Define a list of invalid thresholds
    invalid_thresholds = [
        '1234',
        '3.14',
        None,
        [],
        {}
    ]
    for invalid_threshold in invalid_thresholds:
        # Test with `packed_threshold`
        try:
            actual = analysis.find_packed_ice(
                dataset = test_cases[0]['dataset'],
                packed_threshold = invalid_threshold
            )
        except (TypeError, ValueError) as e:
            assert True, f"`find_packed_ice` raised an exception on invalid `packed_threshold`: {e}"
        else:
            assert False, f"`find_packed_ice` did not raise an exception on invalid `packed_threshold` {invalid_threshold}"

def test_find_slow_ice():
    """Test the `find_slow_ice` function."""
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
            test_var_name='sispeed',
            time_axis=True,
            save_as=test_file,
        )
    # Define test cases
    test_cases = [
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='sispeed',
            ),
            'slow_threshold': 3,
            'save_as': None,
            'expected_sum': 4,
        },
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='sispeed',
            ),
            'slow_threshold': 3,
            'save_as': f"{test_file_dir}/example_landfast_0.nc",
            'expected_sum': 4,
        },
        {
            'dataset': test_file_names,
            'slow_threshold': 3,
            'save_as': None,
            'expected_sum': 24,
        },
        {
            'dataset': test_file_names,
            'slow_threshold': 3,
            'save_as': f"{test_file_dir}/example_landfast_1.nc",
            'expected_sum': 24,
        },
    ]
    for test_case in test_cases:
        actual_dataset = analysis.find_slow_ice(
            dataset = test_case['dataset'],
            slow_threshold = test_case['slow_threshold'],
            save_as = test_case['save_as'],
        )
        actual_sum = actual_dataset['sislow'].sum(skipna=True).values
        assert actual_sum == test_case['expected_sum'], f"`find_slow_ice` failed on test case: {test_case}.\nExpected: {test_case['expected_sum']}\nActual: {actual_sum}"
        if not isinstance(test_case['save_as'], type(None)):
            try:
                actual_save_as = verify_path(test_case['save_as'])
            except (FileNotFoundError) as e:
                assert True, f"`find_packed_ice` raised an exception: {e}\nExpected save file at {test_case['save_as']}"
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
            actual = analysis.find_slow_ice(
                dataset = invalid_test_case['dataset'],
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`find_slow_ice` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`find_slow_ice` did not raise an exception on invalid test case {invalid_test_case}"
    
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
            actual = analysis.find_slow_ice(
                dataset = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`find_slow_ice` raised an exception on invalid `dataset`: {e}"
        else:
            assert False, f"`find_slow_ice` did not raise an exception on invalid `dataset` {invalid_string}"
        # Test with `save_as`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.find_slow_ice(
                    dataset = test_cases[0]['dataset'],
                    save_as = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`find_slow_ice` raised an exception on invalid `save_as`: {e}"
            else:
                assert False, f"`find_slow_ice` did not raise an exception on invalid `save_as` {invalid_string}"
    # Define a list of invalid thresholds
    invalid_thresholds = [
        '1234',
        '3.14',
        None,
        [],
        {}
    ]
    for invalid_threshold in invalid_thresholds:
        # Test with `slow_threshold`
        try:
            actual = analysis.find_slow_ice(
                dataset = test_cases[0]['dataset'],
                slow_threshold = invalid_threshold
            )
        except (TypeError, ValueError) as e:
            assert True, f"`find_slow_ice` raised an exception on invalid `slow_threshold`: {e}"
        else:
            assert False, f"`find_slow_ice` did not raise an exception on invalid `slow_threshold` {invalid_threshold}"

def test_find_landfast_ice():
    """Test the `find_landfast_ice` function."""
    # Create multiple example test files
    test_file_dir = 'tests/test_analysis/example_datasets'
    make_file_path(test_file_dir)
    test_file_names = {
        'siconc': None,
        'sispeed': None,
    }
    for si_var in test_file_names.keys():
        test_file_names[si_var] = [
            f"{test_file_dir}/example_{si_var}_dataset_0.nc",
            f"{test_file_dir}/example_{si_var}_dataset_1.nc",
            f"{test_file_dir}/example_{si_var}_dataset_2.nc",
        ]
        for test_file in test_file_names[si_var]:
            make_example_dataset(
                n=3,
                test_var_name=si_var,
                time_axis=True,
                save_as=test_file,
            )
    # Define test cases
    test_cases = [
        {
            'siconc_dataset': make_example_dataset(
                n=3, 
                test_var_name='siconc',
            ),
            'sispeed_dataset': make_example_dataset(
                n=3, 
                test_var_name='sispeed',
            ),
            'packed_threshold': 4,
            'slow_threshold': 4,
            'siconc_var': 'siconc',
            'save_as': None,
            'expected_sum': 1,
        },
        {
            'siconc_dataset': make_example_dataset(
                n=3, 
                test_var_name='siconc',
            ),
            'sispeed_dataset': make_example_dataset(
                n=3, 
                test_var_name='sispeed',
            ),
            'packed_threshold': 4,
            'slow_threshold': 4,
            'siconc_var': 'siconc',
            'save_as': f"{test_file_dir}/example_landfast_0.nc",
            'expected_sum': 1,
        },
        {
            'siconc_dataset': make_example_dataset(
                n=3, 
                test_var_name='siconc2',
            ),
            'sispeed_dataset': make_example_dataset(
                n=3, 
                test_var_name='sispeed',
            ),
            'packed_threshold': 4,
            'slow_threshold': 4,
            'siconc_var': 'siconc2',
            'save_as': None,
            'expected_sum': 1,
        },
        {
            'siconc_dataset': test_file_names['siconc'],
            'sispeed_dataset': test_file_names['sispeed'],
            'packed_threshold': 4,
            'slow_threshold': 4,
            'siconc_var': 'siconc',
            'save_as': None,
            'expected_sum': 6,
        },
        {
            'siconc_dataset': test_file_names['siconc'],
            'sispeed_dataset': test_file_names['sispeed'],
            'packed_threshold': 4,
            'slow_threshold': 4,
            'siconc_var': 'siconc',
            'save_as': f"{test_file_dir}/example_landfast_1.nc",
            'expected_sum': 6,
        },
    ]
    for test_case in test_cases:
        actual_dataset = analysis.find_landfast_ice(
            siconc_dataset = test_case['siconc_dataset'],
            sispeed_dataset = test_case['sispeed_dataset'],
            packed_threshold = test_case['packed_threshold'],
            slow_threshold = test_case['slow_threshold'],
            siconc_var = test_case['siconc_var'],
            save_as = test_case['save_as'],
        )
        actual_sum = actual_dataset['silandfast'].sum(skipna=True).values
        assert actual_sum == test_case['expected_sum'], f"`find_landfast_ice` failed on test case: {test_case}.\nExpected: {test_case['expected_sum']}\nActual: {actual_sum}"
        if not isinstance(test_case['save_as'], type(None)):
            try:
                actual_save_as = verify_path(test_case['save_as'])
            except (FileNotFoundError) as e:
                assert True, f"`find_packed_ice` raised an exception: {e}\nExpected save file at {test_case['save_as']}"

    # Define invalid test cases
    invalid_test_cases = [
        {
            'siconc_dataset': 'invalid_var',
            'sispeed_dataset': test_file_names['sispeed'][0],
        },
        {
            'siconc_dataset': test_file_names['siconc'][0],
            'sispeed_dataset': 'invalid_var',
        },
        {
            'siconc_dataset': make_example_dataset(
                n=3, 
                test_var_name='invalid_var',
                time_axis=True,
            ),
            'sispeed_dataset': test_file_names['sispeed'][0],
        },
        {
            'siconc_dataset': test_file_names['siconc'][0],
            'sispeed_dataset': make_example_dataset(
                n=3, 
                test_var_name='invalid_var',
                time_axis=True,
            ),
        },
        {
            'siconc_dataset': make_example_dataset(
                n=4, 
                test_var_name='siconc',
            ),
            'sispeed_dataset': make_example_dataset(
                n=3, 
                test_var_name='sispeed',
            ),
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = analysis.find_landfast_ice(
                siconc_dataset = invalid_test_case['siconc_dataset'],
                sispeed_dataset = invalid_test_case['sispeed_dataset'],
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`find_landfast_ice` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`find_landfast_ice` did not raise an exception on invalid test case {invalid_test_case}"
    
    # Define a list of invalid inputs
    invalid_strings = [
        1234,
        3.14,
        None,
        [],
        {}
    ]
    for invalid_string in invalid_strings:
        # Test with `siconc_dataset`
        try:
            actual = analysis.find_landfast_ice(
                siconc_dataset = invalid_string,
                sispeed_dataset = test_file_names['sispeed'][0],
            )
        except (TypeError, ValueError) as e:
            assert True, f"`find_landfast_ice` raised an exception on invalid `siconc_dataset`: {e}"
        else:
            assert False, f"`find_landfast_ice` did not raise an exception on invalid `siconc_dataset` {invalid_string}"
        # Test with `sispeed_dataset`
        try:
            actual = analysis.find_landfast_ice(
                siconc_dataset = test_file_names['siconc'][0],
                sispeed_dataset = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`find_landfast_ice` raised an exception on invalid `sispeed_dataset`: {e}"
        else:
            assert False, f"`find_landfast_ice` did not raise an exception on invalid `sispeed_dataset` {invalid_string}"
        # Test with `siconc_var`
        try:
            actual = analysis.find_landfast_ice(
                siconc_dataset = test_file_names['siconc'][0],
                sispeed_dataset = test_file_names['sispeed'][0],
                siconc_var = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`find_landfast_ice` raised an exception on invalid `siconc_var`: {e}"
        else:
            assert False, f"`find_landfast_ice` did not raise an exception on invalid `siconc_var` {invalid_string}"
        # Test with `save_as`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.find_landfast_ice(
                    siconc_dataset = test_file_names['siconc'][0],
                    sispeed_dataset = test_file_names['sispeed'][0],
                    save_as = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`find_landfast_ice` raised an exception on invalid `save_as`: {e}"
            else:
                assert False, f"`find_landfast_ice` did not raise an exception on invalid `save_as` {invalid_string}"
    # Clean up test files that were created
    remove_non_empty_directory(test_file_dir)

def test_make_landfast_files():
    """Test the `make_landfast_files` function."""
    # Create multiple example test files
    test_file_dir = 'tests/test_analysis/example_datasets'
    version_id = 'v20260618'
    make_file_path(test_file_dir)
    test_file_names = {
        'siconc': None,
        'sispeed': None,
        'siconc2': None,
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
                time_axis=True,
                save_as=test_file,
            )
    # Define test cases
    test_cases = [
        {
            'siconc_files': test_file_names['siconc'][0],
            'sispeed_files': test_file_names['sispeed'][0],
            'packed_threshold': 4,
            'slow_threshold': 8,
            'siconc_var': 'siconc',
            'version_id': 'v20260618',
            'expected_sum': 10,
        },
        {
            'siconc_files': test_file_names['siconc2'][0],
            'sispeed_files': test_file_names['sispeed'][0],
            'packed_threshold': 4,
            'slow_threshold': 8,
            'siconc_var': 'siconc2',
            'version_id': 'v20260618',
            'expected_sum': 10,
        },
        {
            'siconc_files': test_file_names['siconc'][0],
            'sispeed_files': test_file_names['sispeed'][0],
            'packed_threshold': 8,
            'slow_threshold': 4,
            'siconc_var': 'siconc',
            'version_id': 'v20260618',
            'expected_sum': 0,
        },
        {
            'siconc_files': test_file_names['siconc'],
            'sispeed_files': test_file_names['sispeed'],
            'packed_threshold': 4,
            'slow_threshold': 8,
            'siconc_var': 'siconc',
            'version_id': 'v20260618',
            'expected_sum': 10,
        },
    ]
    for test_case in test_cases:
        analysis.make_landfast_files(
            siconc_files = test_case['siconc_files'],
            sispeed_files = test_case['sispeed_files'],
            packed_threshold = test_case['packed_threshold'],
            slow_threshold = test_case['slow_threshold'],
            siconc_var = test_case['siconc_var'],
            version_id = test_case['version_id'],
            overwrite = True,
        )
        # Assemble expected filepath
        if not isinstance(test_case['siconc_files'], type([])):
            test_case['siconc_files'] = [test_case['siconc_files']]
        if not isinstance(test_case['sispeed_files'], type([])):
            test_case['sispeed_files'] = [test_case['sispeed_files']]
        original_version_id = test_case['siconc_files'][0].split('/')[-2]
        for i in range(len(test_case['siconc_files'])):
            expected_filepath = test_case['siconc_files'][i].replace('siconc', 'silandfast').replace(original_version_id, test_case['version_id'])
            # Verify the filepath exists
            try:
                actual_filepath = verify_path(expected_filepath)
            except (FileNotFoundError) as e:
                assert True, f"`find_packed_ice` raised an exception: {e}\nExpected save file at {expected_filepath}"
            # Check that the sum of the `silandfast` variable is as expected
            actual_dataset = xr.open_dataset(actual_filepath)
            actual_sum = actual_dataset['silandfast'].sum(skipna=True).values
            assert actual_sum == test_case['expected_sum'], f"`make_landfast_files` failed on test case: {test_case}.\nExpected: {test_case['expected_sum']}\nActual: {actual_sum}"
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
            'siconc_files': test_file_names['siconc'],
            'sispeed_files': test_file_names['sispeed'][0],
        },
        {   # Passing a string that isn't a file path
            'siconc_files': 'invalid_var',
            'sispeed_files': test_file_names['sispeed'][0],
        },
        {   # Passing a file that does not exist
            'siconc_files': test_file_names['siconc'][0],
            'sispeed_files': 'invalid_var.nc',
        },
        {   # Passing a dataset with the incorrect variable
            'siconc_files': test_file_names['invalid_var'][0],
            'sispeed_files': test_file_names['sispeed'][0],
        },
        {   # Passing a dataset with the incorrect variable
            'siconc_files': test_file_names['siconc'][0],
            'sispeed_files': test_file_names['invalid_var'][0],
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = analysis.make_landfast_files(
                siconc_files = invalid_test_case['siconc_files'],
                sispeed_files = invalid_test_case['sispeed_files'],
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`make_landfast_files` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`make_landfast_files` did not raise an exception on invalid test case {invalid_test_case}"
    
    # Define a list of invalid inputs
    invalid_strings = [
        1234,
        3.14,
        None,
        [],
        {}
    ]
    for invalid_string in invalid_strings:
        # Test with `siconc_files`
        try:
            actual = analysis.make_landfast_files(
                siconc_files = invalid_string,
                sispeed_files = test_file_names['sispeed'][0],
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_landfast_files` raised an exception on invalid `siconc_files`: {e}"
        else:
            assert False, f"`make_landfast_files` did not raise an exception on invalid `siconc_files` {invalid_string}"
        # Test with `sispeed_files`
        try:
            actual = analysis.make_landfast_files(
                siconc_files = test_file_names['siconc'][0],
                sispeed_files = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_landfast_files` raised an exception on invalid `sispeed_files`: {e}"
        else:
            assert False, f"`make_landfast_files` did not raise an exception on invalid `sispeed_files` {invalid_string}"
        # Test with `siconc_var`
        try:
            actual = analysis.make_landfast_files(
                siconc_files = test_file_names['siconc'][0],
                sispeed_files = test_file_names['sispeed'][0],
                siconc_var = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_landfast_files` raised an exception on invalid `siconc_var`: {e}"
        else:
            assert False, f"`make_landfast_files` did not raise an exception on invalid `siconc_var` {invalid_string}"
        # Test with `version_id`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.make_landfast_files(
                    siconc_files = test_file_names['siconc'][0],
                    sispeed_files = test_file_names['sispeed'][0],
                    version_id = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`make_landfast_files` raised an exception on invalid `version_id`: {e}"
            else:
                assert False, f"`make_landfast_files` did not raise an exception on invalid `version_id` {invalid_string}"
        # Test with `overwrite`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.make_landfast_files(
                    siconc_files = test_file_names['siconc'][0],
                    sispeed_files = test_file_names['sispeed'][0],
                    overwrite = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`make_landfast_files` raised an exception on invalid `overwrite`: {e}"
            else:
                assert False, f"`make_landfast_files` did not raise an exception on invalid `overwrite` {invalid_string}"
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
            actual = analysis.make_landfast_files(
                siconc_files = invalid_string,
                sispeed_files = test_file_names['sispeed'][0],
                map_bbox = invalid_map_bbox,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_landfast_files` raised an exception on invalid `map_bbox`: {e}"
        else:
            assert False, f"`make_landfast_files` did not raise an exception on invalid `map_bbox` {invalid_string}"
    # Clean up test files that were created
    remove_non_empty_directory(test_file_dir)
