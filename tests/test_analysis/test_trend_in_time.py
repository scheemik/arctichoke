import numpy as np 
import xarray as xr

from arctichoke import analysis
from arctichoke.dataset.example_dataset import make_example_dataset
from arctichoke.path.manipulate_paths import remove_non_empty_directory, make_file_path
from arctichoke.verify import verify_path

def test_trend_in_time():
    """Test the `trend_in_time` function."""
    # Create multiple example test files
    test_file_dir = 'tests/test_analysis/example_datasets'
    make_file_path(test_file_dir)
    test_file_names = [
        f"{test_file_dir}/example_dataset_0.nc",
        f"{test_file_dir}/example_dataset_1.nc",
        f"{test_file_dir}/example_dataset_2.nc",
    ]
    offsets = [0, 1, 3]
    for i in range(len(test_file_names)):
        make_example_dataset(
            n=3,
            offset=offsets[i],
            test_var_name='test_var',
            time_axis=(2000+i),
            save_as=test_file_names[i],
        )
    # Create test case with many different trends
    if True:
        n = 3
        offset = 0
        test_var_name = 'test_var'
        # Initialize the dataset
        test_many_trends = xr.Dataset()
        # Add dimensions
        j_arr = np.arange(n, dtype=np.float64)
        test_many_trends['j'] = ('j',j_arr)
        i_arr = np.arange(n+1,2*n+1, dtype=np.float64)
        test_many_trends['i'] = ('i',i_arr)
        this_year = 2026
        time_arr = np.arange(f'{this_year}-01', f'{this_year+3}-01', dtype='datetime64[Y]')
        time_arr = [2026, 2027, 2028]
        test_many_trends['year'] = ('year',time_arr)
        len_t = len(time_arr)

        # Assign longitude and latitude coordinates
        lon_arr = np.reshape([np.arange(2*n+1,3*n+1, dtype=np.float64)]*n, (n,n))
        lat_arr = np.reshape([np.arange(3*n+1,4*n+1, dtype=np.float64)]*n, (n,n)).T
        test_many_trends = test_many_trends.assign_coords(
            {
                'longitude': (['j','i'], lon_arr),
                'latitude': (['j','i'], lat_arr),
            }
        )

        # Add a test variable
        test_var = np.reshape(np.arange(offset, n*n+offset, dtype=np.float64), (n,n))
        test_var
        test_var = np.array([
            [[0., 1., 2.],
            [0., 1., 2.],
            [0., 1., 2.]],
            [[0., 1., 2.],
            [1., 2., 0.],
            [2., 1., 1.]],
            [[0., 1., 2.],
            [0., 1., 1.],
            [1., 2., 2.]],
        ])
        test_many_trends[test_var_name] = (['year','j','i'],test_var)
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
            'var': 'test_var',
            'time_dim': 'time',
            'mask_where_zero_across_time': True,
            'use_xarray_polyfit': True,
            'save_as': None,
            'atol': 1e-12,
            'expected_trends': [0, np.nan],
            'expected_residuals': [np.nan],
        },
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='test_var',
                time_axis=True,
            ),
            'var': 'test_var',
            'time_dim': 'time',
            'mask_where_zero_across_time': False,
            'use_xarray_polyfit': True,
            'save_as': f"{test_file_dir}/example_new_0.nc",
            'atol': 1e-12,
            'expected_trends': [0],
            'expected_residuals': [np.nan],
        },
        {
            'dataset': test_file_names,
            'var': 'test_var',
            'time_dim': 'time',
            'mask_where_zero_across_time': True,
            'use_xarray_polyfit': True,
            'save_as': None,
            'atol': 1e-4,
            'expected_trends': [1.49368],
            'expected_residuals': [1.13618e+16],
        },
        {
            'dataset': test_file_names,
            'var': 'test_var',
            'time_dim': 'time',
            'mask_where_zero_across_time': True,
            'use_xarray_polyfit': True,
            'atol': 1e-4,
            'save_as': f"{test_file_dir}/example_new_1.nc",
            'expected_trends': [1.49368],
            'expected_residuals': [1.13618e+16],
        },
        {
            'dataset': test_many_trends,
            'var': 'test_var',
            'time_dim': 'year',
            'mask_where_zero_across_time': True,
            'use_xarray_polyfit': True,
            'atol': 1e-4,
            'save_as': None,
            'expected_trends': [
                 0.00000000e+00, -6.74152213e-17, -1.34830443e-16,
                -1.00804977e-13, -1.00898639e-13, -0.499999999999,
                 0.499999999999,  0.500000000000,  1.00617838e-13, np.nan,
            ],
            'expected_residuals': [
                0.00000000e+00, 3.04386613e-33, 1.21754645e-32,
                6.66666667e-01, 6.66666667e-01, 1.50000000e+00,
                1.50000000e+00, 1.66666667e-01, 6.66666667e-01, np.nan
            ],
        },
        {
            'dataset': test_nan_dataset,
            'var': 'test_var',
            'time_dim': 'time',
            'mask_where_zero_across_time': True,
            'use_xarray_polyfit': True,
            'atol': 1e-4,
            'save_as': None,
            'expected_trends': [1.49368, 0.990164, 0, np.nan],
            'expected_residuals': [2.24627e+14, 1.13618e+16, np.nan],
        },
        {
            'dataset': test_nan_dataset,
            'var': 'test_var',
            'time_dim': 'time',
            'mask_where_zero_across_time': True,
            'use_xarray_polyfit': False,
            'atol': 1e-4,
            'save_as': None,
            'expected_trends': [1.49368, np.nan],
            'expected_residuals': [0.36028, np.nan],
        },
    ]
    for test_case in test_cases:
        actual_dataset = analysis.trend_in_time(
            dataset = test_case['dataset'],
            var = test_case['var'],
            time_dim = test_case['time_dim'],
            mask_where_zero_across_time = test_case['mask_where_zero_across_time'],
            use_xarray_polyfit = test_case['use_xarray_polyfit'],
            save_as = test_case['save_as'],
        )
        # Check the trends present on the time axis
        actual_trends = list(np.unique(actual_dataset[f'{test_case['var']}_trends'].values))
        for actual_trend in actual_trends:
            isclose = False
            for expected_trend in test_case['expected_trends']:
                if np.isclose(actual_trend, expected_trend, atol=test_case['atol'], equal_nan=True):
                    isclose = True
            if isclose == False:
                assert False, f"`trend_in_time` created a dataset with the unique trends: {actual_trends}.\nExpected unique trends: {test_case['expected_trends']}\nFailed on trend: {actual_trend}"
        # Check the residuals present on the time axis
        actual_residuals = list(np.unique(actual_dataset[f'{test_case['var']}_residuals'].values))
        for actual_residual in actual_residuals:
            isclose = False
            for expected_residual in test_case['expected_residuals']:
                if np.isclose(actual_residual, expected_residual, atol=test_case['atol'], equal_nan=True):
                    isclose = True
            if isclose == False:
                assert False, f"`trend_in_time` created a dataset with the unique residuals: {actual_residuals}.\nExpected unique residuals: {test_case['expected_residuals']}\nFailed on residual: {actual_residual}"
        # Check whether a file was saved
        if not isinstance(test_case['save_as'], type(None)):
            try:
                actual_save_as = verify_path(test_case['save_as'])
            except (FileNotFoundError) as e:
                assert True, f"`trend_in_time` raised an exception: {e}\nExpected save file at {test_case['save_as']}"

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
            actual = analysis.trend_in_time(
                dataset = invalid_test_case['dataset'],
                var = 'test_var',
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`trend_in_time` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`trend_in_time` did not raise an exception on invalid test case {invalid_test_case}"
    
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
            actual = analysis.trend_in_time(
                dataset = invalid_string,
                var = 'test_var',
                time_dim = 'time',
            )
        except (TypeError, ValueError) as e:
            assert True, f"`trend_in_time` raised an exception on invalid `dataset`: {e}"
        else:
            assert False, f"`trend_in_time` did not raise an exception on invalid `dataset` {invalid_string}"
        # Test with `var`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.trend_in_time(
                    dataset = test_file_names,
                    var = invalid_string,
                    time_dim = 'time',
                )
            except (TypeError) as e:
                assert True, f"`trend_in_time` raised an exception on invalid `var`: {e}"
            else:
                assert False, f"`trend_in_time` did not raise an exception on invalid `var` {invalid_string}"
        # Test with `time_dim`
        try:
            actual = analysis.trend_in_time(
                dataset = test_file_names,
                var = 'test_var',
                time_dim = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`trend_in_time` raised an exception on invalid `time_dim`: {e}"
        else:
            assert False, f"`trend_in_time` did not raise an exception on invalid `time_dim` {invalid_string}"
        # Test with `mask_where_zero_across_time`
        try:
            actual = analysis.trend_in_time(
                dataset = test_file_names,
                var = 'test_var',
                time_dim = 'time',
                mask_where_zero_across_time = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`trend_in_time` raised an exception on invalid `mask_where_zero_across_time`: {e}"
        else:
            assert False, f"`trend_in_time` did not raise an exception on invalid `mask_where_zero_across_time` {invalid_string}"
        # Test with `use_xarray_polyfit`
        try:
            actual = analysis.trend_in_time(
                dataset = test_file_names,
                var = 'test_var',
                time_dim = 'time',
                use_xarray_polyfit = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`trend_in_time` raised an exception on invalid `use_xarray_polyfit`: {e}"
        else:
            assert False, f"`trend_in_time` did not raise an exception on invalid `use_xarray_polyfit` {invalid_string}"
        # Test with `save_as`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.trend_in_time(
                    dataset = test_file_names,
                    var = 'test_var',
                    time_dim = 'time',
                    save_as = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`trend_in_time` raised an exception on invalid `save_as`: {e}"
            else:
                assert False, f"`trend_in_time` did not raise an exception on invalid `save_as` {invalid_string}"
        # Test with `verbose`
        try:
            actual = analysis.trend_in_time(
                dataset = test_file_names,
                var = 'test_var',
                time_dim = 'time',
                verbose = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`trend_in_time` raised an exception on invalid `verbose`: {e}"
        else:
            assert False, f"`trend_in_time` did not raise an exception on invalid `verbose` {invalid_string}"
    # Clean up test files that were created
    remove_non_empty_directory(test_file_dir)

def test_mask_where_all_zero():
    """Test the `mask_where_all_zero` function."""
    # Create an example dataset
    ex_xr = xr.Dataset({
        'test_var': (
            ['t', 'i', 'j'], 
          [[[ 0,  0,  0],
            [ 1,  1,  1],
            [ 0,  0,  0]],
           [[ 0,  1,  1],
            [ 1,  0,  0],
            [ 0,  0,  0]]]
        )
    })
    # Create the expected array
    ex_arr = np.array(
      [[[np.nan,  0.,  0.],
        [ 1.,  1.,  1.],
        [np.nan, np.nan, np.nan]],

       [[np.nan,  1.,  1.],
        [ 1.,  0.,  0.],
        [np.nan, np.nan, np.nan]]],
    )
    # Define test cases
    test_cases = [
        {
            'dataset': ex_xr,
            'var': 'test_var',
            'time_dim': 't',
            'expected_array': ex_arr,
        },
        {
            'dataset': ex_xr['test_var'],
            'var': None,
            'time_dim': 't',
            'expected_array': ex_arr,
        },
    ]
    for test_case in test_cases:
        actual_dataset = analysis.mask_where_all_zero(
            dataset = test_case['dataset'],
            var = test_case['var'],
            time_dim = test_case['time_dim'],
        )
        # Check the result versus the expectation
        if isinstance(test_case['var'], type(None)):
            actual_array = actual_dataset.values
        else:
            actual_array = actual_dataset[test_case['var']].values
        assert np.array_equal(actual_array, test_case['expected_array'], equal_nan=True), f"`mask_where_all_zero` created a dataset with the array: {actual_array}.\nExpected array: {test_case['expected_array']}"
    
    # Create a dataset with negative values
    invalid_ex_xr = xr.Dataset({
        'test_var': (
            ['t', 'i', 'j'], 
          [[[ -1,  -1,  -1],
            [ 1,  1,  1],
            [ 0,  0,  0]],
           [[ 0,  1,  1],
            [ 1,  0,  0],
            [ 0,  0,  0]]]
        )
    })
    # Define invalid test cases
    invalid_test_cases = [
        {   # Passing a file that does not exist
            'dataset': 'invalid_dataset.nc',
        },
        {   # Passing a string that isn't a file path
            'dataset': 'invalid_dataset',
        },
        {   # Passing a list of files that don't have the same dimensions
            'dataset': invalid_ex_xr,
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = analysis.mask_where_all_zero(
                dataset = invalid_test_case['dataset'],
                var = 'test_var',
                time_dim = 't',
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`mask_where_all_zero` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`mask_where_all_zero` did not raise an exception on invalid test case {invalid_test_case}"
    
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
            actual = analysis.mask_where_all_zero(
                dataset = invalid_string,
                var = test_cases[0]['var'],
                time_dim = test_cases[0]['time_dim'],
            )
        except (TypeError, ValueError) as e:
            assert True, f"`mask_where_all_zero` raised an exception on invalid `dataset`: {e}"
        else:
            assert False, f"`mask_where_all_zero` did not raise an exception on invalid `dataset` {invalid_string}"
        # Test with `var`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = analysis.mask_where_all_zero(
                    dataset = test_cases[0]['dataset'],
                    var = invalid_string,
                    time_dim = test_cases[0]['time_dim'],
                )
            except (TypeError) as e:
                assert True, f"`mask_where_all_zero` raised an exception on invalid `var`: {e}"
            else:
                assert False, f"`mask_where_all_zero` did not raise an exception on invalid `var` {invalid_string}"
        # Test with `time_dim`
        try:
            actual = analysis.mask_where_all_zero(
                dataset = test_cases[0]['dataset'],
                var = test_cases[0]['var'],
                time_dim = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`mask_where_all_zero` raised an exception on invalid `time_dim`: {e}"
        else:
            assert False, f"`mask_where_all_zero` did not raise an exception on invalid `time_dim` {invalid_string}"
        # Test with `verbose`
        try:
            actual = analysis.mask_where_all_zero(
                dataset = test_cases[0]['dataset'],
                var = test_cases[0]['var'],
                time_dim = test_cases[0]['time_dim'],
                verbose = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`mask_where_all_zero` raised an exception on invalid `verbose`: {e}"
        else:
            assert False, f"`mask_where_all_zero` did not raise an exception on invalid `verbose` {invalid_string}"
