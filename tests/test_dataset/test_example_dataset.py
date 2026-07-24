import numpy as np
import os

from arctichoke import dataset

def test_make_example_dataset():
    """Test the `make_example_dataset` function."""
    # Define test filepath
    test_filepath = 'tests/test_dataset/delete_this_dataset.nc'
    # Define test cases
    test_cases = [
        {
            'actual': dataset.make_example_dataset(),
            'keys': ['test_var'],
            'coords': ['j', 'i', 'longitude', 'latitude'],
            'sizes': ['j', 'i'],
            'test_var_size': 100,
            'test_latlon_size': 100,
            'n_size': 10,
        },
        {
            'actual': dataset.make_example_dataset(
                test_var_name='new_test_var'
            ),
            'keys': ['new_test_var'],
            'coords': ['j', 'i', 'longitude', 'latitude'],
            'sizes': ['j', 'i'],
            'test_var_size': 100,
            'test_latlon_size': 100,
            'n_size': 10,
        },
        {
            'actual': dataset.make_example_dataset(
                save_as=test_filepath
            ),
            'keys': ['test_var'],
            'coords': ['j', 'i', 'longitude', 'latitude'],
            'sizes': ['j', 'i'],
            'test_var_size': 100,
            'test_latlon_size': 100,
            'n_size': 10,
        },
        {
            'actual': dataset.make_example_dataset(
                save_as=test_filepath, 
                n=5,
            ),
            'keys': ['test_var'],
            'coords': ['j', 'i', 'longitude', 'latitude'],
            'sizes': ['j', 'i'],
            'test_var_size': 25,
            'test_latlon_size': 25,
            'n_size': 5,
        },
        {
            'actual': dataset.make_example_dataset(
                time_dim='year',
            ),
            'keys': ['test_var'],
            'coords': ['year', 'j', 'i', 'longitude', 'latitude'],
            'sizes': ['year', 'j', 'i'],
            'test_var_size': 100,
            'test_latlon_size': 100,
            'n_size': 10,
            'unique_years': [2000],
            'expected_sums': [4950, 4950],
        },
        {
            'actual': dataset.make_example_dataset(
                time_dim='year',
                time_len=2,
                start_year=2025,
            ),
            'keys': ['test_var'],
            'coords': ['year', 'j', 'i', 'longitude', 'latitude'],
            'sizes': ['year', 'j', 'i'],
            'test_var_size': 200,
            'test_latlon_size': 100,
            'n_size': 10,
            'unique_years': [2025],
            'expected_sums': [4950, 4950],
        },
        {
            'actual': dataset.make_example_dataset(
                n=3, 
                offset=2, 
                time_dim='time',
                time_len=2,
            ),
            'keys': ['test_var'],
            'coords': ['time', 'j', 'i', 'longitude', 'latitude'],
            'sizes': ['time', 'j', 'i'],
            'test_var_size': 18,
            'test_latlon_size': 9,
            'n_size': 3,
            'unique_years': [2026],
            'expected_sums': [36+2*9, 54],
        },
    ]
    for test_case in test_cases:
        # Check the data variables
        assert list(test_case['actual'].keys()) == test_case['keys'], f"`make_example_dataset` created a dataset with the variables: {list(test_case['actual'].keys())}.\nExpected variables: {test_case['keys']}"
        # Check the coordinates
        assert list(test_case['actual'].coords) == test_case['coords'], f"`make_example_dataset` created a dataset with the coordinates: {list(test_case['actual'].coords)}.\nExpected coordinates: {test_case['coords']}"
        # Check the sizes
        assert list(test_case['actual'].sizes) == test_case['sizes'], f"`make_example_dataset` created a dataset with the sizes: {list(test_case['actual'].sizes)}.\nExpected sizes: {test_case['sizes']}"
        for this_var in test_case['keys']:
            assert test_case['actual'][this_var].size == test_case['test_var_size'], f"`make_example_dataset` created a dataset with a variable size: {test_case['actual'][this_var].size}.\nExpected variable size: {test_case['test_var_size']}"
        assert test_case['actual']['longitude'].size == test_case['test_latlon_size'], f"`make_example_dataset` created a dataset with a longitude size: {test_case['actual']['longitude'].size}.\nExpected variable size: {test_case['test_latlon_size']}"
        assert test_case['actual']['latitude'].size == test_case['test_latlon_size'], f"`make_example_dataset` created a dataset with a latitude size: {test_case['actual']['latitude'].size}.\nExpected variable size: {test_case['test_latlon_size']}"
        assert test_case['actual']['i'].size == test_case['n_size'], f"`make_example_dataset` created a dataset with a variable size: {test_case['actual']['i'].size}.\nExpected variable size: {test_case['n_size']}"
        assert test_case['actual']['j'].size == test_case['n_size'], f"`make_example_dataset` created a dataset with a variable size: {test_case['actual']['j'].size}.\nExpected variable size: {test_case['n_size']}"
        if 'time' in test_case['coords']:
            # Check the years present on the time axis
            actual_years = np.unique(test_case['actual']['time'].dt.year.values)
            assert actual_years == test_case['unique_years'], f"`make_example_dataset` created a dataset with the unique years: {actual_years}.\nExpected unique years: {test_case['unique_years']}"
            # Check each year
            for datetime in test_case['actual']['time'].values:
                for i in range(len(test_case['keys'])):
                    this_var = test_case['keys'][i]
                    actual_sum = test_case['actual'][this_var].sel(time=datetime).sum(skipna=True).values
                    assert actual_sum == test_case['expected_sums'][i], f"`make_example_dataset` failed on test case: {test_case}.\nExpected: {test_case['expected_sums'][i]}\nActual: {actual_sum}"
    
    # Test setting overwrite to `False`
    try:
        actual = dataset.make_example_dataset(
            save_as=test_filepath,
            overwrite = False,
        )
    except (FileExistsError) as e:
        assert True, f"`make_example_dataset` raised an exception when specifying overwrite=`False`: {e}"
    else:
        assert False, f"`make_example_dataset` did not raise an exception when specifying overwrite=`False`"

    # Define invalid test cases
    # Test for `save_as`
    invalid_values = [
        'not_a_dataset.txt',
        1234,
        3.14,
        [],
        {},
    ]
    for invalid_value in invalid_values:
        try:
            actual = dataset.make_example_dataset(
                save_as = invalid_value,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_example_dataset` raised an exception on invalid `save_as`: {e}"
        else:
            assert False, f"`make_example_dataset` did not raise an exception on invalid `save_as` {invalid_value}"
    # Test for `test_var_name`
    invalid_values = [
        False,
        3.14,
        None,
        [],
        {},
    ]
    for invalid_value in invalid_values:
        for invalid_value in invalid_values:
            try:
                actual = dataset.make_example_dataset(
                    save_as=test_filepath,
                    test_var_name=invalid_value,
                )
            except (TypeError, ValueError) as e:
                assert True, f"`make_example_dataset` raised an exception on invalid `test_var_name`: {e}"
            else:
                assert False, f"`make_example_dataset` did not raise an exception on invalid `test_var_name` {invalid_value}"
    invalid_values = [
        'not_a_value',
        3.14,
        None,
        [],
        {},
    ]
    for invalid_value in invalid_values:
        # Test for `save_as`
        if not isinstance(invalid_value, type(None)):
            try:
                actual = dataset.make_example_dataset(
                    save_as=invalid_value,
                )
            except (TypeError, ValueError) as e:
                assert True, f"`make_example_dataset` raised an exception on invalid `save_as`: {e}"
            else:
                assert False, f"`make_example_dataset` did not raise an exception on invalid `save_as` {invalid_value}"
        # Test for `n`
        try:
            actual = dataset.make_example_dataset(
                save_as=test_filepath,
                n = invalid_value,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_example_dataset` raised an exception on invalid `n`: {e}"
        else:
            assert False, f"`make_example_dataset` did not raise an exception on invalid `n` {invalid_value}"
        # Test for `offset`
        if not isinstance(invalid_value, (int, float)):
            try:
                actual = dataset.make_example_dataset(
                    offset=invalid_value,
                )
            except (TypeError, ValueError) as e:
                assert True, f"`make_example_dataset` raised an exception on invalid `offset`: {e}"
            else:
                assert False, f"`make_example_dataset` did not raise an exception on invalid `offset` {invalid_value}"
        # Test for `test_var_name`
        if not isinstance(invalid_value, str):
            try:
                actual = dataset.make_example_dataset(
                    test_var_name=invalid_value,
                )
            except (TypeError, ValueError) as e:
                assert True, f"`make_example_dataset` raised an exception on invalid `test_var_name`: {e}"
            else:
                assert False, f"`make_example_dataset` did not raise an exception on invalid `test_var_name` {invalid_value}"
        # Test for `time_dim`
        if not isinstance(invalid_value, type(None)):
            try:
                actual = dataset.make_example_dataset(
                    save_as=test_filepath,
                    time_dim = invalid_value,
                )
            except (TypeError, ValueError, NotImplementedError) as e:
                assert True, f"`make_example_dataset` raised an exception on invalid `time_dim`: {e}"
            else:
                assert False, f"`make_example_dataset` did not raise an exception on invalid `time_dim` {invalid_value}"
        # Test for `time_len`
        try:
            actual = dataset.make_example_dataset(
                save_as=test_filepath,
                time_len = invalid_value,
            )
        except (TypeError, ValueError, NotImplementedError) as e:
            assert True, f"`make_example_dataset` raised an exception on invalid `time_len`: {e}"
        else:
            assert False, f"`make_example_dataset` did not raise an exception on invalid `time_len` {invalid_value}"
        # Test for `start_year`
        try:
            actual = dataset.make_example_dataset(
                save_as=test_filepath,
                start_year = invalid_value,
            )
        except (TypeError, ValueError, NotImplementedError) as e:
            assert True, f"`make_example_dataset` raised an exception on invalid `start_year`: {e}"
        else:
            assert False, f"`make_example_dataset` did not raise an exception on invalid `start_year` {invalid_value}"
        # Test for `overwrite`
        try:
            actual = dataset.make_example_dataset(
                save_as=test_filepath,
                overwrite = invalid_value,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_example_dataset` raised an exception on invalid `overwrite`: {e}"
        else:
            assert False, f"`make_example_dataset` did not raise an exception on invalid `overwrite` {invalid_value}"
    
    # Clean up the example dataset
    os.remove(test_filepath)