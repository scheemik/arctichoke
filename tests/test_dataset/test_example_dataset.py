import os

from seaicecp.dataset import example_dataset

def test_make_example_dataset():
    """Test the `make_example_dataset` function."""
    # Define test filepath
    test_filepath = 'tests/test_dataset/delete_this_dataset.nc'
    # Define test cases
    test_cases = [
        {
            'actual': example_dataset.make_example_dataset(filepath=test_filepath),
            'keys': ['test_var'],
            'coords': ['j', 'i', 'longitude', 'latitude'],
            'sizes': ['j', 'i'],
            'test_var_size': 100,
            'n_size': 10,
        },
        {
            'actual': example_dataset.make_example_dataset(filepath=test_filepath, n=5),
            'keys': ['test_var'],
            'coords': ['j', 'i', 'longitude', 'latitude'],
            'sizes': ['j', 'i'],
            'test_var_size': 25,
            'n_size': 5,
        },
    ]
    for test_case in test_cases:
        # Check the data variables
        assert list(test_case['actual'].keys()) == test_case['keys'], f"`make_example_dataset` created a dataset with the variables: {list(test_case['actual'].keys())}.\nExpected variables: {test_case['keys']}"
        # Check the coordinates
        assert list(test_case['actual'].coords) == test_case['coords'], f"`make_example_dataset` created a dataset with the coordinates: {list(test_case['actual'].coords)}.\nExpected coordinates: {test_case['coords']}"
        # Check the sizes
        assert list(test_case['actual'].sizes) == test_case['sizes'], f"`make_example_dataset` created a dataset with the sizes: {list(test_case['actual'].sizes)}.\nExpected sizes: {test_case['sizes']}"
        assert test_case['actual']['test_var'].size == test_case['test_var_size'], f"`make_example_dataset` created a dataset with a variable size: {test_case['actual']['test_var'].size}.\nExpected variable size: {test_case['test_var_size']}"
        assert test_case['actual']['longitude'].size == test_case['test_var_size'], f"`make_example_dataset` created a dataset with a longitude size: {test_case['actual']['longitude'].size}.\nExpected variable size: {test_case['test_var_size']}"
        assert test_case['actual']['latitude'].size == test_case['test_var_size'], f"`make_example_dataset` created a dataset with a latitude size: {test_case['actual']['latitude'].size}.\nExpected variable size: {test_case['test_var_size']}"
        assert test_case['actual']['i'].size == test_case['n_size'], f"`make_example_dataset` created a dataset with a variable size: {test_case['actual']['i'].size}.\nExpected variable size: {test_case['n_size']}"
        assert test_case['actual']['j'].size == test_case['n_size'], f"`make_example_dataset` created a dataset with a variable size: {test_case['actual']['j'].size}.\nExpected variable size: {test_case['n_size']}"
    
    # Test setting overwrite to `False`
    try:
        actual = example_dataset.make_example_dataset(
            filepath=test_filepath,
            overwrite = False,
        )
    except (FileExistsError) as e:
        assert True, f"`make_example_dataset` raised an exception when specifying overwrite=`False`: {e}"
    else:
        assert False, f"`make_example_dataset` did not raise an exception when specifying overwrite=`False`"

    # Define invalid test cases
    # Test for `filepath`
    invalid_values = [
        'not_a_dataset.txt',
        1234,
        3.14,
        None,
        [],
        {},
    ]
    for invalid_value in invalid_values:
        try:
            actual = example_dataset.make_example_dataset(
                filepath = invalid_value,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_example_dataset` raised an exception on invalid filepath: {e}"
        else:
            assert False, f"`make_example_dataset` did not raise an exception on invalid filepath {invalid_value}"
    # Test for `n`
    invalid_values = [
        'not_a_value',
        3.14,
        None,
        [],
        {},
    ]
    for invalid_value in invalid_values:
        try:
            actual = example_dataset.make_example_dataset(
                filepath=test_filepath,
                n = invalid_value,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_example_dataset` raised an exception on invalid n: {e}"
        else:
            assert False, f"`make_example_dataset` did not raise an exception on invalid n {invalid_value}"
    # Test for `overwrite`
    invalid_values = [
        'not_a_value',
        1234,
        3.14,
        None,
        [],
        {},
    ]
    for invalid_value in invalid_values:
        try:
            actual = example_dataset.make_example_dataset(
                filepath=test_filepath,
                overwrite = invalid_value,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_example_dataset` raised an exception on invalid overwrite: {e}"
        else:
            assert False, f"`make_example_dataset` did not raise an exception on invalid overwrite {invalid_value}"
    
    # Clean up the example dataset
    os.remove(test_filepath)