import numpy as np 
import xarray as xr

from arctichoke import analysis
from arctichoke.dataset.example_dataset import make_example_dataset
from arctichoke.path.manipulate_paths import remove_non_empty_directory, make_file_path
from arctichoke.verify import verify_path

def test_make_climatology():
    """Test the `make_climatology` function."""
    # Define test cases
    test_cases = [
        {
            'this_source_id': 'EC-Earth3P-HR',
            'this_var': 'sithick',
            'this_variant_label': 'r1i1p2f1',
            'this_modification': 'trim_CAA_',
            'find_mean': True,
            'save_as': None,
        },
        {
            'this_source_id': 'EC-Earth3P-HR',
            'this_var': 'sithick',
            'this_variant_label': 'r1i1p2f1',
            'this_modification': 'trim_CAA_',
            'find_mean': False,
            'save_as': None,
        },
    ]
    for test_case in test_cases:
        actual_dataset = analysis.make_climatology(
            this_source_id = test_case['this_source_id'],
            this_var = test_case['this_var'],
            this_variant_label = test_case['this_variant_label'],
            this_modification = test_case['this_modification'],
            find_mean = test_case['find_mean'],
        )
        # Check whether `month` is in the list of coordinates
        coords_list = list(actual_dataset.coords.keys())
        assert 'month' in coords_list, f"`make_climatology` failed on test case: {test_case}.\nExpected `month` to be in list of coordinates: {coords_list}"
        # Check whether the expected variable name is in the list of data variables
        if test_case['find_mean']:
            expected_var = f'{test_case['this_var']}_month_mean'
        else:
            expected_var = f'{test_case['this_var']}_month_sum'
        dvars_list = list(actual_dataset.data_vars)
        assert expected_var in dvars_list, f"`make_climatology` failed on test case: {test_case}.\nExpected `{expected_var}` to be in list of data variables: {dvars_list}"
        if not isinstance(test_case['save_as'], type(None)):
            try:
                actual_save_as = verify_path(test_case['save_as'])
            except (FileNotFoundError) as e:
                assert True, f"`make_climatology` raised an exception: {e}\nExpected save file at {test_case['save_as']}"

    # Define invalid test cases
    invalid_test_cases = [
        {
            'this_source_id': test_cases[0]['this_source_id'],
            'this_var': test_cases[0]['this_var'],
            'this_variant_label': test_cases[0]['this_variant_label'],
            'this_modification': test_cases[0]['this_modification'],
            'find_mean': test_cases[0]['find_mean'],
            'start_year': 1969,
            'end_year': 1950,
        },
        {
            'this_source_id': test_cases[0]['this_source_id'],
            'this_var': test_cases[0]['this_var'],
            'this_variant_label': test_cases[0]['this_variant_label'],
            'this_modification': test_cases[0]['this_modification'],
            'find_mean': test_cases[0]['find_mean'],
            'start_year': 1950,
            'end_year': 1950,
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = analysis.make_climatology(
                this_source_id = invalid_test_case['this_source_id'],
                this_var = invalid_test_case['this_var'],
                this_variant_label = invalid_test_case['this_variant_label'],
                this_modification = invalid_test_case['this_modification'],
                find_mean = invalid_test_case['find_mean'],
                start_year = invalid_test_case['start_year'],
                end_year = invalid_test_case['end_year'],
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`make_climatology` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`make_climatology` did not raise an exception on invalid test case {invalid_test_case}"
    
    # Define a list of invalid inputs
    invalid_strings = [
        1234,
        3.14,
        None,
        [],
        {}
    ]
    for invalid_string in invalid_strings:
        # Test with `this_source_id`
        try:
            actual = analysis.make_climatology(
                this_source_id = invalid_string,
                this_var = test_case['this_var'],
                this_variant_label = test_case['this_variant_label'],
                this_modification = test_case['this_modification'],
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_climatology` raised an exception on invalid `this_source_id`: {e}"
        else:
            assert False, f"`make_climatology` did not raise an exception on invalid `this_source_id` {invalid_string}"
        # Test with `this_var`
        try:
            actual = analysis.make_climatology(
                this_source_id = test_case['this_source_id'],
                this_var = invalid_string,
                this_variant_label = test_case['this_variant_label'],
                this_modification = test_case['this_modification'],
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_climatology` raised an exception on invalid `this_var`: {e}"
        else:
            assert False, f"`make_climatology` did not raise an exception on invalid `this_var` {invalid_string}"
        if not isinstance(invalid_string, type(None)):
            # Test with `this_variant_label`
            try:
                actual = analysis.make_climatology(
                    this_source_id = test_case['this_source_id'],
                    this_var = test_case['this_var'],
                    this_variant_label = invalid_string,
                    this_modification = test_case['this_modification'],
                )
            except (TypeError, ValueError) as e:
                assert True, f"`make_climatology` raised an exception on invalid `this_variant_label`: {e}"
            else:
                assert False, f"`make_climatology` did not raise an exception on invalid `this_variant_label` {invalid_string}"
            # Test with `this_modification`
            try:
                actual = analysis.make_climatology(
                    this_source_id = test_case['this_source_id'],
                    this_var = test_case['this_var'],
                    this_variant_label = test_case['this_variant_label'],
                    this_modification = invalid_string,
                )
            except (TypeError, ValueError) as e:
                assert True, f"`make_climatology` raised an exception on invalid `this_modification`: {e}"
            else:
                assert False, f"`make_climatology` did not raise an exception on invalid `this_modification` {invalid_string}"
        # Test with `find_mean`
        try:
            actual = analysis.make_climatology(
                this_source_id = test_case['this_source_id'],
                this_var = test_case['this_var'],
                this_variant_label = test_case['this_variant_label'],
                this_modification = test_case['this_modification'],
                find_mean = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_climatology` raised an exception on invalid `find_mean`: {e}"
        else:
            assert False, f"`make_climatology` did not raise an exception on invalid `find_mean` {invalid_string}"
        # Test with `select_summer`
        try:
            actual = analysis.make_climatology(
                this_source_id = test_case['this_source_id'],
                this_var = test_case['this_var'],
                this_variant_label = test_case['this_variant_label'],
                this_modification = test_case['this_modification'],
                select_summer = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_climatology` raised an exception on invalid `select_summer`: {e}"
        else:
            assert False, f"`make_climatology` did not raise an exception on invalid `select_summer` {invalid_string}"
    #     # Test with `save_as`
    #     if not isinstance(invalid_string, type(None)):
    #         try:
    #             actual = analysis.make_climatology(
    #                 this_source_id = test_case['this_source_id'],
    #                 this_var = test_case['this_var'],
    #                 this_variant_label = test_case['this_variant_label'],
    #                 this_modification = test_case['this_modification'],
    #                 save_as = invaild_string,
    #             )
    #         except (TypeError) as e:
    #             assert True, f"`make_climatology` raised an exception on invalid `save_as`: {e}"
    #         else:
    #             assert False, f"`make_climatology` did not raise an exception on invalid `save_as` {invalid_string}"
    # Define a list of invalid years
    invalid_years = [
        '1234',
        '3.14',
        None,
        1940,
        4000,
        [],
        {}
    ]
    for invaild_year in invalid_years:
        # Test with `start_year`
        try:
            actual = analysis.make_climatology(
                this_source_id = test_case['this_source_id'],
                this_var = test_case['this_var'],
                this_variant_label = test_case['this_variant_label'],
                this_modification = test_case['this_modification'],
                start_year = invaild_year,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_climatology` raised an exception on invalid `start_year`: {e}"
        else:
            assert False, f"`make_climatology` did not raise an exception on invalid `start_year` {invaild_year}"
        # Test with `end_year`
        try:
            actual = analysis.make_climatology(
                this_source_id = test_case['this_source_id'],
                this_var = test_case['this_var'],
                this_variant_label = test_case['this_variant_label'],
                this_modification = test_case['this_modification'],
                end_year = invaild_year,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_climatology` raised an exception on invalid `end_year`: {e}"
        else:
            assert False, f"`make_climatology` did not raise an exception on invalid `end_year` {invaild_year}"
