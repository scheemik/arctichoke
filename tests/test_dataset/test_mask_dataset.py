import numpy as np 
import xarray as xr

from arctichoke import dataset
from arctichoke.dataset import make_example_dataset
from arctichoke.path import remove_non_empty_directory, make_file_path
from arctichoke.verify import verify_path

def test_make_mask():
    """Test the `make_mask` function."""
    # Create multiple example test files
    test_file_dir = 'tests/test_dataset/example_datasets'
    make_file_path(test_file_dir)
    test_file_names = [
        f"{test_file_dir}/example_dataset_0.nc",
        f"{test_file_dir}/example_dataset_1.nc",
        f"{test_file_dir}/example_dataset_2.nc",
    ]
    for i in range(len(test_file_names)):
        test_file = test_file_names[i]
        make_example_dataset(
            n=2,
            test_var_name='test_var',
            time_dim='time',
            time_len=1,
            offset=i,
            save_as=test_file,
        )
    # Define test cases
    test_cases = [
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='test_var',
            ),
            'var': 'test_var',
            'mask_var_name': None,
            'mask_this_val': 3,
            'mask_this_range': None,
            'val_inside_range': np.nan,
            'val_outside_range': 1,
            'save_as': None,
            'expected_mask': np.array(
               [[     1.,     1.,     1.],
                [ np.nan,     1.,     1.],
                [     1.,     1.,     1.]]),
        },
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='test_var',
            ),
            'var': 'test_var',
            'mask_var_name': None,
            'mask_this_val': 4,
            'mask_this_range': None,
            'val_inside_range': 0,
            'val_outside_range': 2,
            'save_as': f"{test_file_dir}/example_mask_0.nc",
            'expected_mask': np.array(
               [[     2.,     2.,     2.],
                [     2.,     0.,     2.],
                [     2.,     2.,     2.]]),
        },
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='test_var',
            ),
            'var': 'test_var',
            'mask_var_name': 'new_var',
            'mask_this_val': 4,
            'mask_this_range': None,
            'val_inside_range': 0,
            'val_outside_range': 2,
            'save_as': f"{test_file_dir}/example_mask_1.nc",
            'expected_mask': np.array(
               [[     2.,     2.,     2.],
                [     2.,     0.,     2.],
                [     2.,     2.,     2.]]),
        },
        {
            'dataset': make_example_dataset(
                n=3, 
                test_var_name='test_var',
            ),
            'var': 'test_var',
            'mask_var_name': 'new_var',
            'mask_this_val': None,
            'mask_this_range': [4,7],
            'val_inside_range': 0,
            'val_outside_range': 1,
            'save_as': None,
            'expected_mask': np.array(
               [[     1.,     1.,     1.],
                [     1.,     0.,     0.],
                [     0.,     0.,     1.]]),
        },
        {
            'dataset': test_file_names,
            'var': 'test_var',
            'mask_var_name': None,
            'mask_this_val': 3,
            'mask_this_range': None,
            'val_inside_range': 0,
            'val_outside_range': 1,
            'save_as': None,
            'expected_mask': np.array(
              [[[     1.,     1.],
                [     1.,     0.]],
               [[     1.,     1.],
                [     0.,     1.]],
               [[     1.,     0.],
                [     1.,     1.]]]),
        },
        {
            'dataset': make_example_dataset(
                n=2, 
                test_var_name='test_var',
                time_dim='time',
                time_len=2,
            ),
            'var': 'test_var',
            'mask_var_name': 'new_var',
            'mask_this_val': 2,
            'mask_this_range': None,
            'val_inside_range': 0,
            'val_outside_range': 1,
            'save_as': None,
            'expected_mask': np.array(
              [[[     1.,     1.],
                [     0.,     1.]],
               [[     1.,     1.],
                [     0.,     1.]]]),
        },
    ]
    for test_case in test_cases:
        actual_dataset = dataset.make_mask(
            dataset = test_case['dataset'],
            var = test_case['var'],
            mask_var_name = test_case['mask_var_name'],
            mask_this_val = test_case['mask_this_val'],
            mask_this_range = test_case['mask_this_range'],
            val_inside_range = test_case['val_inside_range'],
            val_outside_range = test_case['val_outside_range'],
            save_as = test_case['save_as'],
        )
        # Get the name of the mask variable
        if isinstance(test_case['mask_var_name'], type(None)):
            this_mask_var_name = f'{test_case['var']}_mask'
        else:
            this_mask_var_name = test_case['mask_var_name']
        actual_mask = np.array(actual_dataset[this_mask_var_name].values)
        assert np.array_equal(actual_mask, test_case['expected_mask'], f"`make_mask` failed on test case: {test_case}.\nExpected mask: {test_case['expected_mask']}\nActual mask: {actual_mask}")
        if not isinstance(test_case['save_as'], type(None)):
            try:
                actual_save_as = verify_path(test_case['save_as'])
            except (FileNotFoundError) as e:
                assert True, f"`make_mask` raised an exception: {e}\nExpected save file at {test_case['save_as']}"
    # Clean up test files that were created
    remove_non_empty_directory(test_file_dir)

    # Define invalid test cases
    invalid_test_cases = [
        {
            'dataset': 'invalid_dataset',
            'var': 'test_var',
            'mask_var_name': None,
            'mask_this_val': 2,
            'mask_this_range': None,
        },
        {
            'dataset': test_cases[0]['dataset'],
            'var': 'invalid_var',
            'mask_var_name': None,
            'mask_this_val': 2,
            'mask_this_range': None,
        },
        {
            'dataset': test_cases[0]['dataset'],
            'var': 'test_var',
            'mask_var_name': None,
            'mask_this_val': None,
            'mask_this_range': None,
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = dataset.make_mask(
                dataset = invalid_test_case['dataset'],
                var = invalid_test_case['var'],
                mask_var_name = invalid_test_case['mask_var_name'],
                mask_this_val = invalid_test_case['mask_this_val'],
                mask_this_range = invalid_test_case['mask_this_range'],
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`make_mask` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`make_mask` did not raise an exception on invalid test case {invalid_test_case}"
    
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
            actual = dataset.make_mask(
                dataset = invalid_string,
                var = test_cases[0]['var'],
                mask_this_val = test_cases[0]['mask_this_val'],
                mask_this_range = test_cases[0]['mask_this_range'],
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_mask` raised an exception on invalid `dataset`: {e}"
        else:
            assert False, f"`make_mask` did not raise an exception on invalid `dataset` {invalid_string}"
        # Test with `mask_var_name`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = dataset.make_mask(
                    dataset = test_cases[0]['dataset'],
                    var = test_cases[0]['var'],
                    mask_var_name = invalid_string,
                    mask_this_val = test_cases[0]['mask_this_val'],
                    mask_this_range = test_cases[0]['mask_this_range'],
                )
            except (TypeError, ValueError) as e:
                assert True, f"`make_mask` raised an exception on invalid `mask_var_name`: {e}"
            else:
                assert False, f"`make_mask` did not raise an exception on invalid `mask_var_name` {invalid_string}"
            # Test with `mask_this_range`
            try:
                actual = dataset.make_mask(
                    dataset = test_cases[0]['dataset'],
                    var = test_cases[0]['var'],
                    mask_this_val = test_cases[0]['mask_this_val'],
                    mask_this_range = invalid_string,
                )
            except (TypeError, ValueError) as e:
                assert True, f"`make_mask` raised an exception on invalid `mask_this_range`: {e}"
            else:
                assert False, f"`make_mask` did not raise an exception on invalid `mask_this_range` {invalid_string}"
            # Test with `save_as`
            try:
                actual = dataset.make_mask(
                    dataset = test_cases[0]['dataset'],
                    var = test_cases[0]['var'],
                    mask_this_val = test_cases[0]['mask_this_val'],
                    mask_this_range = test_cases[0]['mask_this_range'],
                    save_as = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`make_mask` raised an exception on invalid `save_as`: {e}"
            else:
                assert False, f"`make_mask` did not raise an exception on invalid `save_as` {invalid_string}"
        # Test with `add_mask_attrs`
        try:
            actual = dataset.make_mask(
                dataset = test_cases[0]['dataset'],
                var = test_cases[0]['var'],
                mask_this_val = test_cases[0]['mask_this_val'],
                mask_this_range = test_cases[0]['mask_this_range'],
                add_mask_attrs = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_mask` raised an exception on invalid `add_mask_attrs`: {e}"
        else:
            assert False, f"`make_mask` did not raise an exception on invalid `add_mask_attrs` {invalid_string}"
        # Test with `verbose`
        try:
            actual = dataset.make_mask(
                dataset = test_cases[0]['dataset'],
                var = test_cases[0]['var'],
                mask_this_val = test_cases[0]['mask_this_val'],
                mask_this_range = test_cases[0]['mask_this_range'],
                verbose = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_mask` raised an exception on invalid `verbose`: {e}"
        else:
            assert False, f"`make_mask` did not raise an exception on invalid `verbose` {invalid_string}"
    # Define a list of invalid numbers
    invalid_numbers = [
        '1234',
        '3.14',
        None,
        [],
        {}
    ]
    for invalid_number in invalid_numbers:
        # Test with `mask_this_val`
        try:
            actual = dataset.make_mask(
                dataset = test_cases[0]['dataset'],
                var = test_cases[0]['var'],
                mask_this_val = invalid_number,
                mask_this_range = None,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_mask` raised an exception on invalid `mask_this_val`: {e}"
        else:
            assert False, f"`make_mask` did not raise an exception on invalid `mask_this_val` {invalid_number}"
        # Test with `mask_this_range`
        try:
            actual = dataset.make_mask(
                dataset = test_cases[0]['dataset'],
                var = test_cases[0]['var'],
                mask_this_val = None,
                mask_this_range = invalid_number,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_mask` raised an exception on invalid `mask_this_range`: {e}"
        else:
            assert False, f"`make_mask` did not raise an exception on invalid `mask_this_range` {invalid_number}"
        try:
            actual = dataset.make_mask(
                dataset = test_cases[0]['dataset'],
                var = test_cases[0]['var'],
                mask_this_val = None,
                mask_this_range = [invalid_number],
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_mask` raised an exception on invalid `mask_this_range`: {e}"
        else:
            assert False, f"`make_mask` did not raise an exception on invalid `mask_this_range` {invalid_number}"
        try:
            actual = dataset.make_mask(
                dataset = test_cases[0]['dataset'],
                var = test_cases[0]['var'],
                mask_this_val = None,
                mask_this_range = [0, invalid_number],
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_mask` raised an exception on invalid `mask_this_range`: {e}"
        else:
            assert False, f"`make_mask` did not raise an exception on invalid `mask_this_range` {invalid_number}"
        # Test with `val_inside_range`
        try:
            actual = dataset.make_mask(
                dataset = test_cases[0]['dataset'],
                var = test_cases[0]['var'],
                mask_this_val = test_cases[0]['mask_this_val'],
                val_inside_range = invalid_number,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_mask` raised an exception on invalid `val_inside_range`: {e}"
        else:
            assert False, f"`make_mask` did not raise an exception on invalid `val_inside_range` {invalid_number}"
        # Test with `val_outside_range`
        try:
            actual = dataset.make_mask(
                dataset = test_cases[0]['dataset'],
                var = test_cases[0]['var'],
                mask_this_val = test_cases[0]['mask_this_val'],
                val_outside_range = invalid_number,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_mask` raised an exception on invalid `val_outside_range`: {e}"
        else:
            assert False, f"`make_mask` did not raise an exception on invalid `val_outside_range` {invalid_number}"
