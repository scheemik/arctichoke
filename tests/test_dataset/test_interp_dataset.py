import numpy as np
import os

from arctichoke import dataset

def test_interp_to_reg_grid():
    """Test the `interp_to_reg_grid` function."""
    # Define test filepaths
    test_dataset_filepath = 'tests/test_dataset/delete_this_dataset.nc'
    test_targetgrid_filepath = 'tests/test_dataset/delete_this_targetgrid.nc'
    # Create a test targetgrid file
    dataset.make_example_latlon_grid(
        lat_range = [7, 9],
        lon_range = [10, 12],
        lat_step = 1,
        lon_step = 1,
        save_as = test_targetgrid_filepath,
    )
    # Define test cases
    test_cases = [
        {
            'dataset': dataset.make_example_dataset(
                n = 3,
                test_var_name = 'to_interp',
                save_as = test_dataset_filepath,
            ),
            'target_grid': test_targetgrid_filepath,
            'keys': ['to_interp'],
            'coords': ['lon','lat'],
            'sizes': {
                'lat': 3,
                'lon': 3,
            },
            'test_var_size': 9,
            'expected_data': np.array(
                [[0., 1., 2.],
                 [3., 4., 5.],
                 [6., 7., 8.]],
            ),
        },
    ]
    for test_case in test_cases:
        # Interpolate the dataset
        actual = dataset.interp_to_reg_grid(
            dataset = test_case['dataset'],
            targetgrid = test_case['target_grid'],
        )
        # Check the data variables
        assert list(actual.keys()) == test_case['keys'], f"`interp_to_reg_grid` created a dataset with the variables: {list(actual.keys())}.\nExpected variables: {test_case['keys']}"
        # Check the coordinates
        assert list(actual.coords) == test_case['coords'], f"`interp_to_reg_grid` created a dataset with the coordinates: {list(actual.coords)}.\nExpected coordinates: {test_case['coords']}"
        # Check the sizes
        assert actual.sizes == test_case['sizes'], f"`interp_to_reg_grid` created a dataset with the sizes: {actual.sizes}.\nExpected sizes: {test_case['sizes']}"
        for this_var in test_case['keys']:
            assert actual[this_var].size == test_case['test_var_size'], f"`interp_to_reg_grid` created a dataset with a variable size: {actual[this_var].size}.\nExpected variable size: {test_case['test_var_size']}"
        # Check the interpolated data
        actual_data = np.array(actual[test_case['keys'][0]].values)
        assert np.array_equal(actual_data, test_case['expected_data']), f"`interp_to_reg_grid` created a dataset with the data: \n{actual_data}.\nExpected data: {test_case['expected_data']}"
    
