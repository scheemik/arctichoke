import numpy as np 
import xarray as xr

from arctichoke.analysis.significance import find_significance
from arctichoke.analysis import trend_in_time
from arctichoke.dataset.example_dataset import make_example_dataset
from arctichoke.path.manipulate_paths import remove_non_empty_directory, make_file_path
from arctichoke.verify import verify_path

# Create test case with multiple, different trends
test_var = 'score'
test_time_dim = 'year'

small_xr = make_example_dataset(
    n = 2,
    test_var_name = test_var,
    time_dim = test_time_dim,
    time_len = 12,
    start_year = 0,
)
small_xr[test_var] = small_xr[test_var].isel(year=0)
small_xr = small_xr.drop_dims(test_time_dim)
small_xr = small_xr.expand_dims(
    dim={test_time_dim: [0.5, 0.5, 1, 1, 1, 1.5, 2, 2.5, 2.5, 3, 3, 4]}, 
    axis=0)
small_xr[test_var].values = [
    [[76, 100], [100, 100]], 
    [[78,  78], [100, 100]], 
    [[74,  74], [ 74, 100]], 
    [[80,  80], [ 80,  80]], 
    [[84,  84], [ 84,  84]], 
    [[79,  79], [ 79,  79]], 
    [[86,  86], [ 86,  86]], 
    [[90,  90], [ 90,  90]], 
    [[92,  92], [ 92,  92]], 
    [[84,  84], [ 84,  84]], 
    [[83,  83], [ 83,  83]], 
    [[97,  97], [ 97,  97]]
]
# I know that, with the data above, the trends for the first two columns are significant and the other two are not significant

def test_find_significance():
    """Test the `find_significance` function."""
    # Define test cases
    test_cases = [
        {
            'dataset': small_xr,
            'var': test_var,
            'time_dim': test_time_dim,
            'expected_trends': [
                [ 4.89777778,  2.55111111],
                [ 0.4       , -1.21777778],
            ],
            'expected_intercepts': [
                [74.4       , 80.8       ],
                [86.66666667, 91.86666667],
            ],
            'expected_residuals': [
                [175.58222222, 585.39555556],
                [784.66666667, 688.06222222],
                # [784.66666667, 688.],
            ],
            'expected_significance_test': [
                [276.29756049,  21.18550123],
                [-76.50666667, -50.63968395],
            ],
            'expected_trends_sig': [
                [1., 1.],
                [0., 0.],
            ],
        },
    ]
    for test_case in test_cases:
        # Get the trends
        trends_dataset = trend_in_time(
            dataset = test_case['dataset'],
            var = test_case['var'],
            time_dim = test_case['time_dim'],
        )
        # Check that the trends dataset matches expectations
        for expected_var in ['trends', 'intercepts', 'residuals']:
            actual_vals = trends_dataset[f'{test_case['var']}_{expected_var}'].values
            expected_vals = test_case[f'expected_{expected_var}']
            assert np.allclose(actual_vals, expected_vals), f"`trends_dataset` created a dataset with the {expected_var}: {actual_vals}.\nExpected {expected_var}: {expected_vals}"
        # Get the significance of the trends
        actual_trends_sig = find_significance(
            dataset = test_case['dataset'],
            trend_dataset = trends_dataset,
            var = test_case['var'],
            time_dim = test_case['time_dim'],
        )
        # Check that the trends significance dataset matches expectations
        for expected_var in ['significance_test', 'trends_sig']:
            actual_vals = actual_trends_sig[f'{test_case['var']}_{expected_var}'].values
            expected_vals = test_case[f'expected_{expected_var}']
            assert np.allclose(actual_vals, expected_vals), f"`trends_dataset` created a dataset with the {expected_var}: {actual_vals}.\nExpected {expected_var}: {expected_vals}"

    # Define a list of invalid inputs
    invalid_datasets = [
        'invalid_dataset',
        'invalid_dataset.nc',
        1234,
        3.14,
        None,
        [],
        {},
        test_cases[0]['dataset'][test_cases[0]['var']],
        actual_trends_sig[f'{test_cases[-1]['var']}_trends_sig'],
    ]
    # Get the trends
    valid_trends_dataset = trend_in_time(
        dataset = test_cases[0]['dataset'],
        var = test_cases[0]['var'],
        time_dim = test_cases[0]['time_dim'],
    )
    for invalid_dataset in invalid_datasets:
        # Test with `dataset`
        if not isinstance(invalid_dataset, xr.DataArray):
            try:
                actual = find_significance(
                    dataset = invalid_dataset,
                    trend_dataset = valid_trends_dataset,
                    var = test_cases[0]['var'],
                    time_dim = test_cases[0]['time_dim'],
                )
            except (TypeError, ValueError) as e:
                assert True, f"`find_significance` raised an exception on invalid `dataset`: {e}"
            else:
                assert False, f"`find_significance` did not raise an exception on invalid `dataset` {invalid_dataset}"
        # Test with `trend_dataset`
        try:
            actual = find_significance(
                dataset = test_cases[0]['dataset'],
                trend_dataset = invalid_dataset,
                var = test_cases[0]['var'],
                time_dim = test_cases[0]['time_dim'],
            )
        except (TypeError, ValueError) as e:
            assert True, f"`find_significance` raised an exception on invalid `trend_dataset`: {e}"
        else:
            assert False, f"`find_significance` did not raise an exception on invalid `trend_dataset` {invalid_dataset}"
    
    # Define a list of invalid inputs
    invalid_strings = [
        1234,
        3.14,
        None,
        [],
        {},
    ]
    for invalid_string in invalid_strings:
        # Test with `var`
        try:
            actual = find_significance(
                dataset = test_cases[0]['dataset'],
                trend_dataset = valid_trends_dataset,
                var = invalid_string,
                time_dim = test_cases[0]['time_dim'],
            )
        except (TypeError) as e:
            assert True, f"`find_significance` raised an exception on invalid `var`: {e}"
        else:
            assert False, f"`find_significance` did not raise an exception on invalid `var` {invalid_string}"
        # Test with `time_dim`
        try:
            actual = find_significance(
                dataset = test_cases[0]['dataset'],
                trend_dataset = valid_trends_dataset,
                var = test_cases[0]['var'],
                time_dim = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`find_significance` raised an exception on invalid `time_dim`: {e}"
        else:
            assert False, f"`find_significance` did not raise an exception on invalid `time_dim` {invalid_string}"
        # Test with `verbose`
        try:
            actual = find_significance(
                dataset = test_cases[0]['dataset'],
                trend_dataset = valid_trends_dataset,
                var = test_cases[0]['var'],
                time_dim = test_cases[0]['time_dim'],
                verbose = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`find_significance` raised an exception on invalid `verbose`: {e}"
        else:
            assert False, f"`find_significance` did not raise an exception on invalid `verbose` {invalid_string}"
