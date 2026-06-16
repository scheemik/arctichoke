import numpy as np 

from seaicecp import analysis
from seaicecp.path.manipulate_paths import remove_non_empty_directory, make_file_path
from seaicecp.dataset.example_dataset import make_example_dataset

def test_find_packed_ice():
    """Test the `find_packed_ice` function."""
    # Create multiple example test files
    # test_file_dir = 'tests/test_dataset/example_datasets'
    # make_file_path(test_file_dir)
    # test_file_names = [
    #     f"{test_file_dir}/example_dataset_0.nc",
    #     f"{test_file_dir}/example_dataset_1.nc",
    #     f"{test_file_dir}/example_dataset_2.nc",
    # ]
    # for test_file in test_file_names:
    #     make_example_dataset(save_as=test_file, n=10)
    # Define test cases
    ## Note: The expected output of some of these test cases must be manually kept up to date
    test_cases = [
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='siconc',
            ),
            'packed_threshold': 3,
            'expected_sums': [
                5,
                ],
        },
        # {
        #     'dataset': test_file_names,
        #     'variable_id': 'test_var',
        #     'expected_means': [
        #         49.49999999999998,
        #         ],
        # },
        # {
        #     'dataset': 'data/NWP_cdo_CLI_areacello_Ofx_EC-Earth3P-HR_highres-future_r2i1p2f1_gn.nc',
        #     'variable_id': 'areacello',
        #     'expected_means': [
        #         1.3731426e+08,
        #         ],
        # },
    ]
    for test_case in test_cases:
        actual_datasets = analysis.find_packed_ice(
            dataset = test_case['dataset'],
            packed_threshold = test_case['packed_threshold'],
        )
        for i in range(len(actual_datasets)):
            actual_dataset = actual_datasets#[i]
            actual_sum = actual_dataset['sipacked'].sum(skipna=True).values
            assert actual_sum == test_case['expected_sums'][i], f"`find_packed_ice` failed on test case: {test_case} for index i={i}.\nExpected: {test_case['expected_sums']}\nActual: {actual_sum}"
    # Clean up test files that were created
    # remove_non_empty_directory(test_file_dir)

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