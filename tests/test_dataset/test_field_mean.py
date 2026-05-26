from cdo import CDOException

from seaicecp import dataset
from seaicecp.path.manipulate_paths import remove_non_empty_directory, make_file_path
from seaicecp.dataset.example_dataset import make_example_dataset

def test_get_field_mean():
    """Test the `get_field_mean` function."""
    # Create multiple example test files
    test_file_dir = 'tests/test_dataset/example_datasets'
    make_file_path(test_file_dir)
    test_file_names = [
        f"{test_file_dir}/example_dataset_0.nc",
        f"{test_file_dir}/example_dataset_1.nc",
        f"{test_file_dir}/example_dataset_2.nc",
    ]
    for test_file in test_file_names:
        make_example_dataset(save_as=test_file, n=10)
    # Define test cases
    ## Note: The expected output of some of these test cases must be manually kept up to date
    test_cases = [
        {
            'dataset': make_example_dataset(n=5),
            'variable_id': 'test_var',
            'expected_means': [
                12.000000000000004,
                ],
        },
        {
            'dataset': test_file_names,
            'variable_id': 'test_var',
            'expected_means': [
                49.49999999999998,
                ],
        },
        {
            'dataset': 'data/NWP_cdo_CLI_areacello_Ofx_EC-Earth3P-HR_highres-future_r2i1p2f1_gn.nc',
            'variable_id': 'areacello',
            'expected_means': [
                1.3731426e+08,
                ],
        },
    ]
    for test_case in test_cases:
        actual = list(dataset.get_field_mean(test_case['dataset'])[test_case['variable_id']].values.flatten())
        assert actual == test_case['expected_means'], f"`get_field_mean` failed on test case: {test_case}.\nExpected: {test_case['expected_means']}\nActual: {actual}"
    # Clean up test files that were created
    remove_non_empty_directory(test_file_dir)

    # Define invalid test cases
    invalid_test_cases = [
        {
            'dataset': 'invalid_dataset',
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = dataset.get_field_mean(
                dataset = invalid_test_case['dataset'],
            )
        except (FileNotFoundError) as e:
            assert True, f"`get_field_mean` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`get_field_mean` did not raise an exception on invalid test case {invalid_test_case}"
    
    # Define a list of invalid datasets
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
            actual = dataset.get_field_mean(
                dataset = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`get_field_mean` raised an exception on invalid `dataset`: {e}"
        else:
            assert False, f"`get_field_mean` did not raise an exception on invalid `dataset` {invalid_string}"
        # Test with `save_as`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = dataset.get_field_mean(
                    dataset = test_cases[0]['dataset'],
                    save_as = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`get_field_mean` raised an exception on invalid `save_as`: {e}"
            else:
                assert False, f"`get_field_mean` did not raise an exception on invalid `save_as` {invalid_string}"