import numpy as np 
import xarray as xr

from arctichoke import analysis
from arctichoke.dataset.example_dataset import make_example_dataset

# Create test case with many different trends
n = 3
offset = 0
test_var_name = 'si_var'
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

def test_find_standard_error():
    """Test the `find_standard_error` function."""
    # Create a test example dataset
    test_xr = make_example_dataset(
        n = 1,
        test_var_name = 'score',
        time_dim = 'year',
        time_len = 12,
        start_year = 0,
    )
    test_xr['score'] = test_xr['score'].isel(year=0)
    test_xr = test_xr.drop_dims('year')
    test_xr = test_xr.expand_dims(
        dim={'hours': [0.5, 0.5, 1, 1, 1, 1.5, 2, 2.5, 2.5, 3, 3, 4]}, 
        axis=0)
    test_xr['score'].values = [[[76]], [[78]], [[74]], [[80]], [[84]], [[79]], [[86]], [[90]], [[92]], [[84]], [[83]], [[97]]]
    test_xr_polyfit = test_xr['score'].polyfit('hours', 1, skipna=True, full=True)
    # Get an example with many different trends
    test_many_trends_polyfit = test_many_trends[test_var_name].polyfit('year', 1, skipna=True, full=True)
    # Create test case with `nan` values
    test_many_trends[test_var_name] = test_many_trends[test_var_name].where(
        lambda val:
            (test_many_trends[test_var_name] != 0),
        lambda val: np.nan
    )
    test_nan_polyfit = test_many_trends[test_var_name].polyfit('year', 1, skipna=True, full=True)
    # Define test cases
    test_cases = [
        {
            'polyfit_residuals': 1000,
            'n_dof': 12,
            'expected_stderr': 10.0,
            'expected_dtype': np.float64,
        },
        {
            'polyfit_residuals': 175.58222222,
            'n_dof': 12,
            'expected_stderr': 4.190253240795835,
            'expected_dtype': np.float64,
        },
        {
            'polyfit_residuals': test_xr_polyfit['polyfit_residuals'],
            'n_dof': test_xr['score'].sizes['hours'],
            'expected_stderr': [4.190253240822351],
            'expected_dtype': xr.DataArray,
            'atol': 1e-10,
        },
        {
            'polyfit_residuals': test_many_trends_polyfit['polyfit_residuals'],
            'n_dof': test_many_trends[test_var_name].sizes['year'],
            'expected_stderr': [0, 0.816496581, 1.22474487, 0.408248290],
            'expected_dtype': xr.DataArray,
            'atol': 1e-6,
        },
        {
            'polyfit_residuals': test_nan_polyfit['polyfit_residuals'],
            'n_dof': test_many_trends[test_var_name].sizes['year'],
            'expected_stderr': [0, 0.816496581, np.nan, 0.408248290],
            'expected_dtype': xr.DataArray,
            'atol': 1e-6,
        },
    ]
    for test_case in test_cases:
        actual_stderrs = analysis.find_standard_error(
            polyfit_residuals = test_case['polyfit_residuals'],
            n_dof = test_case['n_dof'],
        )
        actual_dtype = type(actual_stderrs)
        assert actual_dtype == test_case['expected_dtype'], f"`find_standard_error` failed on test case: {test_case}.\nExpected: {test_case['expected_dtype']}\nActual: {actual_dtype}"
        if actual_dtype == np.float64:
            assert actual_stderrs == test_case['expected_stderr'], f"`find_standard_error` failed on test case: {test_case}.\nExpected: {test_case['expected_stderr']}\nActual: {actual_stderrs}"
        else:
            for actual_stderr in actual_stderrs.values.flatten():
                isclose = False
                for expected_stderr in test_case['expected_stderr']:
                    if np.isclose(actual_stderr, expected_stderr, atol=test_case['atol'], equal_nan=True):
                        isclose = True
                if isclose == False:
                    assert False, f"`trend_in_time` created a dataset with the unique stderrs: {actual_stderr}.\nExpected unique stderrs: {test_case['expected_stderrs']}\nFailed on trend: {actual_stderr}"

    # Define a list of invalid inputs
    invalid_strings = [
        1234,
        3.14,
        None,
        [],
        {}
    ]
    for invalid_string in invalid_strings:
        if not isinstance(invalid_string, (int, float)):
            # Test with `polyfit_residuals`
            try:
                actual = analysis.find_standard_error(
                    polyfit_residuals = invalid_string,
                    n_dof = 10,
                )
            except (TypeError, ValueError) as e:
                assert True, f"`find_standard_error` raised an exception on invalid `polyfit_residuals`: {e}"
            else:
                assert False, f"`find_standard_error` did not raise an exception on invalid `polyfit_residuals` {invalid_string}"
            # Test with `n_dof`
            try:
                actual = analysis.find_standard_error(
                    dataset = test_cases[0]['polyfit_residuals'],
                    n_dof = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`find_standard_error` raised an exception on invalid `n_dof`: {e}"
            else:
                assert False, f"`find_standard_error` did not raise an exception on invalid `n_dof` {invalid_string}"
        # Test with `verbose`
        try:
            actual = analysis.find_standard_error(
                dataset = test_cases[0]['polyfit_residuals'],
                n_dof = 10,
                verbose = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`find_standard_error` raised an exception on invalid `verbose`: {e}"
        else:
            assert False, f"`find_standard_error` did not raise an exception on invalid `verbose` {invalid_string}"