#     # Test setting overwrite to `False`
#     try:
#         actual = dataset.interp_to_reg_grid(
#             save_as=test_filepath,
#             overwrite = False,
#         )
#     except (FileExistsError) as e:
#         assert True, f"`interp_to_reg_grid` raised an exception when specifying overwrite=`False`: {e}"
#     else:
#         assert False, f"`interp_to_reg_grid` did not raise an exception when specifying overwrite=`False`"
# 
#     # Define invalid test cases
#     # Test for `save_as`
#     invalid_values = [
#         'not_a_dataset.txt',
#         1234,
#         3.14,
#         [],
#         {},
#     ]
#     for invalid_value in invalid_values:
#         try:
#             actual = dataset.interp_to_reg_grid(
#                 save_as = invalid_value,
#             )
#         except (TypeError, ValueError) as e:
#             assert True, f"`interp_to_reg_grid` raised an exception on invalid `save_as`: {e}"
#         else:
#             assert False, f"`interp_to_reg_grid` did not raise an exception on invalid `save_as` {invalid_value}"
#     # Test for `test_var_name`
#     invalid_values = [
#         False,
#         3.14,
#         None,
#         [],
#         {},
#     ]
#     for invalid_value in invalid_values:
#         for invalid_value in invalid_values:
#             try:
#                 actual = dataset.interp_to_reg_grid(
#                     save_as=test_filepath,
#                     test_var_name=invalid_value,
#                 )
#             except (TypeError, ValueError) as e:
#                 assert True, f"`interp_to_reg_grid` raised an exception on invalid `test_var_name`: {e}"
#             else:
#                 assert False, f"`interp_to_reg_grid` did not raise an exception on invalid `test_var_name` {invalid_value}"
#     invalid_values = [
#         'not_a_value',
#         3.14,
#         None,
#         [],
#         {},
#     ]
#     for invalid_value in invalid_values:
#         # Test for `save_as`
#         if not isinstance(invalid_value, type(None)):
#             try:
#                 actual = dataset.interp_to_reg_grid(
#                     save_as=invalid_value,
#                 )
#             except (TypeError, ValueError) as e:
#                 assert True, f"`interp_to_reg_grid` raised an exception on invalid `save_as`: {e}"
#             else:
#                 assert False, f"`interp_to_reg_grid` did not raise an exception on invalid `save_as` {invalid_value}"
#         # Test for `n`
#         try:
#             actual = dataset.interp_to_reg_grid(
#                 save_as=test_filepath,
#                 n = invalid_value,
#             )
#         except (TypeError, ValueError) as e:
#             assert True, f"`interp_to_reg_grid` raised an exception on invalid `n`: {e}"
#         else:
#             assert False, f"`interp_to_reg_grid` did not raise an exception on invalid `n` {invalid_value}"
#         # Test for `offset`
#         if not isinstance(invalid_value, (int, float)):
#             try:
#                 actual = dataset.interp_to_reg_grid(
#                     offset=invalid_value,
#                 )
#             except (TypeError, ValueError) as e:
#                 assert True, f"`interp_to_reg_grid` raised an exception on invalid `offset`: {e}"
#             else:
#                 assert False, f"`interp_to_reg_grid` did not raise an exception on invalid `offset` {invalid_value}"
#         # Test for `multiplier`
#         if not isinstance(invalid_value, (int, float)):
#             try:
#                 actual = dataset.interp_to_reg_grid(
#                     multiplier=invalid_value,
#                 )
#             except (TypeError, ValueError) as e:
#                 assert True, f"`interp_to_reg_grid` raised an exception on invalid `multiplier`: {e}"
#             else:
#                 assert False, f"`interp_to_reg_grid` did not raise an exception on invalid `multiplier` {invalid_value}"
#         # Test for `test_var_name`
#         if not isinstance(invalid_value, str):
#             try:
#                 actual = dataset.interp_to_reg_grid(
#                     test_var_name=invalid_value,
#                 )
#             except (TypeError, ValueError) as e:
#                 assert True, f"`interp_to_reg_grid` raised an exception on invalid `test_var_name`: {e}"
#             else:
#                 assert False, f"`interp_to_reg_grid` did not raise an exception on invalid `test_var_name` {invalid_value}"
#         # Test for `time_dim`
#         if not isinstance(invalid_value, type(None)):
#             try:
#                 actual = dataset.interp_to_reg_grid(
#                     save_as=test_filepath,
#                     time_dim = invalid_value,
#                 )
#             except (TypeError, ValueError, NotImplementedError) as e:
#                 assert True, f"`interp_to_reg_grid` raised an exception on invalid `time_dim`: {e}"
#             else:
#                 assert False, f"`interp_to_reg_grid` did not raise an exception on invalid `time_dim` {invalid_value}"
#         # Test for `time_len`
#         try:
#             actual = dataset.interp_to_reg_grid(
#                 save_as=test_filepath,
#                 time_len = invalid_value,
#             )
#         except (TypeError, ValueError, NotImplementedError) as e:
#             assert True, f"`interp_to_reg_grid` raised an exception on invalid `time_len`: {e}"
#         else:
#             assert False, f"`interp_to_reg_grid` did not raise an exception on invalid `time_len` {invalid_value}"
#         # Test for `start_year`
#         try:
#             actual = dataset.interp_to_reg_grid(
#                 save_as=test_filepath,
#                 start_year = invalid_value,
#             )
#         except (TypeError, ValueError, NotImplementedError) as e:
#             assert True, f"`interp_to_reg_grid` raised an exception on invalid `start_year`: {e}"
#         else:
#             assert False, f"`interp_to_reg_grid` did not raise an exception on invalid `start_year` {invalid_value}"
#         # Test for `overwrite`
#         try:
#             actual = dataset.interp_to_reg_grid(
#                 save_as=test_filepath,
#                 overwrite = invalid_value,
#             )
#         except (TypeError, ValueError) as e:
#             assert True, f"`interp_to_reg_grid` raised an exception on invalid `overwrite`: {e}"
#         else:
#             assert False, f"`interp_to_reg_grid` did not raise an exception on invalid `overwrite` {invalid_value}"
    
    # Clean up the example datasets
    os.remove(test_dataset_filepath)
    os.remove(test_targetgrid_filepath)
