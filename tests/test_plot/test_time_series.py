from seaicecp.plot import time_series
from seaicecp.dataset import example_dataset

def test_plot_time_series():
    """Test the `plot_time_series` function."""
    ## Note: None of the tests below actually make any plots. They solely test the input arguments.
    test_xr = example_dataset.make_example_dataset()
    # Define test cases
    test_cases = [
        {
            'plt_title': None,
            'xlims': None,
            'ylims': None,
            'save_as': None,
            'name': 'test_var',
        },
        {
            'plt_title': 'Test Title',
            'xlims': None,
            'ylims': None,
            'save_as': None,
            'name': 'test_var',
        },
        {
            'plt_title': None,
            'xlims': ['2014-01-01', '2014-09-01'],
            'ylims': None,
            'save_as': None,
            'name': 'test_var',
        },
        {
            'plt_title': None,
            'xlims': None,
            'ylims': [0, 1],
            'save_as': None,
            'name': 'test_var',
        },
        {
            'plt_title': None,
            'xlims': None,
            'ylims': None,
            'save_as': 'test_filepath.png',
            'name': 'test_var',
        },
    ]
    for test_case in test_cases:
        actual = time_series.plot_time_series(
            dataset = test_xr,
            variable_id = 'test_var',
            plt_title = test_case['plt_title'],
            xlims = test_case['xlims'],
            ylims = test_case['ylims'],
            save_as = test_case['save_as'],
            test = True,
        )
        # Check the data variables
        assert actual.name == test_case['name'], f"`plot_time_series` failed on test case: {test_case} \nExpected: {test_case['name']} \nActual: {actual.name}"

    # Define invalid test cases
    invalid_test_cases = [
        {
            'dataset': None,
            'variable_id': 'test_var',
            'xlims': None,
            'ylims': None,
        },
        {
            'dataset': 'not_a_valid_dataset.nc',
            'variable_id': 'test_var',
            'xlims': None,
            'ylims': None,
        },
        {
            'dataset': test_xr,
            'variable_id': 'invalid_var',
            'xlims': None,
            'ylims': None,
        },
        {
            'dataset': test_xr,
            'variable_id': 'test_var',
            'xlims': ['not a date', '2014-09-01'],
            'ylims': None,
        },
        {
            'dataset': test_xr,
            'variable_id': 'test_var',
            'xlims': ['2014-01-99', '2014-09-01'],
            'ylims': None,
        },
        {
            'dataset': test_xr,
            'variable_id': 'test_var',
            'xlims': ['2014-01-01', 20140901],
            'ylims': None,
        },
        {
            'dataset': test_xr,
            'variable_id': 'test_var',
            'xlims': None,
            'ylims': ['foo', 1],
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = time_series.plot_time_series(
                dataset = invalid_test_case['dataset'],
                variable_id = invalid_test_case['variable_id'],
                xlims = invalid_test_case['xlims'],
                ylims = invalid_test_case['ylims'],
                test = True,
            )
        except (TypeError, ValueError, FileNotFoundError, KeyError) as e:
            assert True, f"`plot_time_series` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`plot_time_series` did not raise an exception on invalid test case {invalid_test_case}"
    
    # Define a list of invalid datasets
    invalid_strings = [
        1234,
        3.14,
        [],
        {}
    ]
    for invalid_string in invalid_strings:
        # Test with `dataset`
        try:
            actual = time_series.plot_time_series(
                dataset = invalid_string,
                variable_id = 'test_var',
            )
        except (TypeError) as e:
            assert True, f"`plot_time_series` raised an exception on invalid `dataset`: {e}"
        else:
            assert False, f"`plot_time_series` did not raise an exception on invalid `dataset` {invalid_string}"
        # Test with `variable_id`
        try:
            actual = time_series.plot_time_series(
                dataset = test_xr,
                variable_id = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`plot_time_series` raised an exception on invalid `variable_id`: {e}"
        else:
            assert False, f"`plot_time_series` did not raise an exception on invalid `variable_id` {invalid_string}"
        # Test with `plt_title`
        try:
            actual = time_series.plot_time_series(
                dataset = test_xr,
                variable_id = 'test_var',
                plt_title = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`plot_time_series` raised an exception on invalid `plt_title`: {e}"
        else:
            assert False, f"`plot_time_series` did not raise an exception on invalid `plt_title` {invalid_string}"
        # Test with `xlims`
        try:
            actual = time_series.plot_time_series(
                dataset = test_xr,
                variable_id = 'test_var',
                xlims = [invalid_string, '2014-01-01'],
            )
        except (TypeError) as e:
            assert True, f"`plot_time_series` raised an exception on invalid `xlims`: {e}"
        else:
            assert False, f"`plot_time_series` did not raise an exception on invalid `xlims` {invalid_string}"
        # Test with `save_as`
        try:
            actual = time_series.plot_time_series(
                dataset = test_xr,
                variable_id = 'test_var',
                save_as = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`plot_time_series` raised an exception on invalid `save_as`: {e}"
        else:
            assert False, f"`plot_time_series` did not raise an exception on invalid `save_as` {invalid_string}"